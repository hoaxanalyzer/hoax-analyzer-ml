import csv
import hashlib
import numpy as np
import pandas as pd
import re
import regex
import sys
import time
from lsa import LSA, all_stopwords
from word2vec import old_calculate_similarity

COL_DESC = "desc"
COL_QUERY_TEXT = "query_text"
COL_QUERY_SEARCH = "query_search"
COL_ARTICLE_CONTENT = "article_content"
COL_LABEL = "label"


# LSA two text
def lsa(text1, text2):
    return 0

# Name entity
def similar_ne(ne1, ne2):
    return 0

def similar_ne_avg(ne1, ne2):
    return 0

# Word Count
def word_count_features(query, text):
    ## This is counting that the query apeared near each other
    text = clear_content(text)
    queryclean = re.sub(r"[^\w\s]|_+", ' ', query.lower())
    querywords = queryclean.split()
    querywords = [word for word in querywords if word not in all_stopwords]

    total = 0
    appeared = 0
    counts = {}
    for word in querywords:
        counts[word] = 0
        words = word.rsplit()
        regexpat = r'%s' % "\s+".join(words)
        pattern = regex.findall(regexpat, text.lower())
        ln = len(pattern)
        counts[word] = ln
        total += ln
        if ln > 0:
            appeared += 1

    feature_query_onesen = 0
    for sentence in text.split("."):
        counter = 0
        for word in querywords:
            if word in sentence:
                counter += 1
        if len(querywords) <= 3:
            if counter == len(querywords):
                feature_query_onesen += 1
        elif (counter/len(querywords)) > 0.55:
            feature_query_onesen += 1

    return total / len(querywords), appeared / len(querywords), feature_query_onesen

# Psychology
def liwc(text1, text2):
    return 0

def clear_content(text):
    return re.sub(r"[^\w\s]|_+", ' ', text)

def extract_file_features(filename, output_file):
    csvfile = open(output_file, 'w')
    wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL, lineterminator='\n')

    header = ["id", "input_sim_article", "query_sim_article", "input_qcount", "input_qpercentage", "input_qonesen", "query_qcount", "query_qpercentage", "query_qonesen", "input_sim_word2vec", "query_sim_word2vec"]
    wr.writerow(header)

    data = pd.read_csv(filename, sep=';', encoding="utf-8", error_bad_lines=False)
    query_list = data[COL_QUERY_TEXT].unique()

    for index, row in data.iterrows():
        features = []
        try:
            query_text = row[COL_QUERY_TEXT]
            query_search = row[COL_QUERY_SEARCH]
            article = row[COL_ARTICLE_CONTENT]
            col_article = data[data[COL_QUERY_TEXT] == query_text][COL_ARTICLE_CONTENT]
            documents = []
            for idx, art in enumerate(col_article):
                documents.append(art)
                if art == article:
                    cur_idx = idx

            # id
            # features.append(hashlib.sha1(article.rstrip().encode()).hexdigest())
            features.append(index)
            # similarity (input - article)
            similar = LSA(query_text, documents)
            features.append(similar.rank[cur_idx][1])
            # similarity (query - article)
            similar = LSA(query_search, documents)
            features.append(similar.rank[cur_idx][1])
            # word count
            query_count, query_percentage, query_onesen = word_count_features(query_text, article)
            features.append(query_count)
            features.append(query_percentage)
            features.append(query_onesen)
            query_count, query_percentage, query_onesen = word_count_features(query_search, article)
            features.append(query_count)
            features.append(query_percentage)
            features.append(query_onesen)
            # # word2vec sim (input - article)
            # features.append(old_calculate_similarity(query_text, article))
            # # word2vec sim (query - article)
            # features.append(old_calculate_similarity(query_search, article))
            # label
            features.append(row[COL_LABEL])
        except:
            while len(features) < len(header):
                features.append(-1)
            features[len(features-1)] = row[COL_LABEL]
        print(features)
        wr.writerow(features)
    print("=============== \n")
    csvfile.close()


def main():
    input_file = "input.txt"
    article_file = "article.txt"
    data_file = "dataset_small.csv"
    output_file = "relatedness_features.csv"

    query = "google buys spotify"
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as myfile:
        input_text = myfile.read().replace('\n', '')

    with open(article_file, 'r', encoding='utf-8', errors='ignore') as myfile:
        article = myfile.read().replace('\n', '')

    # print(language_detection("aku suka sama kucing suka sekali"))
    extract_file_features(data_file, output_file)
    

if __name__ == "__main__":
    main()