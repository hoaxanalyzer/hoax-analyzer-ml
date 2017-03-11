from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag.stanford import StanfordNERTagger
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import nltk
import operator
import pattern.en as en
import re
import string
import sys


# st = StanfordNERTagger('lib/stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz', 'lib/stanford-ner/stanford-ner.jar')
n_entities = 3
n_term_max = 6
n_term_min = 2
change_threshold = 1.0

with open('stopwords_en.txt', 'r') as myfile:
    hoax_stopwords = myfile.read()
    hoax_stopwords = word_tokenize(hoax_stopwords)

##################
### PREPROCESS ###
##################

def preprocess(text):
	text = text.decode("ascii", "replace").replace(u"\ufffd", "_").replace("___", "'").replace("'s", " ").replace("``", " ").replace("''", " ")
	return text

def tokenize(text):
	return word_tokenize(text)

def chunk_words(tokens):
    return ne_chunk(pos_tag(tokens))

##########################
### ENTITY RECOGNITION ###
##########################

# def entity_recognition_stanford(text):
#     for sent in nltk.sent_tokenize(text):
#         tokens = nltk.tokenize.word_tokenize(sent)
#         tags = st.tag(tokens)
#         for tag in tags:
#             print tag

def entity_recognition(chunked):
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
            if type(i) == Tree:
                    current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:
                    named_entity = " ".join(current_chunk)
                    if named_entity not in continuous_chunk:
                            continuous_chunk.append(named_entity)
                            current_chunk = []
            else:
                    continue
    # entities = []
    # for entity in continuous_chunk:
    # 	ent = ''
    # 	for idx, word in enumerate(entity.split(' ')):
    # 		if idx > 0:
    # 			if word == entity[idx-1]:
    # 				continue
    # 			elif len(ent) > 0:
    # 				ent += ' ' + word
    # 			else:
    # 				ent += word
    # 		else:
    # 			ent += word
    # 		if ent not in entities:
    # 			entities.append(ent)
    # return entities
    return continuous_chunk

def count_entity(entities, text):
	tf = {}
	sentences = text.split('.')
	for entity in entities:
		parsed_entity = entity.split(' ')
		first_appear = 0
		for pars in parsed_entity:
			n_match = 0
			for idx, sentence in enumerate(sentences):
				matching = re.findall('\w*' + pars +  '\w*', sentence)
				if len(matching) > 0 and (first_appear == 0 or first_appear > (idx+1)):
					first_appear = idx + 1
					break
			matching = re.findall(r"([^.]*?" + pars + "[^.]*\.)", text)
			n_match = len(matching)
			try:
				tf[entity]['count'] += n_match/(len(parsed_entity)* 1.0)
			except KeyError:
				tf[entity] = {}
				tf[entity]['count'] = n_match/(len(parsed_entity)* 1.0)
		tf[entity]['first_appear'] = first_appear
	return tf

def select_entity(entities):
	sorted_ent = sorted(entities.items(), key=operator.itemgetter(1), reverse=True)
	if len(sorted_ent) >= n_entities:
		return sorted_ent[:n_entities]
	else:
		i = 1
		while len(sorted_ent) < n_entities:
			sorted_ent["null_" + i] = 0
			i += 1
		return sorted_ent

################################
### EXTRACT MOST COMMON WORD ###
################################

def term_frequencies(tokens):
	# lmtzr = WordNetLemmatizer()
	# stemmer = SnowballStemmer("english")
	punctuations = list(string.punctuation)

	tf = {}
	i = 0
	len_token = len(tokens)
	for token in tokens:
		# token = stemmer.stem(token)
		# token = lmtzr.lemmatize(token)
		token = en.lemma(token)
		if token not in stopwords.words('english') and token not in punctuations and token not in hoax_stopwords and len(token) > 1 and token != "''" and token != "``":
			# print token, 1.0 * (len_token - i) / (len_token * 1.0)
			try:
				tf[token] += 1.0 * (len_token - i) / (len_token * 1.0)
			except KeyError:
				tf[token] = 1.0 * (len_token - i) / (len_token * 1.0)
		elif token == ".":
			i += 1
	tf = sorted(tf.items(), key=operator.itemgetter(1), reverse=True)
	return tf

def select_words(tf):
	sliced_tf = []
	for term in tf:
		if len(sliced_tf) < n_term_max:
			sliced_tf.append(term)
		else:
			break
	return sliced_tf

def build_query(selected_entities, selected_words):
	query = ''
	for entity in selected_entities:
		query += str(entity[0]) + ' '
		break

	prev_count = 0
	i = 1
	found = False
	for word in selected_words:
		term = str(word[0])
		cur_count = word[1]
		if prev_count != 0:
			if (prev_count - cur_count) > change_threshold and i > n_term_min:
				# query += " [[ "
				# found = True
				break
		if term.lower() not in query.lower().split(' '):
			query += term + ' '
		prev_count = cur_count
		i += 1
	# if found:
	# 	query += " ]]"
	# else:
	# 	query += " [[ ]]"
	return query

############
### MAIN ###
############

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        text = myfile.read().replace('\n', '')

    
	print text, "\n\n"

    # entity_recognition_stanford(text)
    tokens = tokenize(preprocess(text))
    ne_chunk = chunk_words(tokens)
    ent = entity_recognition(ne_chunk)
    print ent
    ent_res = count_entity(ent, " ".join(tokens))
    selected_entities = select_entity(ent_res)
    print "# ENTITY RECOGNITION #"
    print selected_entities
    print "\n\n"

    print "# TERM FREQUENCY #"
    tf = term_frequencies(tokens)
    print tf
    selected_words = select_words(tf)
    print selected_words
    print "\n\n"

    print "# QUERY RESULT #"
    query = build_query(selected_entities, selected_words)
    print query


if __name__ == "__main__":
    main()