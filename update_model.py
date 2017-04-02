"""
UPDATE MODEL

Update Model
Usage: -
Example: -

update_model.py
TW (2017) 

"""

import query_builder
import sys
import time

def main():
    start = time.time()
    
    query_builder.sklearn_classifier.main()
    end = time.time()
    elapsed = end - start
    print("Time elapsed:", elapsed, "s")

if __name__ == "__main__":
    main()