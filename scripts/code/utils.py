import csv
import time
import json
import pandas as pd
import gzip
import math
from datetime import datetime
from collections import namedtuple

"""
Please use this file to put util methods. 
"""
COLS = ['overall','vote', 'verified', 'reviewTime', 'reviewerID', 'asin', 'reviewerName',
       'reviewText', 'summary', 'unixReviewTime', 'image', 'category',
       'description', 'title', 'brand', 'rank', 'price', 'fit', 'main_cat',
       'tech2', 'amazon']
NON_TEXT = ['X','overall', 'vote', 'verified', 'reviewTime', 'reviewerID', 'asin', 'word_count',
            'sentiment','image', 'category', 'brand', 'price', 'main_cat', 'amazon']
COLS_SIM = COLS.append('sim1')
NON_TEXT_SIM = NON_TEXT.append('sim1')

def parse(path):
    '''
    Parse file to JSON
    '''
    g = gzip.open(path, 'rb')
    for l in g:
        yield json.loads(l.decode('utf-8'))

def getDF(path):
    '''
    Get dataframe from .json.gz files
    '''
    i = 0
    df = {}
    for d in parse(path):
        df[i] = d
        i += 1
    return pd.DataFrame.from_dict(df, orient='index')

def is_amazon(x):
    '''
    Label Amazon products based on brand names
    Brand names are listed on Amazon website
    '''
    # Look for an exact match
    amazon_brands = ['Amazon', 'Rivet', 'Stone & Beam', 'AmazonBasics', 'Ravenna Home', 'Pinzon by Amazon', 'Goodthreads', '206 Collective', 'Core 10', 'Presto!', 'Mae', 'Spotted Zebra', 'Amazon Essentials', 'Amazon Elements', 'Mama Bear', 'Basic Care', 'Happy Belly', 'Revly', 'Solimo', 'OWN PWR', 'Mountain Falls', 'P2N Peak Performance Nutrition', 'Nature\'s Wonder', 'Amazing Baby', 'Nod by Tuft & Needle']
    if x in amazon_brands:
        return 1
    return 0
