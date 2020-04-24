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
