# Import libraries
import csv
import time
import json
import pandas as pd
import gzip
import math
from datetime import datetime

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

# Our script
#import get_incent_reviews

def get_duplicates(paths):
    df_path = paths[0]
    dataset = paths[1]
    vectors = paths[2]
    similar_df = paths[3]
	
    # Read the merged review file
    reviews = pd.read_csv(df_path, index_col=0, low_memory=False)
    reviews = reviews[reviews['title'].map(str).map(len) < 1000]

    # Remove asin with less than 10 reviews
    reviews['review_count'] = reviews.groupby('asin')['asin'].transform('count') # Count reviews/asin
    reviews = reviews.loc[reviews['review_count'] > 10]
	
    print('There are '+str(reviews.shape[0])+' reviews in the original dataset.')

    # dropping duplicate values 
    reviews.drop_duplicates(keep=False,inplace=True)
    print('There are '+str(reviews.shape[0])+' reviews after removing duplicates.')

# main script
q = []

# Already in
#q.append(('../data/merged_Cell_Phones_&_Accessories.csv', 'Cell_Phones_and_Accessories', '../data/Processed_Julian_Amazon_data/doc2vec/Cell_Phones_and_Accessories_doc2vec.csv'))

# Pending
#q.append(('../data/merged_Tools_&_Home_Improvement.csv', 'Tools_and_Home_Improvement', '../data/Processed_Julian_Amazon_data/doc2vec/Tools_and_Home_Improvement_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Tools_and_Home_Improvement_similar_reviews.csv'))
#q.append(('../data/merged_Home_&_Kitchen.csv', 'Home_and_Kitchen', '../data/Processed_Julian_Amazon_data/doc2vec/Home_and_Kitchen_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Home_and_Kitchen_10_similar_reviews.csv'))
#q.append(('../data/merged_Electronics.csv', 'Electronics', '../data/Processed_Julian_Amazon_data/doc2vec/Electronics_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Electronics_10_similar_reviews.csv'))
#q.append(('../data/merged_Office_Products.csv', 'Office_Products', '../data/Processed_Julian_Amazon_data/doc2vec/Office_Products_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Office_Products_similar_reviews.csv'))
#q.append(('../data/merged_Sports_&_Outdoors.csv', 'Sports_and_Outdoors', '../data/Processed_Julian_Amazon_data/doc2vec/Sports_and_Outdoors_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Sports_and_Outdoors_similar_reviews.csv'))
q.append(('../data/merged_Patio,_Lawn_&_Garden.csv', 'Patio_Lawn_and_Garden', '../data/Processed_Julian_Amazon_data/doc2vec/Patio_Lawn_and_Garden_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Patio_Lawn_and_Garden_similar_reviews.csv'))
#q.append(('../data/merged_Pet_Supplies.csv', 'Pet_Supplies', '../data/Processed_Julian_Amazon_data/doc2vec/Pet_Supplies_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Pet_Supplies_similar_reviews.csv'))
#q.append(('../data/merged_Automotive.csv' ,'Automotive', '../data/Processed_Julian_Amazon_data/doc2vec/Automotive_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Automotive_similar_reviews.csv'))
#q.append(('../data/merged_Clothing,_Shoes_&_Jewelry.csv', 'Clothing_Shoes_and_Jewelry', '../data/Processed_Julian_Amazon_data/doc2vec/Clothing_Shoes_and_Jewelry_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Clothing_Shoes_and_Jewelry_similar_reviews.csv'))
#q.append(('../data/merged_Video_Games.csv'))
#q.append(('../data/merged_AMAZON_FASHION.csv'))
#q.append(('../data/merged_Appliances.csv', 'Appliances', '../data/Processed_Julian_Amazon_data/doc2vec/Appliances_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Appliances_similar_reviews.csv'))
#q.append(('../data/merged_Industrial_and_Scientific.csv'))

for i in q:
	get_duplicates(i)
