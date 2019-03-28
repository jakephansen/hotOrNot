# PART 1: Web Scraper
# Jacob Hansen (jbknill), Joshua Knill (jphans), Tyler Laredo (tlaredo), Gautam Visveswaran (gautamv)

from requests import get
from bs4 import *
import errno, json, os, pickle, re, shutil, string, sys, unicodedata
from threading import Thread
from util import *
from preprocessor import *

# GLOBALS

# Array containing all scores for all reviews. Used for determining average score
all_scores = list()
# Array of prof_ids; used for k-folding
professor_ids = list()
# Dictionary containing all professors scraped (maps prof_id to prof info)
professors = dict()
# Global list of words
all_words = list()
# Base url
rmp_url = "http://www.ratemyprofessors.com"
# urls for small dataset
small_set_school_urls = ["https://www.ratemyprofessors.com/search.jsp?query=webb+institute", "https://www.ratemyprofessors.com/search.jsp?query=Northwestern+Polytechnic+University"]
# school ids for small dataset
small_set_school_ids = [1152, 4718]
# urls for large dataset 
large_set_school_urls = [ "http://www.ratemyprofessors.com/search.jsp?queryBy=teacherName&queryoption=HEADER&query=University+of+Michigan&facetSearch=true"]
# school ids for large dataset
large_set_school_ids = [1258]

# Takes in text (e.g. professor name, comments, etc.) and strips whitespace
def sanitizeText(text):
	text = str(text)
	text = text.replace('\r', '')
	text = text.replace('\n', '')
	text = re.sub(' +',' ',text)
	text = text.lstrip()
	text = text.rstrip()
	return text

# Makes API call for fetching additional reviews for a professor (i.e. if we need to click "Load More"). Occurs whenever a professor has more than 20 reviews
# Inputs: prof_id (int), review_ids (array), scores (array), comments (array)
# Output: object containing updated review_ids, scores, and comments arrays
def fetchAdditionalReviews(prof_id, review_ids, scores, comments):
	
	# Starting page number
	page = 2
	reviews_remaining = 1
	
	# Request url for api
	request_url = "https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" + str(prof_id) + "&filter=&courseCode=&page="
	
	# Keep making API calls until reviews_remaining is zero, and append each review to scores/comments/review_ids arrays and all_reviews string
	while (reviews_remaining is not 0):
		api_response = get(request_url + str(page))
		reviews = json.loads(api_response.text)['ratings']
		reviews_remaining = int(json.loads(api_response.text)['remaining'])

		for review in reviews:
			review_ids.append(review['id'])
			scores.append(review['rOverall'])
			
			sanitized_comment = sanitizeText(unicodedata.normalize('NFKD', review['rComments']).encode('ascii','ignore'))
			comments.append(sanitized_comment)

		page += 1
	
	ret_obj = {'review_ids': review_ids, 'scores': scores, 'comments': comments}
	return ret_obj


