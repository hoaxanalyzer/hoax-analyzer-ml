"""
HOAX ANALYZER

Hoax Analyzer
Usage: -
Example: -

hoax_analyzer.py
TW (2017) 

"""

import json
import query_builder
import sys
import time

def main():
    start = time.time()
    input_type = sys.argv[1]
    filename = sys.argv[2]
    
    if(input_type == "text"):
        with open(filename, 'r', encoding='utf-8', errors='ignore') as myfile:
            text = myfile.read().replace('\n', '')
            query = query_builder.build_query_from_text(text)
            print(query)
    elif (input_type == "image"):
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
            result1 = query_builder.image_to_text(b)
            print(result1)
            text = json.loads(result1)["text"]
            result2 = query_builder.build_query_from_image(result1)
            print(result2)

    end = time.time()
    elapsed = end - start
    print("Time elapsed:", elapsed, "s")

if __name__ == "__main__":
    main()