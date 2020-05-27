import csv
import time
import json
import pandas as pd
import gzip
import math
from datetime import datetime
import collections

from utils import getDF, is_amazon

'''
Usage instructions:
    
    This script 
        1) Merges meta_product_data with review_data files for each category
        2) Records the count info
    
    Primary use case: Given a list of file paths
'''

def common_member(a, cats): 
    a_set = set(a) 
    b_set = set(cats) 
    if (a_set & b_set): 
        return True 
    else: 
        return False

def remove_uncommon(x, cats):
    return list(set(x) & set(cats))

def create_cols(df, cats):
    for i in cats:
        df[i] = df['category'].apply(lambda x: int(i in x))


def merge_datasets(product_path, review_path):
    # Read the files
    reviews = getDF(review_path)
    print("Loaded review dataset: {}".format(review_path))
    df = getDF(product_path)
    print("Loaded product dataset:{}".format(product_path))

    # Drop irrelevant columns
    print("Drop irrelevant columns")
    df.drop(['image','feature', 'also_buy', 'also_view', 'similar_item', 'date', 'details', 'tech1'], axis=1, inplace=True)
    
    # Drop records with nan in category
    df = df.dropna(subset=['category'])

    # Set the title to empty if bad data presents
    print("Setting bad data to empty strings")
    df.loc[df['title'].map(str).map(len) > 1000,'title'] = ''
    print("Successfully set bad data to empty strings")

    # Add amazon label to each product
    df['amazon'] = df['brand'].apply(is_amazon)

    # 1459641600 is the Unix timestamp of 2016-04-03
    # 1491177600 is the Unix timestamp of 2017-04-03
    # 1522713600 is the Unix timestamp of 2018-04-03
    # Get reviews within the 1 year time frame
    #reviews = reviews.loc[reviews['unixReviewTime'].apply(lambda x: x > 1459641600 and x < 1522713600)]
    reviews = reviews.loc[reviews['unixReviewTime'].apply(lambda x: x > 1459641600)]

    # All records have the same category labels
    cats = []
    df['category'].apply(lambda x: cats.extend(x))

    # Get the top 10 subcategories as a list
    cats = collections.Counter(cats)
    cats = {k: v for k, v in reversed(sorted(cats.items(), key = lambda item: item[1]))}
    cats = list(cats.keys())[0:1]

    # Get products within top subcategories
    df = df.loc[df['category'].apply(lambda x: common_member(x, cats))]
    df['category'] = df['category'].apply(lambda x: remove_uncommon(x, cats)) # Remove subcategories not in tops

    # Create a binary column for each subcategory
    create_cols(df, cats)

    # Join and remove asin with less than 10 reviews
    df_merged = pd.merge(reviews, df, on='asin')
    df_merged['review_count'] = df_merged.groupby('asin')['asin'].transform('count') # Count reviews/asin
    df_merged = df_merged.loc[df_merged['review_count'] > 10]

    # Save to file
    name_string = 'merged_'+cats[0].replace(' ','_')
    df_merged.to_csv('../data/'+name_string+'.csv', index=False)
    print("Successfully merged datasets for category: "+name_string)

    # Count the number products in each subcategory
    #cols = ['asin','amazon'] + cats
    #df_asin = df_merged[cols].drop_duplicates()
    #products_count = df_asin.groupby([df_asin['amazon']]).sum().astype(int)

    # Count the number reviews in each subcategory
    #reviews_count = df_merged.groupby([df_merged['amazon']]).sum().astype(int)[cats]

    #return [cats[0], products_count.iloc[1,0], reviews_count.iloc[1,0], products_count.iloc[0,0], reviews_count.iloc[0,0]]

def get_counts(log_path, paths):
    """
    Merge the product meta dataset and the review dataset of a category, get the count of Amazon and non-Amazon products
    :param log_path: file path to save the count information
    :param paths: tuples of raw meta data and review data
    """
    merge_datasets(paths[0], paths[1])
    '''
    with open(log_path, 'a') as csvfile:
        fieldnames = ['category','amazon_products','amazon_reviews','nonamazon_products','nonamazon_reviews','time'] # time in min
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        start = time.time()
        results = merge_datasets(paths[0], paths[1])
        end = time.time()
        print((end - start)/60)
        writer.writerow({'category':results[0], 'amazon_products': results[1], 'amazon_reviews': results[2], 'nonamazon_products': results[3], 'nonamazon_reviews': results[4], 'time': (end - start)/60})
    '''

if __name__ == "__main__":
    """
    Use case
    """
    log = "../data/counts.csv"
    q = []

    q.append(('../data/Julian_Amazon_data/meta_Cell_Phones_and_Accessories.json.gz','../data/Julian_Amazon_data/Cell_Phones_and_Accessories.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Clothing_Shoes_and_Jewelry.json.gz','../data/Julian_Amazon_data/Clothing_Shoes_and_Jewelry.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Home_and_Kitchen.json.gz','../data/Julian_Amazon_data/Home_and_Kitchen.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Electronics.json.gz','../data/Julian_Amazon_data/Electronics.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Office_Products.json.gz','../data/Julian_Amazon_data/Office_Products.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Tools_and_Home_Improvement.json.gz','../data/Julian_Amazon_data/Tools_and_Home_Improvement.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Sports_and_Outdoors.json.gz','../data/Julian_Amazon_data/Sports_and_Outdoors.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Patio_Lawn_and_Garden.json.gz','../data/Julian_Amazon_data/Patio_Lawn_and_Garden.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Pet_Supplies.json.gz','../data/Julian_Amazon_data/Pet_Supplies.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Automotive.json.gz','../data/Julian_Amazon_data/Automotive.json.gz'))
    q.append(('../data/Julian_Amazon_data/meta_Video_Games.json.gz','../data/Julian_Amazon_data/Video_Games.json.gz'))
    
    #q.append(('../data/Julian_Amazon_data/meta_AMAZON_FASHION.json.gz','../data/Julian_Amazon_data/AMAZON_FASHION.json.gz'))
    #q.append(('../data/Julian_Amazon_data/meta_Appliances.json.gz','../data/Julian_Amazon_data/Appliances.json.gz'))
    #q.append(('../data/Julian_Amazon_data/meta_Industrial_and_Scientific.json.gz','../data/Julian_Amazon_data/Industrial_and_Scientific.json.gz'))

    for i in q:
    	#get_counts(log, i)
        merge_datasets(i[0], i[1])

