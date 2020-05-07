import sys
#sys.path.append('..')
# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

import csv
import time
import json
import pandas as pd
import numpy as np
import gzip
import math
from datetime import datetime, timedelta

from utils import COLS_SIM, NON_TEXT_SIM

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
SID = SentimentIntensityAnalyzer()

'''
Process datasets by aggregating review data to a week-product level, specifically by
    - select relevant columns (e.g., non-textual attributes for now)
    - parse price ranges to a single integer by getting the mean
    - get sentiment scores using nltk package
    - add week dummies
'''

def nltk_polarity(text):
    if isinstance(text, str):
        print('hey')
        return SID.polarity_scores(text)['compound']
    return np.NaN

def get_image_count(x): 
    if (type(x) is str):
        return x.count(',')
    return 0

def get_int(x):
    if (type(x) is str):
        return float(int(x.replace(',', '')))
    if (math.isnan(x)):
        return 0
    return x

def handle_price(x):
    if isinstance(x, str):
        x = x.replace('$','')
        prices = x.replace(' ','').replace(',','').split('-')
        prices = [float(i) for i in prices]
        x = np.mean(prices)
        return x
    return np.NaN

def get_selected_data(paths, save_to, verbose=True):
    df_list = []
    for i in paths:
        ORIGINAL_DATASET = i[0]
        DATASET_NAME = i[1]
        TOP10_SIMILAR = '../data/Processed_Julian_Amazon_data/sim_reviews/'+DATASET_NAME+'_10_similar_reviews.csv'
	
        # Get selected data columns
        df = pd.read_csv(TOP10_SIMILAR, index_col=0, low_memory=False)
        df = df.loc[:,COLS_SIM]
        df['overall'] = df['overall'].apply(get_int)
        df['vote'] = df['vote'].apply(get_int)
        df['reviewTime'] = df['reviewTime'].apply(lambda x: str(datetime.strptime(x, '%m %d, %Y').date()))
        df['word_count'] = df['reviewText'].apply(lambda x: len(str(x)))
        df['sentiment'] = df['reviewText'].apply(nltk_polarity)
        df['image'] = df['image'].apply(get_image_count)
        df['category'] = df['category'].apply(lambda x: x.strip('][').strip('\''))
        df['price'] = df['price'].apply(handle_price)
        
        if verbose:
        	print("Size before dropping duplicates: %d" % df.shape[0])
        df.drop_duplicates(keep='first', inplace=True)
        if verbose: 
        	print("Size after dropping duplicates: %d" % df.shape[0])
        
        df_list.append(df)
        
        if verbose: 
        	print("Successfully appended "+DATASET_NAME)

    df_merged = pd.concat(df_list, ignore_index=True)
    print(df_merged.loc[0:4,'overall'])
    print(df_merged.columns)
    # Get the numeric attributes only
    df_merged = df_merged.loc[:, NON_TEXT_SIM]
    df_merged.to_csv(save_to, index=False)
    print("Successfully saved the merged file")

def get_selected_columns(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    df = df.loc[:, NON_TEXT_SIM]
    print(df.shape[0])
    df.to_csv(save_to)
    print("Successfully saved the file with selected columns")

def get_weekly_stats(file_path, save_to):
    df = pd.read_csv(file_path, index_col=0)
    df['week'] = df['reviewTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') - timedelta(days=datetime.strptime(x, '%Y-%m-%d').weekday()))
    groups = df.groupby(['asin','week'], as_index=False)
    cols = ['asin','week','avg_rating','weekly_review_count','avg_word_count','avg_sentiment','avg_vote','avg_image']
    df_weekly = pd.DataFrame(columns=cols)
    for group in groups:
        df_group = group[1]
        df_group['avg_rating'] = df_group['overall'].mean()
        df_group['avg_word_count'] = df_group['word_count'].mean()
        df_group['avg_sentiment'] = df_group['sentiment'].mean()
        df_group['avg_vote'] = df_group['vote'].mean()
        df_group['avg_image'] = df_group['image'].mean()
        df_group['weekly_review_count'] = df_group.shape[0]
        df_group.drop_duplicates(keep='first', inplace=True)
        df_weekly = pd.concat([df_weekly, df_group[cols]], ignore_index=True)
        print('Successfully calculated weekly stats for product ID {} in week {}'.format(group[0][0], group[0][1]))
    df = pd.merge(df, df_weekly, on=['asin','week'])
    df.to_csv(save_to, index=False)
    print("Successfully saved the file with calculated weekly stats")

def get_products_data(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    df_cols = ['asin','week','category','brand','price','main_cat','sim1','amazon','avg_rating','weekly_review_count','avg_word_count','avg_sentiment','avg_vote','avg_image']
    df_products = df[df_cols]
    df_products.drop_duplicates(keep='first',inplace=True)
    df_products.to_csv(save_to)
    print("Successfully saved the file with calculated weekly stats for products only")

def add_week_numbers(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    df.rename(columns={'item_id':'asin'}, inplace=True)
    weeks = list(set(df['week'].values))
    weeks.sort()
    nums = list(range(len(weeks)))
    week_dict = dict(zip(weeks,nums))
    df['week_num'] = df['week'].apply(lambda x: week_dict[x])
    df.to_csv(save_to)
    print("Successfully saved the file with week numbers")

if __name__ == "__main__":
    """
    Use case
    """
    #q = []
    #q.append(('../data/merged_Cell_Phones_&_Accessories.csv', 'Cell_Phones_and_Accessories'))
    #q.append(('../data/merged_Tools_&_Home_Improvement.csv', 'Tools_and_Home_Improvement'))

    reviews_dataset = '../data/Processed_Julian_Amazon_data/did/reviews_mcauley_description_full.csv' #'../data/merged_McAuley.csv' #'mcauley_top10_numeric.csv'
    products_dataset = '../data/Processed_Julian_Amazon_data/did/products_mcauley_description_full.csv' #'../data/merged_McAuley_weekly.csv'
    get_selected_data(q, 'reviews_mcauley_description.csv')
    get_weekly_stats('reviews_mcauley_description.csv', reviews_dataset)
    get_products_data(reviews_dataset, products_dataset)
    add_week_numbers(reviews_dataset, reviews_dataset)
    add_week_numbers(products_dataset, products_dataset)


