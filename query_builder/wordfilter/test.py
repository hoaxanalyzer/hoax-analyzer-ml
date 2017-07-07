import re

#this python example doesn't support text with html tags
text = "duh-p3n1s babi kebab i k4mpr3t halo the Pen is mightier penisilin p e ni s dan lainnya a.s.s-h-o-l-e kampret ass classic kucing andhjieng si b r e n g s e k d a n v i r g i n"

patt = open('id.re.txt', 'r').read()
regex = '\\b((?:' + patt + ')+)\\b'
result = re.sub(regex, '*****', text, flags=re.IGNORECASE)

print text + "\n"
print result
