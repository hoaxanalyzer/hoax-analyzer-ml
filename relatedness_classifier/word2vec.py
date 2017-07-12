import base64
import gensim
import json
import numpy as np
import urllib.request
from ast import literal_eval
from gensim import models
from scipy import spatial
from utils import LANG_EN, LANG_ID, language_detection, preprocess

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

def avg_feature_vector(words, lang, num_features): #, index2word_set):
    #function to average all words vectors in a given paragraph
    featureVec = np.zeros((num_features,), dtype="float32")
    nwords = 0

    #list containing names of words in the vocabulary
    #index2word_set = set(model.index2word) this is moved as input param for performance reasons
    for word in words:
        # if word in index2word_set:
            wvec = get_word_vector(lang, word)
            if wvec is not None:
                nwords = nwords+1
                featureVec = np.add(featureVec, wvec)

    if(nwords>0):
        featureVec = np.divide(featureVec, nwords)
    return featureVec

def calculate_similarity(first_text, second_text):
    first_text = preprocess(first_text)
    second_text = preprocess(second_text)

    lang = language_detection(first_text + second_text)

    #get average vector for sentence 1
    first_text_avg_vector = avg_feature_vector(first_text.split(), lang, num_features=200)

    #get average vector for sentence 2
    second_text_avg_vector = avg_feature_vector(second_text.split(), lang, num_features=200)

    similarity =  1 - spatial.distance.cosine(first_text_avg_vector,second_text_avg_vector)
    return similarity


def main():
    input_file = "test.txt"
    article_file = "jackie.txt"
    data_file = "dataset_small.csv"

    query = "google buys spotify"
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as myfile:
        input_text = myfile.read().replace('\n', '')

    with open(article_file, 'r', encoding='utf-8', errors='ignore') as myfile:
        article = myfile.read().replace('\n', '')

    # print(calculate_similarity(input_text, article))
    # obj = get_index_to_word(LANG_EN)
    #print(type(obj))
    #print(obj)
    # print(get_word_vector("aku"))
    

if __name__ == "__main__":
    main()