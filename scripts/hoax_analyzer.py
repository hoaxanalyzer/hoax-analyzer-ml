"""
HOAX ANALYZER

Hoax Analyzer
Usage: -
Example: -

hoax_analyzer.py
TW (2017) 

"""

from preprocessor import preprocess as en_preprocess
from ms_text_analytics import detect_language
from subprocess import Popen, PIPE, STDOUT
from weka_classifier import classify_json_object
import weka.core.jvm as jvm
import json
import sys

query_len = 14
lang_not_supported = "LANGUAGE NOT SUPPORTED"

def is_query(text):
    if len(text.split(" ")) > 14:
        return False
    else:
        return True

def generate_idn_query(json_data):
    query = []
    nnp_pred = classify_json_object("nnp", json_data)
    nnp_pred = int(nnp_pred[len(nnp_pred)-1:])
    for i in range(0, nnp_pred):
        token = json_data["nnp" + str(i + 1)]["nnp" + str(i + 1) + "_token"]
        if token not in query:
            query.append(token)

    nn_pred = classify_json_object("nn", json_data)
    nn_pred = int(nn_pred[len(nn_pred)-1:])
    token = json_data["nn" + str(i + 1)]["nn" + str(i + 1) + "_token"]
    if token not in query:
        query.append(token)

    cdp_pred = classify_json_object("cdp", json_data)
    cdp_pred = int(cdp_pred[len(cdp_pred)-1:])
    token = json_data["cdp" + str(i + 1)]["cdp" + str(i + 1) + "_token"]
    if token not in query:
        query.append(token)
    return " ".join(query).replace("\"", " ")

def build_query(text):
    lang = detect_language(text)

    # English Query
    if is_query(text) and lang == "English":
        query = en_preprocess(text)

    # Indonesian Query
    elif is_query(text) and lang == "Indonesian":
        p = Popen(['java', '-jar', '../lib/HoaxAnalyzer.jar', 'preprocess', text], stdout=PIPE, stderr=STDOUT)
        result = []
        for line in p.stdout:
            arr_token = line.decode("ascii", "replace").split(" ")
            for token in arr_token:
                if token not in result and token != '_url_' and len(token) > 0:
                    result.append(token)
        query = " ".join(result)

    # English Text
    elif not is_query(text) and lang == "English":
        query = "kulelah ngemodelin yg bhs indo"

    # Indonesian Text
    elif not is_query(text) and lang == "Indonesian":
        p = Popen(['java', '-jar', '../lib/HoaxAnalyzer.jar', 'extract', text], stdout=PIPE, stderr=STDOUT)
        query = ""
        result = ""
        for line in p.stdout:
            result += line.decode("ascii", "replace") + " "
        json_res = json.loads(result)
        try:
            jvm.start()
            query = generate_idn_query(json_res)
        except Exception as e:
            print(traceback.format_exc())
        finally:
            jvm.stop()

    # Not supported
    else:
        query = lang_not_supported
    return query

def main():
    filename = sys.argv[1]
    with open(filename, 'r') as myfile:
        text = myfile.read().replace('\n', '')
        query = build_query(text)
        print(query)

if __name__ == "__main__":
    main()