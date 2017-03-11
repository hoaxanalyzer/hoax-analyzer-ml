"""
QUERY BUILDER

Create query from text
Usage: python query_builder.py [dir] [output file]
Example: python query_builder.py test result_x.csv

"""

from information_ex import *
import csv, os

def query_builder(text):
    tokens = tokenize(preprocess(text))
    ne_chunk = chunk_words(tokens)
    ent = entity_recognition(ne_chunk)
    ent_res = count_entity(ent, " ".join(tokens))
    selected_entities = select_entity(ent_res)

    tf = term_frequencies(tokens, selected_entities)
    selected_words = select_words(tf)

    query = build_query(selected_entities, selected_words)
    return query

def main():
	if (len(sys.argv) >= 3):
	    directory = sys.argv[1]
	    file_output = sys.argv[2]

	    csvfile = open(file_output, 'wb')

	    for subdir, dirs, files in os.walk(directory):
	        for filename in files:
	            with open(directory + "/" + filename, 'r') as myfile:
	                text = myfile.read().replace('\n', '')
	                myfile.close()

	            query = query_builder(text)
	            result = [filename, text, query]

	            wr = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
	            wr.writerow(result)
	            print filename, "done!"
	            print "\t", query
	else:
	 	filename = sys.argv[1]
	 	with open(filename, 'r') as myfile:
			text = myfile.read().replace('\n', '')
			myfile.close()

        query = query_builder(text)
        print query

if __name__ == "__main__":
    main()