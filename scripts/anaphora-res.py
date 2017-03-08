"""
ANAPHORA RESOLUTION

Change personal pronouns to their real entity

"""

from sklearn.feature_extraction.text import CountVectorizer
import requests
import string
import xml.etree.ElementTree as ET

BART_SERVER = 'http://localhost:8125'

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
                cur_array.append([pos, phrase])
                print pos, phrase
            else:
                print "HAHA"
        coref_matrix[cur_coref] = cur_array

    sp_change = ['he', 'she', 'it', 'i', 'you', 'we', 'they']
    pd_change = ['his', 'her', 'its', 'my', 'your', 'our', 'their']
    pp_change = ['hers', 'mine', 'yours', 'ours', 'theirs']

    for idx, coref in coref_matrix.iteritems():
        key = ''
        value = ''
        for coref_content in coref:
            if coref_content[0] == 'nnp' and len(value) < len(coref_content[1]):
                key = coref_content[0]
                value = coref_content[1]
        for coref_xml in root.iter('coref'):
            cur_coref = int(string.replace(coref_xml.attrib.get('set-id'), 'set_', ''))
            # print cur_coref
            if cur_coref == idx:
                i = 0
                for w in coref_xml.iter('w'):
                    if i==0 and (w.text in sp_change or w.text in pd_change or w.text in pp_change):
                        if (w.text in sp_change):
                            w.text = str(value)
                            w.set('pos', key)
                        elif (w.text in pd_change or w.text in pp_change):
                            w.text = str(value) + '\'s'
                            w.set('pos', key)
                    i = i + 1

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
    # bart = bart_coref(ex_text2)
    # print "bart"
    # print bart
    res = (anaphora_resolution("la"))
    print "res"
    print res
    # cvec = CountVectorizer()
    # counts = cvec.fit_transform(res)   
    # print(cvec.vocabulary_)

if __name__ == "__main__":
    main()