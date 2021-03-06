"""
FEATURE EXTRACTOR

Module for extracting tag features from text
Usage: python feature_extractor.py [file] or python feature_extractor.py [dir] [output_file]
Example: python feature_extractor.py jackie.txt or python feature_extractor.py test output.csv

feature_extractor.py
TW (2017)

"""

from multiprocessing.pool import ThreadPool
from nltk import word_tokenize
from nltk.corpus import stopwords
from query_builder.english.tagger import tagging
from query_builder.english.preprocessor import all_stopwords
from query_builder.english.word_feature import WordFeature
from query_builder.ms_text_analytics import detect_key_phrases
from threading import Thread
import concurrent.futures
import csv
import json
import operator
import os
import sys
import threading

acceptible_tags = ["NNP", "JJ", "NN", "VBP", "CD", "VB"]
n_word = 5
avg_word = 7
n_sen = 2

def extract_key_phrases(text, kp_result):
    json_data = {}
    json_doc = []
    json_text = {}
    json_text["id"] = "1"
    json_text["text"] = text
    json_text["language"] = "en"
    json_doc.append(json_text)
    json_data["documents"] = json_doc
    json_data = json.dumps(json_data)
    result = ""
    key_phrase_analysis = detect_key_phrases(json_data)
    for key in key_phrase_analysis:
        for val in key['keyPhrases']:
            if val not in ["text", "id", "language", "documents"]:
                result += val + " "
    kp_result.append(result)
    return result

def count_token_tag(text, tag_dict):
    token_tag = tagging(text)

    # Count in Text
    len_token = len(token_tag)
    w = 1 # word position
    s = 1 # word position in sentence

    for tk in token_tag:
        token = tk[0]
        tag = tk[1]
        if tag == "NNPS":
            token = token[:len(token)-1]
            tag = "NNP"
        if token == '.':
            s += 1
        elif tag in acceptible_tags:
            n = 1 + 2.0 * (len_token - w) / (len_token * 1.0)
            if w < n_sen * avg_word:
                n += 1
            try:
                tag_dict[tag][token].increment_count(n)
            except KeyError:
                try:
                    tag_dict[tag][token] = WordFeature(token, w, s, n)
                except KeyError:
                    tag_dict[tag] = {}
                    tag_dict[tag][token] = WordFeature(token, w, s, n)
        w += 1
    return tag_dict

def extract_tag(text):
    tag_dict = {}
    kp_arr = []
    kp_thread = Thread(target=extract_key_phrases, args=(text, kp_arr))
    tg_thread = Thread(target=count_token_tag, args=(text, tag_dict))

    kp_thread.start()
    tg_thread.start()

    kp_thread.join()
    tg_thread.join()

    if len(kp_arr) > 0:
        key_phrase = kp_arr[0]
    else:
        key_phrase = ""

    # Count using Microsoft's Text Analytics
    w = 1 # word position
    s = 1 # word position in sentence
    kp_tag = tagging(key_phrase)
    for kp in kp_tag:
        token = kp[0]
        tag = kp[1]
        if tag == "NNPS":
            token = token[:len(token)-1]
            tag = "NNP"
        if tag in acceptible_tags and token not in all_stopwords:
            try:
                tag_dict[tag][token].increment_key_phrase()
            except KeyError:
                try:
                    tag_dict[tag][token] = WordFeature(token, w, s, 1)
                except KeyError:
                    tag_dict[tag] = {}
                    tag_dict[tag][token] = WordFeature(token, w, s, 1)
        w += 1

    for key in acceptible_tags:
        if key in tag_dict:
            tag_dict[key] = sorted(tag_dict[key].values(),key=operator.attrgetter('prob', 'kp_count', 'word_pos'), reverse=True)
            tag_dict[key] = tag_dict[key][:5]
            
        else:
            tag_dict[key] = []
        while len(tag_dict[key]) < n_word:
                tag_dict[key].append(WordFeature(WordFeature.null, 0, 0, 0))
    return tag_dict

def extract_tag_to_csv(directory, file_output):
    csvfile = open(file_output, 'a')
    header = ["fname", "text"]
    for tag in acceptible_tags:
        for i in range(1,6):
            header.append(tag.lower() + str(i) + "_token")
            header.append(tag.lower() + str(i) + "_prob")
            header.append(tag.lower() + str(i) + "_wcount")
            header.append(tag.lower() + str(i) + "_kpcount")
            header.append(tag.lower() + str(i) + "_wpos")
            header.append(tag.lower() + str(i) + "_spos")
        header.append(tag.lower() + "class")
    wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL, lineterminator='\n')
    wr.writerow(header)
    for subdir, dirs, files in os.walk(directory):
        for filename in files:
            with open(directory + "/" + filename, 'r') as myfile:
                text = myfile.read().replace('\n', '')
                myfile.close()

            result = [filename, text]
            tag_feature = extract_tag(text)
            for tag in acceptible_tags:
                for val in tag_feature[tag]:
                    result.append(val.token)
                    result.append(val.prob)
                    result.append(val.w_count)
                    result.append(val.kp_count)
                    result.append(val.word_pos)
                    result.append(val.sentence_pos)
                result.append("")

            wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL, lineterminator='\n')
            wr.writerow(result)
            print(filename, "done!")

def print_tag_dict(tag_dict):
    for key in tag_dict:
        print(key)
        for gkey in tag_dict[key]:
            print(gkey, tag_dict[key][gkey].token, tag_dict[key][gkey].prob, tag_dict[key][gkey].w_count, tag_dict[key][gkey].word_pos, tag_dict[key][gkey].sentence_pos)
        print("\n")

def print_tag_dict_key(tag_dict, key):
    print(key)
    for gkey in tag_dict[key]:
        print(gkey.token, gkey.prob, gkey.w_count, gkey.kp_count, gkey.word_pos, gkey.sentence_pos)
    print("\n")

def main():
    if (len(sys.argv) >= 3):
        directory = sys.argv[1]
        file_output = sys.argv[2]

        extract_tag_to_csv(directory, file_output)

    else:
        filename = sys.argv[1]
        with open(filename, 'r') as myfile:
            text = myfile.read().replace('\n', '')
        extract_tag(text)

if __name__ == "__main__":
    main()