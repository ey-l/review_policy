import json
import csv
import pandas as pd
import gzip
import math
from datetime import datetime

# To count frequency in lists
import collections
from collections import Counter
from itertools import chain

# For graphing
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# NLP
import spacy

def get_review_lemma(doc):
    # Set up NLP
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(doc)
    lemma = ""
    for token in doc:
        lemma += " " + token.lemma_
    return lemma

def find_ngrams(input_list, n):
    return list(zip(*[input_list[i:] for i in range(n)]))

# Write to .csv
def write_cnter(file_path, cnter, n):
    with open(file_path,'w') as csvfile:
        fieldnames=[str(i) for i in range(n)]
        fieldnames.append('count')
        writer=csv.writer(csvfile)
        writer.writerow(fieldnames)
        for key, value in cnter.items():
            writer.writerow(list(key) + [value]) 


# Load file
reviewText = pd.read_csv('../data/reviewMeta/reviewMeta_before_nonincentive_text.csv', index_col=0, low_memory=False)
n = 6

# Get lemma
reviewText['lemmaText'] = reviewText['x'].apply(get_review_lemma)
log = '../data/reviewMeta/reviewMeta_before_nonincentive_text_ngrams.csv'
reviewText.to_csv(log)

for n in range(5,11):
    # Get ngrams
    reviewText['ngrams'] = reviewText['lemmaText'].map(lambda x: find_ngrams(x.split(" "), n))

    # ngram Frequency Counts
    ngrams = reviewText['ngrams'].tolist()
    ngrams = list(chain(*ngrams))

    # Get the most common
    ngram_counts = Counter(ngrams)

    # Write to .csv
    log = '../data/reviewMeta/'+str(n)+'grams_nonincentive_tokens.csv'
    write_cnter(log, ngram_counts, int(n))
    print('Logged tokens!')

    # Read the saved file
    ngrams_text = pd.read_csv(log, low_memory=False)

    # Combine ngrams
    col = n-1
    ngrams_text['ngrams'] = ngrams_text[ngrams_text.columns[0:col]].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)
    ngrams_text = ngrams_text.dropna()

    # Save only ngrams and count
    ngrams_df = ngrams_text.loc[:,'count':'ngrams']
    ngrams_df = ngrams_df.sort_values('count', ascending=False)
    log = '../data/reviewMeta/'+str(n)+'grams_nonincentive_phrases.csv'
    ngrams_df.to_csv(log)
    print('Logged phrases!')

