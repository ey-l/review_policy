import json
import pandas as pd
import gzip
import math
from datetime import datetime

# To count frequency in lists
import collections

# For NLP
import numpy as np
import spacy

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

def get_review_lemma(doc):
    # Set up NLP
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(doc)
    lemma = ""
    for token in doc:
        lemma += " " + token.lemma_
    return lemma

def getNegation_tree(x):
	# Set up NLP
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(x)
    negation_tokens = [tok for tok in doc if tok.text in ['not','no']]
    negation_head_tokens = [token.head.text for token in negation_tokens]
    negation_ancestors = []
    for n in negation_tokens:
        n_tokens = n.ancestors
        # The first jump
        for i in n_tokens:
            negation_ancestors.append(i.text)
            children = i.children
            # The second jump
            for j in children:
                negation_ancestors.extend([t.text for t in children])
    result = negation_ancestors + negation_head_tokens
    if len(result) > 0:
        return list(set(result))
    return []

def ifNegation_incentivized(x):
    negation_head_tokens = getNegation_tree(x)
    for i in negation_head_tokens:
        if i in incentivized_flags:
            return 1
    return 0

# Save as .csv
#text.to_csv('../data/Processed_Julian_Amazon_data/merged_review_lemma.csv')