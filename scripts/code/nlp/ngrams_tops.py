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

# Get ngram phrases with a minimum frequency
def get_incentive_text(path, freq):
    # df is ngrams phrases
    df = pd.read_csv(path, index_col=0, low_memory=False)
    df = df.loc[df['count'].apply(lambda x: x >= freq)]
    return df

# main script
ngrams_phrases = pd.DataFrame(columns=['count','ngrams'])
frames = []
frames.append(ngrams_phrases)

# Pending
for n in range(6,11):
    path = '../data/reviewMeta/'+str(n)+'grams_incentive_phrases.csv'
    frames.append(get_incentive_text(path, 10))

ngrams_phrases = pd.concat(frames, ignore_index=True)
ngrams_phrases = ngrams_phrases.sort_values('count', ascending=False)

# Save results
log = '../data/reviewMeta/incentive_text_combined.csv'
ngrams_phrases.to_csv(log, index=False)


