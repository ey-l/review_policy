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
from functools import reduce

from utils import COLS, COLS_SIM, NON_TEXT, NON_TEXT

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

def get_numeric_columns(paths, save_to, verbose=True):
    df_list = []
    for i in paths:
        ORIGINAL_DATASET = i[0]
        DATASET_NAME = i[1]
        TOP10_SIMILAR = '../data/Processed_Julian_Amazon_data/sim_reviews/'+DATASET_NAME+'_10_similar_reviews.csv'
	
        # Get selected data columns
        df = pd.read_csv(TOP10_SIMILAR, low_memory=False)
        #df = pd.read_csv(ORIGINAL_DATASET, index_col=0, low_memory=False)
        df = df.loc[:,COLS]
        #df = df.loc[:,COLS_SIM]
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
    #df_merged = df_merged.loc[:, NON_TEXT_SIM]
    df_merged = df_merged.loc[:, NON_TEXT]
    df_merged.to_csv(save_to, index=False)
    print("Successfully saved the merged file")

def get_selected_columns(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    #df = df.loc[:, NON_TEXT_SIM]
    df = df.loc[:, NON_TEXT]
    print(df.shape[0])
    df.to_csv(save_to, index=False)
    print("Successfully saved the file with selected columns")

def get_weekly_stats(file_path, save_to, verbose=True):
    df = pd.read_csv(file_path, index_col=0, low_memory=False)
    df['week'] = df['reviewTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') - timedelta(days=datetime.strptime(x, '%Y-%m-%d').weekday()))
    df['is_5_stars'] = np.where(df['overall'] == 5, 1, 0)
    groups = df.groupby(['asin','week'])
    #groups = df.groupby(['asin','week'], as_index=False)
    #cols = ['asin','week','avg_rating','weekly_review_count','avg_word_count','avg_sentiment','avg_vote','avg_image']

    review_counts = groups['reviewTime'].count()
    df_counts = review_counts.to_frame().reset_index().rename(columns={'reviewTime':'weekly_review_count'})
    if verbose:
        print("Successfully computed weekly_review_count for each reviewer by week")

    df_ratings = groups['overall'].mean()
    df_ratings = df_ratings.to_frame().reset_index().rename(columns={'overall':'avg_rating'})
    if verbose:
        print("Successfully computed avg_rating for each reviewer by week")

    df_length = groups['word_count'].mean()
    df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count'})
    if verbose:
        print("Successfully computed avg_word_count for each reviewer by week")

    df_helpfulness = groups['vote'].mean()
    df_helpfulness = df_helpfulness.to_frame().reset_index().rename(columns={'vote':'avg_vote'})
    if verbose:
        print("Successfully computed avg_vote for each reviewer by week")

    df_sentiment = groups['sentiment'].mean()
    df_sentiment = df_sentiment.to_frame().reset_index().rename(columns={'sentiment':'avg_sentiment'})
    if verbose:
        print("Successfully computed avg_sentiment for each reviewer by week")

    df_images = groups['image'].mean()
    df_images = df_images.to_frame().reset_index().rename(columns={'image':'avg_image'})
    if verbose:
        print("Successfully computed avg_image for each reviewer by week")

    df_votes = groups['vote'].mean()
    df_votes = df_votes.to_frame().reset_index().rename(columns={'vote':'weekly_vote_count'})
    if verbose:
        print("Successfully computed weekly_vote_count for each reviewer by week")

    groups = df.groupby(['asin','week', 'is_5_stars'])

    df_votes_split = groups['vote'].mean()
    df_votes_split = df_votes_split.to_frame().reset_index().rename(columns={'vote':'avg_vote'})
    df_votes_split.set_index(['asin','week','is_5_stars'], inplace=True)
    df_votes_split = df_votes_split.unstack()
    df_votes_split.columns = df_votes_split.columns.droplevel()
    df_votes_split.reset_index(inplace=True)
    df_votes_split.columns = ['asin','week','non_5_stars','5_stars']
    df_votes_split.fillna(value=0, inplace=True)
    if verbose:
        print("Successfully computed avg_vote for each reviewer by week")

    dfs = [df_counts, df_ratings, df_sentiment, df_length, df_helpfulness, df_images, df_votes]
    df_stats = reduce(lambda x, y: pd.merge(x, y, on=['asin','week']), dfs)
    if verbose:
        print("Successfully merged statistics computed above")

    df = pd.merge(df, df_stats, on=['asin','week'])
    df = pd.merge(df, df_votes_split, on=['asin','week'])
    df.to_csv(save_to, index=False)
    print("Successfully saved the file with calculated weekly stats")

def get_products_data(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    df_cols = ['asin','week','category','brand','price','main_cat','sim1','amazon','avg_rating','weekly_review_count','avg_word_count','avg_sentiment','avg_vote','avg_image','weekly_vote_count','non_5_stars','5_stars']
    df_products = df[df_cols]
    df_products.drop_duplicates(keep='first',inplace=True)
    df_products.to_csv(save_to, index=False)
    print("Successfully saved the file with calculated weekly stats for products only")

def add_week_numbers(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    df.rename(columns={'item_id':'asin'}, inplace=True)
    weeks = list(set(df['week'].values))
    weeks.sort()
    nums = list(range(len(weeks)))
    week_dict = dict(zip(weeks,nums))
    df['week_num'] = df['week'].apply(lambda x: week_dict[x])
    df.to_csv(save_to, index=False)
    print("Successfully saved the file with week numbers")

if __name__ == "__main__":
    """
    Use case
    """
    q = []
    #q.append(('../data/merged_Cell_Phones_&_Accessories.csv', 'Cell_Phones_and_Accessories'))
    #q.append(('../data/merged_Tools_&_Home_Improvement.csv', 'Tools_and_Home_Improvement'))
    q.append(('../data/merged_Office_Products.csv', 'Office_Products'))

    reviews_dataset = '../data/Processed_Julian_Amazon_data/did/reviews_mcauley_office_full.csv' #'../data/merged_McAuley.csv' #'mcauley_top10_numeric.csv'
    products_dataset = '../data/Processed_Julian_Amazon_data/did/products_mcauley_office_full.csv' #'../data/merged_McAuley_weekly.csv'
    get_numeric_columns(q, 'reviews_mcauley_office_full.csv')
    get_weekly_stats('reviews_mcauley_office_full.csv', reviews_dataset)
    #get_products_data(reviews_dataset, products_dataset)
    add_week_numbers(reviews_dataset, reviews_dataset)
    #add_week_numbers(products_dataset, products_dataset)


