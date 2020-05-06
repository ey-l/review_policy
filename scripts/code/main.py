import csv
import time

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

# Our script
from product_matching import tag_incentivized 

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

    for i in q:
        tag_incentivized(i)
