"""
ANAPHORA RESOLUTION

Change personal pronouns to their real entity

"""

from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import enchant
import nltk
import re
import requests
import string
import xml.etree.ElementTree as ET

BART_SERVER = 'http://localhost:8125'
d = enchant.Dict("en_US")

ex_text = "Long before he was a contender for the US presidency, Donald Trump was America's most famous and colourful billionaire.\
Once considered a long shot, Trump is now president of the United States.\
Scepticism over Trump's candidacy stemmed not only from his controversial platform on immigration and outrageous campaign style, but from his celebrity past.\
But the 70-year-old businessman had the last laugh when he defied all predictions to beat much more seasoned politicians in the Republican primary race.\
And he has now gone a step further by winning the presidential election, after one of the most divisive and controversial contests in living memory against Democratic rival Hillary Clinton."

ex_text2 = "According to a report from cnminformativo which let us know that the popular actor 'Jackie chan' died of heart attack on the 17th of july 2015. Cry\
The historic actor, who made a name for himself for his incredible performance in 1995 Rumble in the Bronx. His enormous charisma always gave him the opportunity to develop his career as a singer, stuntman, writer, film director and producer. The\
brilliant career of the most famous Chinese ended this morning by a heart attack in a Hong Kong Hospital.\
\
The medical reports indicate that he suffered a fulminate heart attack, which paralyzed his heart making it impossible for the blood to reach his brain, and other vital organs, that caused the death of this humanitarian man, who years before was named philanthropist of the year for his country.\
\
The sad news of Chans's death was given by his wife Lin Feng-jiao in a news conference, a couple of hours ago, where she said to the media, \"I hope you can understand my loss, and I would appreciate if you can give us space for our mourning\" .\
Until now, funeral's details are uncertain, nevertheless, the body of Jackie Chan will be buried next to his\
parents, who taught him the meaning of love for his family."

def bart_coref(text):
    response = requests.post(BART_SERVER + '/BARTDemo/ShowText/process/', data=text)
    return(response.content)

def extract_entity_names(t):
    entity_names = []
    
    if hasattr(t, 'node') and t.node:
        if t.node == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
                
    return entity_names

def anaphora_resolution_la(s):
    tree = ET.parse('jackie.xml')
    root = tree.getroot()

    i = 1
    for coref in root.iter('coref'):
        cur_coref = int(string.replace(coref.attrib.get('set-id'), 'set_', ''))
        print "cur_coref: ", cur_coref
        for child in coref:
            pos = child.attrib.get('pos')
            phrase = ''
            if pos is not None:
                if phrase == '':
                    phrase = child.text
                else:
                    phrase = phrase + ' ' + child.text
                print pos, phrase
            else:
                print "HAHA"

def anaphora_resolution(s):
    # root = ET.fromstring(s)
    tree = ET.parse('jackie.xml')
    root = tree.getroot()

    coref_matrix = {}
    i = 0
    for coref in root.iter('coref'):
        print coref.attrib
        cur_coref = int(string.replace(coref.attrib.get('set-id'), 'set_', ''))
        cur_array = []
        if cur_coref in coref_matrix:
            cur_array = coref_matrix.get(cur_coref)
        phrase = ''
        for child in coref:
            pos = child.attrib.get('pos')
            if pos is not None:
                if phrase == '':
                    phrase = child.text
                else:
                    phrase = phrase + ' ' + child.text
            else:
                for grandchild in child:
                    pos = child.attrib.get('pos')
                    if pos is not None:
                        if phrase == '':
                            phrase = child.text
                        else:
                            phrase = phrase + ' ' + child.text
        cur_array.append([pos, phrase])
        print pos, phrase
        coref_matrix[cur_coref] = cur_array

    sp_change = ['he', 'she', 'it', 'i', 'you', 'we', 'they']
    pd_change = ['his', 'her', 'its', 'my', 'your', 'our', 'their']
    pp_change = ['hers', 'mine', 'yours', 'ours', 'theirs']
    pos_change = ['prp', 'prp$']
    pattern = r'^[A-Z][a-z]*(?:_[A-Z][a-z]*)*$'

    # sentences = nltk.sent_tokenize(ex_text2)
    # tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    # tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    # chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)
    # entity_names = []
    # for tree in chunked_sentences:
    #     entity_names.extend(extract_entity_names(tree))
    #     print set(entity_names)

    cur_nnp = {}
    for idx, coref in coref_matrix.iteritems():
        print idx, coref
        key = ''
        value = ''
        for coref_content in coref:
            content = ''.join(str(x) for x in coref_content[1])
            first_content = str(content).replace(',', ' ').split(' ')
            if (coref_content[0] == 'nnp' or d.check(first_content[0]) is False):
                cur_nnp[coref_content[1]] = coref_content[0]
                if len(value) < len(coref_content[1]):
                    key = coref_content[0]
                    value = coref_content[1]
            else:
                r = re.compile(".*" + coref_content[1] + "*.")
                matching = filter(r.match, cur_nnp.keys())
                if len(matching) > 0 and re.match(pattern, coref_content[1][0]):
                    key = cur_nnp[matching[0]]
                    value = matching[0]
        if value != '':
            for coref_xml in root.iter('coref'):
                cur_coref = int(string.replace(coref_xml.attrib.get('set-id'), 'set_', ''))
                if cur_coref == idx:
                    i = 0
                    for w in coref_xml.iter('w'):
                        if i==0 and (w.get('pos') in pos_change):
                            w.text = str(value)
                            w.set('pos', key)
                        i = i + 1
        tree.write("output.xml")
    result = ''.join(root.itertext()).replace('\n', ' ').replace('  ', ' ').replace(' ,', ',').replace(" 's", "'s")
    return result

def parse(s):
    sentences = s.split(".")
    for idx, s in enumerate(sentences):
        if s[0] == ' ':
            sentences[idx] = sentences[idx][1:]
        if s[len(s)-1] == ' ':
            sentences[idx] = sentences[idx][:len(s)-1]
        if len(s) <= 1:
            sentences.pop(idx)
    return sentences

def main():
    res = (anaphora_resolution("la"))
    print "res"
    print res
    # corpus = []
    # corpus.append(res)
    # toker = RegexpTokenizer(r'((?<=[^\w\s])\w(?=[^\w\s])|(\W))+', gaps=True)
    # word_list = toker.tokenize(res)

    word_list = nltk.word_tokenize(res)
    punctuations = list(string.punctuation)
    filtered_word_list = word_list[:] #make a copy of the word_list
    for word in word_list: # iterate over word_list
      if word in stopwords.words('english') or word in punctuations: 
        filtered_word_list.remove(word) # remove word from filtered_word_list if it is a stopword
    print "HAHAHAAHAH\n\n\n"

    tf = Counter()
    for word in filtered_word_list:
        tf[word] +=1
    sorted(tf, key=tf.get, reverse=True)
    most =  tf.most_common(8)
    query = ''
    for key, word in enumerate(most):
        query = query + str(word[0]) + ' '
    print "query: ", query

if __name__ == "__main__":
    main()