# Thread function takes in URL for given colleges and collects all reviews for each profressor at that university
def runCollege(college_url, school_ids, mode):

	print "Starting to scrape: ", college_url

	# results_pages contains links to all pages of professors for given university
	results_pages = [college_url]
	page_num = 0
	
	for page in results_pages:
		try:

			# Make request to univerity's page and parse
			univ_response = get(page)
			univ_html_soup = BeautifulSoup(univ_response.text, "html.parser")

			# Find any links for next results page of professors and add href to results_pages
			try:
				next_page = univ_html_soup.find('a', class_="nextLink")
				next_link = next_page['href']

				if(next_page != None):
					results_pages.append(rmp_url + str(next_link))

			except:
				pass

			page_of_professors = univ_html_soup.find('ul', class_='listings')
			
			for litag in page_of_professors.find_all('li'):

				#For all profs on page
				for a in litag.find_all('a', href=True):
					try:
						professor = dict()

						# Get professor info
						prof_response = get(rmp_url + a['href'])
						prof_html_soup = BeautifulSoup(prof_response.text, "html.parser")

						# Get professor's unique id
						prof_id = int(a['href'].split('tid=')[1])


						# Get professor's name
						prof_first_name = prof_html_soup.find('span', class_="pfname")
						prof_last_name = prof_html_soup.find('span', class_="plname")
						professor['name'] = sanitizeText(prof_first_name.contents[0]) + ' ' + sanitizeText(prof_last_name.contents[0])

						# Get professor's school info
						prof_school = prof_html_soup.find('a', class_="school", href=True)
						professor['school_id'] = int(prof_school['href'].split('sid=')[1])
						professor['school'] = str(prof_school.contents[0])

						# Ignore any professors that do not belong to any universities that we are scraping
						if professor['school_id'] not in school_ids:
							continue


						# Prepare to collect individual (and concatenated) reviews for each professor
						professor['reviews'] = dict()
						prof_reviews = prof_html_soup.find('table', class_="tftable")
						review_ids = list()
						scores = list()
						comments = list()
					
					except Exception as e:
						continue
					
					try:

						# Get review ids
						for review_id in prof_reviews.find_all('tr'):
							if review_id.has_attr('id'):
								review_ids.append(int(sanitizeText(review_id['id'])))

						# Get scores on this page
						for num_rating in prof_reviews.find_all('td', class_="rating"):
							temp = num_rating.find('div', class_="descriptor-container")
							scores.append(float(temp.span.contents[0]))

						# Get comments on this page
						for comment in prof_reviews.find_all('td', class_="comments"):
							sanitized_comment = sanitizeText(comment.p.contents[0])
							comments.append(sanitized_comment)

						# If a professor has more than 20 reviews, make API call to load other reviews and update scores, comments, and review_ids arrays
						prof_num_reviews = prof_html_soup.find('div', class_ ="rating-count")
						num_reviews = int(sanitizeText(prof_num_reviews.contents[0]).split(' ')[0])
						if num_reviews > 20:
							additional_reviews = fetchAdditionalReviews(prof_id, review_ids, scores, comments)
							review_ids = additional_reviews['review_ids']
							scores = additional_reviews['scores']
							comments = additional_reviews['comments']

						all_reviews = ""
						valid_scores = list()

						# Consolidate reviews and comments into one list and create file with review comment
						for i in range(0, len(scores)):

							# Ignore any reviews that don't have comments
							if comments[i] == "No Comments":
								continue
							if not comments[i]:
								continue

							professor['reviews'][review_ids[i]] = {'overall_quality_score': scores[i], 'comment': comments[i]}
							all_reviews += comments[i] + ' '
							valid_scores.append(scores[i])
							all_scores.append(scores[i])

							# Add words to corpus
							tokens = preprocess(comments[i])
							for token in tokens:
								all_words.append(token)

							# Create file for review (e.g. prof1234.review5678.txt)
							review_filename = "prof"+str(prof_id)+".review"+str(review_ids[i])+".txt"
							review_file = open(review_filename,"w+")
							review_file.write(comments[i])

						# Calculate overall quality score for professor
						professor['overall_quality_score'] = sum(valid_scores)/len(valid_scores)
						# Include concatenated reviews for professor
						professor['all_reviews'] = all_reviews


					except Exception as e:
						pass

					print "Scraped", professor['name'], "with", len(professor['reviews']), "reviews"
					
					# If professor has at least one non-empty review, add to dataset
					if professor['reviews']:
						professors[prof_id] = professor
						professor_ids.append(prof_id)

		except Exception as e:
			pass

		page_num = page_num + 1

	print "Finished scraping: ", college_url


