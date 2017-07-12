import base64
import gensim
import json
import math
import numpy as np
import urllib.request
from ast import literal_eval
from gensim import models
from scipy import spatial
from utils import LANG_EN, LANG_ID, language_detection, preprocess, remove_stopwords
from sklearn.metrics.pairwise import cosine_similarity

id_model_path = "../models/word2vec/word2vec_id.model"
en_model_path = "../models/word2vec/word2vec_en.model" 

# print("loading model")
# id_model = gensim.models.KeyedVectors.load_word2vec_format(id_model_path, binary=False)
# en_model = id_model
# print("model loaded")
# en_model = gensim.models.Word2Vec.load_word2vec_format(en_model_path, binary=True)
# python3 word2vec-api/word2vec-api.py --model ../models/word2vec/word2vec_id.model --path /word2vec --host 0.0.0.0 --port 5000

def get_word_vector(lang, word):
    url = "http://127.0.0.1:5000/word2vec/model?word=" + word + "&lang=" + lang
    r = urllib.request.urlopen(url)
    result = r.read()
    obj = base64.b64decode(result)
    try:
        num = np.fromstring(obj, dtype='<f4')
        # print("HFKJHSDJKHSD")
        # print(num)
        return num
    except:
        return None

def get_index_to_word(lang):
    url = "http://127.0.0.1:5000/word2vec/index_2_word?lang=" + lang
    r = urllib.request.urlopen(url)
    result = r.read()
    # obj = result.decode("utf-8").replace('\\"', "'").replace("\"","")[1:][:-1].split()
    obj = json.loads(result.decode("utf-8"))
    return obj

def avg_feature_vector(words, lang, num_features, index2word_set):
    #function to average all words vectors in a given paragraph
    featureVec = np.zeros((num_features,), dtype=np.float)
    nwords = 0

    #list containing names of words in the vocabulary
    #index2word_set = set(model.index2word) this is moved as input param for performance reasons
    for word in words:
        if word in index2word_set:
            # print("TEST", word)
            wvec = get_word_vector(lang, word)
            if wvec is not None:
                nwords = nwords+1
                featureVec = np.add(featureVec, wvec)

    featureVec[np.any(np.isnan(featureVec))] = 0
    # print(featureVec)
    # print(nwords)
    # print("\n===\n")
    if(nwords>0):
        featureVec = np.divide(featureVec, nwords)
    return featureVec

def old_calculate_similarity(first_text, second_text):
    lang = language_detection(first_text + second_text)

    first_text = remove_stopwords(preprocess(first_text), lang)
    second_text = remove_stopwords(preprocess(second_text), lang)

    index2word_set = set(get_index_to_word(lang))

    #get average vector for sentence 1
    first_text_avg_vector = avg_feature_vector(first_text, lang, 200, index2word_set)

    #get average vector for sentence 2
    second_text_avg_vector = avg_feature_vector(second_text, lang, 200, index2word_set)

    similarity =  1 - spatial.distance.cosine(first_text_avg_vector,second_text_avg_vector)
    if math.isnan(similarity):
        similarity = 0
    return similarity

def calculate_similarity(first_text, second_text):
    lang = language_detection(first_text + second_text)

    first_text = remove_stopwords(preprocess(first_text), lang)
    second_text = remove_stopwords(preprocess(second_text), lang)

    index2word_set = set(get_index_to_word(lang))

    #get average vector for sentence 1
    first_text_avg_vector = getAvgFeatureVecs(first_text, lang, 200, index2word_set)

    #get average vector for sentence 2
    second_text_avg_vector = getAvgFeatureVecs(second_text, lang, 200, index2word_set)

    # print(first_text_avg_vector)
    # print(second_text_avg_vector)
    # print("HAHAHAAHHA")
    mat =  np.array(np.array(first_text_avg_vector), np.array(second_text_avg_vector))
    mat_sparse = sparse.csr_matrix(mat)
    similarity = cosine_similarity(mat_sparse)
    return similarity


def makeFeatureVec(words, lang, num_features, index2word_set):
    # Function to average all of the word vectors in a given
    # paragraph
    #
    # Pre-initialize an empty numpy array (for speed)
    featureVec = np.zeros((num_features,),dtype=np.float)
    #
    nwords = 0.
    #
    # Index2word is a list that contains the names of the words in
    # the model's vocabulary. Convert it to a set, for speed
    # index2word_set = set(model.index2word)
    #
    # Loop over each word in the sku and, if it is in the model's
    # vocaublary, add its feature vector to the total
    for word in words:
        if word in index2word_set:
            nwords = nwords + 1.
            featureVec = np.add(featureVec,get_word_vector(lang, word))
    #
    # Divide the result by the number of words to get the average
    featureVec[np.any(np.isnan(featureVec))] = 0
    if(nwords>0):
        featureVec = np.divide(featureVec,nwords)
    return featureVec


def getAvgFeatureVecs(skucollection, lang, num_features, index2word_set):
    # Given a set of skucollection (each one a list of words), calculate
    # the average feature vector for each one and return a 2D numpy array
    #
    # Initialize a counter
    counter = 0.
    #
    # Preallocate a 2D numpy array, for speed
    reviewFeatureVecs = np.zeros((len(skucollection),num_features),dtype=np.float)
    #
    # Loop through the skucollection
    for sku in skucollection:
       #
       # Print a status message every 1000th sku
       if counter%1000. == 0.:
           print("sku %d of %d" % (counter, len(skucollection)))
       #
       # Call the function (defined above) that makes average feature vectors
       reviewFeatureVecs[int(counter)] = makeFeatureVec(sku, lang, num_features, index2word_set)
       #
       # Increment the counter
       counter = counter + 1.
    return reviewFeatureVecs


def main():
    input_file = "input.txt"
    article_file = "jackie.txt"
    data_file = "dataset_small.csv"

    query = "google buys spotify"
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as myfile:
        input_text = myfile.read().replace('\n', '')

    with open(article_file, 'r', encoding='utf-8', errors='ignore') as myfile:
        article = myfile.read().replace('\n', '')

    sim = old_calculate_similarity(input_text, article)
    


    # obj = get_index_to_word(LANG_EN)
    #print(type(obj))
    #print(obj)
    # print(get_word_vector("aku"))
    

if __name__ == "__main__":
    main()