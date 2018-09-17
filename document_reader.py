import re
import os 
import csv
import string
from collections import defaultdict

caps = "([A-Z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"
path = os.getcwd()

def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + caps + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(caps + "[.]" + caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(caps + "[.]" + caps + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + caps + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences

PREPOSITIONS = {'a', 'an', 'as', 'did', 'or', 'does'} 

result = defaultdict(dict)

files = []

for _, _, file_names in os.walk(path):
    files = file_names


for file in files:
    if file in  {__file__, 'result.csv'}:
        continue
    with open(file, 'r') as file_content:
        sentences = split_into_sentences(file_content.read())

        for sentence in sentences:
            word_list = set(re.sub('[{}]'.format(string.punctuation), " ",  sentence).split())

            for word in word_list:

                if word in PREPOSITIONS:
                    continue
                    
                result[word.lower()].setdefault('document', set()).add(file)
                result[word.lower()].setdefault('sentences', set()).add(sentence)



with open('result.csv', 'w', newline='') as outfile:

    fieldnames = ['Word', 'Documents', 'Sentences']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for word, properties in result.items():

        writer.writerow({'Word': word, 'Documents': ','.join(properties['document']), 'Sentences': '\n'.join(properties['sentences'])})
