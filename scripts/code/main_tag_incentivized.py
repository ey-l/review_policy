import csv
import time

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')

# Our script
import get_incent_reviews

DIR_PATH = '../data/Processed_Julian_Amazon_data'

def tag_incentivized(paths):
    df_path = paths[0]
    dataset = paths[1]

    vectors = DIR_PATH+'/doc2vec/'+dataset+'_description.csv'
    similar_df = DIR_PATH+'/sim_reviews/'+dataset+'_10_similar_reviews.csv'
    tagged_path = DIR_PATH+'/tagged/'+dataset+'_merged_reviews_tagged.csv'
	
    #get_incent_reviews.get_doc2vec(dataset, df_path)
    get_incent_reviews.get_similar_products(dataset, df_path, vectors, 10)
    #get_incent_reviews.tag_incentive(dataset, similar_df)
    #get_incent_reviews.tag_incentive_ngrams(dataset, tagged_path)
	

# main script
q = []

# Already in
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