# Cleans up directory
def cleanDirectory(mode):
	# Remove any reviews directory
	if os.path.exists("review_level_reviews_"+mode):
		shutil.rmtree("review_level_reviews_"+mode)
	if os.path.exists("prof_level_reviews_"+mode):
		shutil.rmtree("prof_level_reviews_"+mode)

	# Remove existing .pkl files
	if os.path.exists("professors_"+mode+".pkl"):
		os.remove("professors_"+mode+".pkl")
	if os.path.exists("professor_ids_"+mode+".pkl"):
		os.remove("professor_ids_"+mode+".pkl")
	if os.path.exists("all_scores_"+mode+".pkl"):
		os.remove("all_scores_"+mode+".pkl")


# Iterate over professors and create file with concatenated reviews
def createProfessorLevelReviews():
	for prof_id, professor in professors.iteritems():
		professor_file = open("prof"+str(prof_id)+".txt", "w+")
		professor_file.write(professor['all_reviews'])


def createCorpusDict(all_words):

	corpus_dict = dict()
	word_count = 0

	for word in all_words:
		if word not in corpus_dict:
			corpus_dict[word] = word_count
			word_count += 1

	return corpus_dict


if __name__ == "__main__":

	# Get mode - small vs. large
	# small = dataset from Northwestern Polytechnic Institute and Webb Institute
	# large = dataset from University of Michigan
	if len(sys.argv) < 1:
		print "Please enter a mode: 'small' or 'large'"
		print "    small = dataset from Northwestern Polytechnic Institute and Webb Institute"
		print "    large = dataset from University of Michigan"
		exit(1)
	
	mode = sys.argv[1]

	errorCheckMode(mode)
	cleanDirectory(mode)

	# Create directories for review-level reviews and professor-level_reviews
	if not os.path.exists("review_level_reviews_"+mode):
		os.makedirs("review_level_reviews_"+mode)
	if not os.path.exists("prof_level_reviews_"+mode):
		os.makedirs("prof_level_reviews_"+mode)

	# Enter review_level_reviews during scraping
	os.chdir(os.getcwd()+"/review_level_reviews_"+mode)

	thread_pool = list()
	
	# Set lists of college urls and school ids. Used for scraping
	college_urls = list()
	school_ids = list()
	if mode == "small":
		college_urls = small_set_school_urls
		school_ids = small_set_school_ids
	elif mode == "large":
		college_urls = large_set_school_urls
		school_ids = large_set_school_ids

	#Create a thread to crawl each college, store in thread_pool list
	for url in college_urls:
		try:
			thread = Thread(target = runCollege, args = (url, school_ids, mode, ))
			thread_pool.append(thread)
		except: 
			pass

	# Start all threads
	for thread in thread_pool:
		thread.start()

	# Join all threads so that we can perform pickle dumps at end of function
	for thread in thread_pool:
		thread.join()
	
	os.chdir('..')

	# Create prof_level reviews
	os.chdir(os.getcwd()+"/prof_level_reviews_"+mode)
	createProfessorLevelReviews()
	os.chdir('..')

	# Generate corpus_dict with all words
	corpus_dict = createCorpusDict(all_words)

	# Save professors dictionary to file
	with open("professors_"+mode+".pkl", 'wb') as prof_file:
		pickle.dump(professors, prof_file, protocol=pickle.HIGHEST_PROTOCOL)

	# Save professor_ids array to file
	with open("professor_ids_"+mode+".pkl", 'wb') as prof_ids_file:
		pickle.dump(professor_ids, prof_ids_file, protocol=pickle.HIGHEST_PROTOCOL)

	# Save all_scores array to file
	with open("all_scores_"+mode+".pkl", 'wb') as all_scores_file:
		pickle.dump(all_scores, all_scores_file, protocol=pickle.HIGHEST_PROTOCOL)

	# Save all_scores array to file
	with open("corpus_dict_"+mode+".pkl", 'wb') as corpus_dict_file:
		pickle.dump(corpus_dict, corpus_dict_file, protocol=pickle.HIGHEST_PROTOCOL)

	# Print metrics for dataset
	print "Number of professors:", len(professors)
	print "Number of reviews:", len(all_scores)
	print "Average review:", sum(all_scores)/len(all_scores)
   
