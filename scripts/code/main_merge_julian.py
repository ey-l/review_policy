# Import libraries
import csv
import time
import json
import pandas as pd
import numpy as np
import gzip
import math
from datetime import datetime, timedelta

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

COLS = ['X','overall','vote', 'verified', 'reviewTime', 'reviewerID', 'asin', 'reviewerName',
       'reviewText', 'summary', 'unixReviewTime', 'image', 'category',
       'description', 'title', 'brand', 'rank', 'price', 'fit', 'main_cat',
       'tech2', 'amazon', 'sim1']

NON_TEXT = ['X','overall', 'vote', 'verified', 'reviewTime', 'reviewerID', 'asin', 'word_count',
            'image', 'category', 'brand', 'price', 'main_cat', 'amazon', 'sim1'] #, 'sim1'

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
        #TOP10_SIMILAR = '../data/Processed_Julian_Amazon_data/sim_reviews/'+DATASET_NAME+'_10_similar_reviews.csv'
	
        # Get selected data columns
        df = pd.read_csv(ORIGINAL_DATASET, index_col=0, low_memory=False)
        df = df.loc[:,COLS]
        df['overall'] = df['overall'].apply(get_int)
        df['vote'] = df['vote'].apply(get_int)
        df['reviewTime'] = df['reviewTime'].apply(lambda x: str(datetime.strptime(x, '%m %d, %Y').date()))
        df['word_count'] = df['reviewText'].apply(lambda x: len(str(x)))
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
    df_merged = df_merged.loc[:, NON_TEXT]
    df_merged.to_csv(save_to, index=False)
    print("Successfully saved the merged file")

def get_selected_columns(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    df = df.loc[:, NON_TEXT]
    print(df.shape[0])
    df.to_csv(save_to)
    print("Successfully saved the file with selected columns")

def get_weekly_stats(file_path, save_to):
    df = pd.read_csv(file_path, index_col=0)
    df['week'] = df['reviewTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') - timedelta(days=datetime.strptime(x, '%Y-%m-%d').weekday()))
    groups = df.groupby(['asin','week'], as_index=False)
    cols = ['asin','week','avg_rating','weekly_review_count','avg_word_count','avg_vote','avg_image']
    df_weekly = pd.DataFrame(columns=cols)
    for group in groups:
        df_group = group[1]
        df_group['avg_rating'] = df_group['overall'].mean()
        df_group['avg_word_count'] = df_group['word_count'].mean()
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
    df_cols = ['asin','week','category','brand','price','main_cat','sim1','amazon','avg_rating','weekly_review_count','avg_word_count','avg_vote','avg_image']
    df_products = df[df_cols]
    df_products.drop_duplicates(keep='first',inplace=True)
    df_products.to_csv(save_to)
    print("Successfully saved the file with calculated weekly stats for products only")

def add_week_numbers(file_path, save_to):
    df = pd.read_csv(file_path, low_memory=False)
    weeks = list(set(df['week'].values))
    weeks.sort()
    nums = list(range(len(weeks)))
    week_dict = dict(zip(weeks,nums))
    df['week_num'] = df['week'].apply(lambda x: week_dict[x])
    df.to_csv(save_to)
    print("Successfully saved the file with week numbers")

# main script
q = []

#q.append(('../data/merged_Cell_Phones_&_Accessories.csv', 'Cell_Phones_and_Accessories'))
#q.append(('../data/merged_Tools_&_Home_Improvement.csv', 'Tools_and_Home_Improvement'))
#q.append(('../data/merged_Home_&_Kitchen.csv', 'Home_and_Kitchen'))
#q.append(('../data/merged_Electronics.csv', 'Electronics'))
q.append(('../data/merged_Office_Products.csv', 'Office_Products'))
#q.append(('../data/merged_Sports_&_Outdoors.csv', 'Sports_and_Outdoors'))
q.append(('../data/merged_Patio,_Lawn_&_Garden.csv', 'Patio_Lawn_and_Garden'))
#q.append(('../data/merged_Pet_Supplies.csv', 'Pet_Supplies'))
#q.append(('../data/merged_Clothing,_Shoes_&_Jewelry.csv', 'Clothing_Shoes_and_Jewelry'))
#q.append(('../data/merged_Automotive.csv' ,'Automotive'))

reviews_dataset = '../data/Processed_Julian_Amazon_data/did/reviews_mcauley_description.csv' #'../data/merged_McAuley.csv' #'mcauley_top10_numeric.csv'
products_dataset = '../data/Processed_Julian_Amazon_data/did/products_mcauley_description.csv' #'../data/merged_McAuley_weekly.csv'
#get_selected_data(q, reviews_dataset) 
#get_selected_columns(file_path, save_to)
#get_weekly_stats(reviews_dataset, reviews_dataset)
get_products_data(reviews_dataset, products_dataset)
add_week_numbers(reviews_dataset, '../data/Processed_Julian_Amazon_data/did/reviews_mcauley_description_week_num.csv')
add_week_numbers(products_dataset, products_dataset)

