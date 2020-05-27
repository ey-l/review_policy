# Set path
import sys
#sys.path.append('/stat_analysis')

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

import csv
import time
import pandas as pd

# Script
#from reviewer_analysis import get_reviews_from_list, get_reviewers, process_reviews, get_reviewer_stats
from product_analysis import get_products_stats, get_category_stats, get_product_burstiness_stats, get_category_burstiness_stats, merge_datasets
from product_matching import match_products
from data_processing import get_selected_data, get_products_data, get_weekly_stats, add_week_numbers


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
    #q.append(('../data/merged_Automotive.csv' ,'Automotive'))
    #q.append(('../data/merged_Video_Games.csv'))
    #q.append(('../data/merged_AMAZON_FASHION.csv'))
    #q.append(('../data/merged_Appliances.csv', 'Appliances', '../data/Processed_Julian_Amazon_data/doc2vec/Appliances_doc2vec.csv', '../data/Processed_Julian_Amazon_data/sim_reviews/Appliances_similar_reviews.csv'))
    #q.append(('../data/merged_Industrial_and_Scientific.csv'))

    #reviews_w_text = DIR_PATH+'/stat_analysis/office_reviews.csv'
    #reviews_numeric = DIR_PATH+'/stat_analysis/office_reviews_numeric.csv'
    reviews_dataset = DIR_PATH+'/did/reviews_mcauley_description_top10_extend.csv' 
    products_dataset = DIR_PATH+'/did/products_mcauley_description_top10_extend.csv'
    products_stats = DIR_PATH+'/stat_analysis/product_stats_top10_extend.csv'
    category_stats = DIR_PATH+'/stat_analysis/category_stats_top10_extend.csv'
    burstiness_stats = DIR_PATH+'/stat_analysis/burstiness_stats_top10_extend.csv'
    merged_stats = DIR_PATH+'/stat_analysis/products_stats_top10_extend.csv'

    #for i in q:
    #    match_products(i)

    #get_selected_data(q, reviews_dataset)
    #get_weekly_stats(reviews_dataset, products_dataset)
    #get_products_data(products_dataset, products_dataset)
    #add_week_numbers(reviews_dataset, reviews_dataset)
    #add_week_numbers(products_dataset, products_dataset)

    
    get_products_stats(reviews_dataset, products_stats)
    get_product_burstiness_stats(reviews_dataset, products_stats, burstiness_stats)
    merge_datasets(products_stats, burstiness_stats, merged_stats, 'asin')
    
    get_category_stats(reviews_dataset, category_stats)
    get_category_burstiness_stats(reviews_dataset, products_stats, burstiness_stats)
    merge_datasets(category_stats, burstiness_stats, category_stats, 'category')
    merge_datasets(category_stats, merged_stats, merged_stats, 'asin')
    

