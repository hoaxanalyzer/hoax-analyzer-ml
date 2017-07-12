import enchant
import multiprocessing
import re
import string
import unicodedata
from gensim import corpora, models, similarities
from langdetect import detect
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from nltk.corpus import stopwords
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
from subprocess import Popen, PIPE, STDOUT


dictionary = enchant.Dict("en_US")
lemmatizer = WordNetLemmatizer()
en_stopwords = stopwords.words('english')
punctuations = list(string.punctuation)
all_stopwords = set(en_stopwords + punctuations)

CORE_NUM = multiprocessing.cpu_count()
if CORE_NUM == 1:
    CORE_NUM = 2


LANG_EN = "en"
LANG_ID = "id"

def language_detection(text):
    return detect(text)

def preprocess(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode("ascii", "ignore")
    text = text.replace("'s", " ").replace("'"," ").replace("`"," ")
    text = re.sub(r"[^\w\s]|_+", ' ', text)
    return text

def stopword_checker(word):
    if word not in all_stopwords:
        return word
    else:
        return ""

def old_remove_stopwords(text, lang):
    tokens = tokenize(text)
    if lang == LANG_ID:
        p = Popen(['java', '-jar', '../lib/HoaxAnalyzer.jar', 'preprocess', text], stdout=PIPE, stderr=STDOUT)
        for line in p.stdout:
            result += line.decode("ascii", "replace") + " "
        return result.split()
    else: #en
        pool = Pool(CORE_NUM)
        results = pool.starmap(stopword_checker, zip(tokens))
        return results

def remove_stopwords(text, lang):
    if lang == LANG_ID:
        p = Popen(['java', '-jar', '../lib/HoaxAnalyzer.jar', 'preprocess', text], stdout=PIPE, stderr=STDOUT)
        for line in p.stdout:
            result += line.decode("ascii", "replace") + " "
        return result.split()
    else: #en
        preprocessed = preprocess(text)
        res = [word for word in preprocessed.split() if word not in all_stopwords]
        return res

def tokenize(text):
    tokens = word_tokenize(text)
    return tokens

def lemmed(text, cores=CORE_NUM): # tweak cores as needed
    with Pool(processes=cores) as pool:
        result = pool.map(lemmatizer.lemmatize, text)
    return result

def lemmatize(text):
    text = preprocess(text)
    if language_detection(text) == LANG_ID:
        result = ""
        p = Popen(['java', '-jar', '../lib/HoaxAnalyzer.jar', 'preprocess', text], stdout=PIPE, stderr=STDOUT)
        for line in p.stdout:
            result += line.decode("ascii", "replace") + " "
        return result.split()
    else: #english
        tokens = tokenize(text)
        try:
            # Create new threads
            results = [word for word in tokens if word not in all_stopwords]
            for idx, token in enumerate(results):
                if token.isupper() or token.istitle():
                    if dictionary.check(token.lower()):
                        results[idx] = token.lower()

            return results
            # sample_text = results * (10 ** CORE_NUM)
            # lemmed_text = lemmed(sample_text)
            # # assert len(sample_text) == len(lemmed_text) == (10 ** CORE_NUM) * len(results)
            # return lemmed_text[:len(results)]
        except Exception as e:
            print(str(e))
        return ["kucing", "terbang"]