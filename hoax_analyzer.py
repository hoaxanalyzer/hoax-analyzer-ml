"""
HOAX ANALYZER

Hoax Analyzer
Usage: -
Example: -

hoax_analyzer.py
TW (2017) 

"""

import query_builder
import sys
import time


def main():
    start = time.time()
    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8', errors='ignore') as myfile:
        text = myfile.read().replace('\n', '')
        query = query_builder.build_query(text)
        print(query)
    end = time.time()
    elapsed = end - start
    print("[inaNLP - Java] Time elapsed:", elapsed, "s")

if __name__ == "__main__":
    main()