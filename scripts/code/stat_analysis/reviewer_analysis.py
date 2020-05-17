import sys
#sys.path.append('..')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import reduce
from utils import COLS, NON_TEXT
from data_processing import get_int, get_image_count, handle_price, nltk_polarity

'''
Perform statistical analysis based on reviewers' characteristics

'''

def get_reviewers(fp, category='Office Products'):
	'''
	Get reviewerIDs in a given dataset
	:param fp: the dataset
	:return: a list of reviewerIDs
	'''
	df = pd.read_csv(fp, low_memory=False, index_col=0)
	#sub_df = df.loc[df['category'] == category]
	reviewerIDs = list(set(df.reviewerID))
	return reviewerIDs

def get_reviews_from_list(p, reviewerIDs, save_to, verbose=True):
	'''
	Get all reviews posted by reviewers in the given list
	:param p: a list of tuples
	:param reviewerIDs: a list of reviewerIDs
	:param save_to: the file path saving the reviews to
	'''
	dfs = []
	for i in p:
		ORIGINAL_DATASET = i[0]
		DATASET_NAME = i[1]

		df = pd.read_csv(ORIGINAL_DATASET, low_memory=False, index_col=0)
		sub_reviews = df.loc[df['reviewerID'].isin(reviewerIDs)]
		sub_reviews.drop_duplicates(keep='first',inplace=True)
		dfs.append(sub_reviews)

		if verbose:
			print("Successfully get reviews for category: {}".format(DATASET_NAME))

	df_merged = pd.concat(dfs, ignore_index=True)
	print(df_merged.loc[0:4, 'overall'])
	print(df_merged.columns)
	df_merged = df_merged.loc[:, COLS]
	df_merged.to_csv(save_to, index=False)
	print("Successfully saved the merged file")

def process_reviews(fp, save_to, verbose=True):
	'''
	Process the dataset
	:param fp: file path of the dataset that needs to be processed
	:param save_to: the file path saving the reviews to
	'''
	df = pd.read_csv(fp, low_memory=False)
	df['overall'] = df['overall'].apply(get_int)
	df['vote'] = df['vote'].apply(get_int)
	df['reviewTime'] = df['reviewTime'].apply(lambda x: str(datetime.strptime(x, '%m %d, %Y').date()))
	df['word_count'] = df['reviewText'].apply(lambda x: len(str(x)))
	df['sentiment'] = df['reviewText'].apply(nltk_polarity)
	df['image'] = df['image'].apply(get_image_count)
	df['category'] = df['category'].apply(lambda x: x.strip('][').strip('\''))
	df['price'] = df['price'].apply(handle_price)

	if verbose:
		print(df.columns)

	df = df.loc[:, NON_TEXT]
	df.to_csv(save_to, index=False)

	if verbose:
		print("Successfully saved the processed reviews")

def get_reviewer_stats(fp, save_to, verbose=True):
	'''
	Get stats for each reviewer
	:param fp: file path to read from
	:param save_to: the file path saved to
	'''
	df = pd.read_csv(fp, low_memory=False)
	#df['week'] = df['reviewTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') - timedelta(days=datetime.strptime(x, '%Y-%m-%d').weekday()))
	groups = df.groupby(['reviewerID'])

	review_counts = groups['reviewTime'].count()
	df_counts = review_counts.to_frame().reset_index().rename(columns={'reviewTime':'total_review_count'})
	if verbose:
		print("Successfully computed total review count for each reviewer")

	days = groups['reviewTime'].nunique()
	df_days = days.to_frame().reset_index().rename(columns={'reviewTime':'day_count'})
	if verbose:
		print("Successfully computed day count for each reviewer")

	brands = groups['brand'].nunique()
	df_brands = brands.to_frame().reset_index().rename(columns={'brand':'brand_count'})
	if verbose:
		print("Successfully computed brand count for each reviewer")

	df_ratings = groups['overall'].mean()
	df_ratings = df_ratings.to_frame().reset_index().rename(columns={'overall':'avg_rating'})
	if verbose:
		print("Successfully computed average rating for each reviewer")

	df_sentiment = groups['sentiment'].mean()
	df_sentiment = df_sentiment.to_frame().reset_index().rename(columns={'sentiment':'avg_sentiment'})
	if verbose:
		print("Successfully computed average sentiment for each reviewer")

	df_length = groups['word_count'].mean()
	df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count'})
	if verbose:
		print("Successfully computed average word count for each reviewer")

	df_helpfulness = groups['vote'].mean()
	df_helpfulness = df_helpfulness.to_frame().reset_index().rename(columns={'vote':'avg_vote'})
	if verbose:
		print("Successfully computed average vote count for each reviewer")

	df_images = groups['image'].mean()
	df_images = df_images.to_frame().reset_index().rename(columns={'image':'avg_images'})
	if verbose:
		print("Successfully computed average image count for each reviewer")

	dfs = [df_counts, df_days, df_brands, df_ratings, df_sentiment, df_length, df_helpfulness, df_images]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on = 'reviewerID'), dfs)
	if verbose:
		print("Successfully merged statistics computed above")

	df_stats['burstiness'] = df_stats['total_review_count']/df_stats['day_count']
	df_stats['repeated_brands'] = df_stats['total_review_count']/df_stats['brand_count']

	df_stats.to_csv(save_to)
	if verbose:
		print("Successfully saved reviewer statistics to {}".format(save_to))

if __name__ == "__main__":
    """
    Use case
    """
    DIR_PATH = '../data/Processed_Julian_Amazon_data'

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

    #fp = DIR_PATH+'/did/reviews_mcauley_description_office_patio.csv'
    fp = '../data/merged_Office_Products.csv'
    reviews_w_text = DIR_PATH+'/stat_analysis/office_reviews.csv'
    reviews_numeric = DIR_PATH+'/stat_analysis/office_reviews_numeric.csv'
    reviewer_stats = DIR_PATH+'/stat_analysis/office_reviewer_stats.csv'

    reviewerIDs = get_reviewers(fp)
    get_reviews_from_list(q, reviewerIDs, reviews_w_text)
    process_reviews(reviews_w_text, reviews_numeric)
    get_reviewer_stats(reviews_numeric, reviewer_stats)

