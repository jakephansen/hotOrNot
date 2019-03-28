import pickle

with open("corpus_dict_small.pkl", 'rb') as file:
	corpus_dict = pickle.load(file)

print len(corpus_dict)