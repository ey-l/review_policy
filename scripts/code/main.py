# Set path
import sys
#sys.path.append('/stat_analysis')

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

import csv
import time

# Script
#from product_matching import tag_incentivized 
from reviewer_analysis import get_reviews_from_list, get_reviewers, process_reviews, get_reviewer_stats


DIR_PATH = '../data/Processed_Julian_Amazon_data'

if __name__ == "__main__":
    """
    Use case
    """
    q = []

    q.append(('../data/merged_Cell_Phones_&_Accessories.csv', 'Cell_Phones_and_Accessories'))
    q.append(('../data/merged_Tools_&_Home_Improvement.csv', 'Tools_and_Home_Improvement'))
    q.append(('../data/merged_Home_&_Kitchen.csv', 'Home_and_Kitchen'))
    q.append(('../data/merged_Electronics.csv', 'Electronics'))
    q.append(('../data/merged_Office_Products.csv', 'Office_Products'))
    q.append(('../data/merged_Sports_&_Outdoors.csv', 'Sports_and_Outdoors'))
    q.append(('../data/merged_Patio,_Lawn_&_Garden.csv', 'Patio_Lawn_and_Garden'))
    q.append(('../data/merged_Pet_Supplies.csv', 'Pet_Supplies'))
    q.append(('../data/merged_Clothing,_Shoes_&_Jewelry.csv', 'Clothing_Shoes_and_Jewelry'))
    q.append(('../data/merged_Automotive.csv' ,'Automotive'))
    #q.append(('../data/merged_Video_Games.csv'))
    #q.append(('../data/merged_AMAZON_FASHION.csv'))
    #q.append(('../data/merged_Appliances.csv', 'Appliances', '../data/Processed_Julian_Amazon_data/doc2vec/Appliances_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Appliances_similar_reviews.csv'))
    #q.append(('../data/merged_Industrial_and_Scientific.csv'))

    fp = DIR_PATH+'/did/reviews_mcauley_description_office_patio.csv'
    reviews_w_text = DIR_PATH+'/stat_analysis/office_reviews.csv'
    reviews_numeric = DIR_PATH+'/stat_analysis/office_reviews_numeric.csv'
    reviewer_stats = DIR_PATH+'/stat_analysis/office_reviewer_stats.csv'
    #reviewerIDs = get_reviewers(fp)
    #get_reviews_from_list(q, reviewerIDs, reviews_w_text)
    #process_reviews(reviews_w_text, reviews_numeric)
    get_reviewer_stats(reviews_numeric, reviewer_stats)

