import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import reduce

from product_analysis import get_reviewTime_dataframe

'''
Perform statistical analysis based on product-week level

'''
def get_word_count_threshold(fp, verbose=True):
	'''
	Get threshold from pre-treatment data for each product
	:param fp: file path to read from
	'''
	df = pd.read_csv(fp, low_memory=False)
	df = df[df['reviewTime'] < '2016-10-03']

	groups = df.groupby(['asin'])

	review_counts = groups['reviewTime'].count()
	df_counts = review_counts.to_frame().reset_index().rename(columns={'reviewTime':'total_review_count'})
	if verbose:
		print("Successfully computed total review count for each product")

	df_length = groups['word_count'].mean()
	df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count_product'})
	if verbose:
		print("Successfully computed average word count for each product")

	df_length_std = groups['word_count'].std()
	df_length_std = df_length_std.to_frame().reset_index().rename(columns={'word_count':'std_word_count_product'})
	if verbose:
		print("Successfully computed standar deviation of word count for each product")

	dfs = [df_counts, df_length, df_length_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)
	if verbose:
		print("Successfully merged product-level statistics computed above")

	df_stats['threshold_word_count_product'] = df_stats['avg_word_count_product'] + 2*df_stats['std_word_count_product']
	if verbose:
		print(df_stats.head())

	return df_stats

def get_burstiness_threshold(fp, verbose=True):
	'''
	Get burstiness threshold for each product using pre-treatment data
	:param fp: file path to read from
	:param products_stats: product-level stats to get product life length
	'''
	df = pd.read_csv(fp, low_memory=False)
	df = df[df['reviewTime'] < '2016-10-03']

	# Get product daily review count to compute burstiness
	groups = get_product_daily_review_n(df).groupby(['asin'])

	df_product_mean = groups['daily_review_count_product'].mean()
	df_product_mean = df_product_mean.to_frame().reset_index().rename(columns={'daily_review_count_product':'avg_review_count_product'})
	if verbose:
		print("Successfully computed avg review count for each product")

	df_product_std = groups['daily_review_count_product'].std()
	df_product_std = df_product_std.to_frame().reset_index().rename(columns={'daily_review_count_product':'std_review_count_product'})
	if verbose:
		print("Successfully computed review count std for each product")

	dfs = [df_product_mean, df_product_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)
	if verbose:
		print("Successfully merged statistics computed above")

	df_stats['threshold_review_count_product'] = df_stats['avg_review_count_product'] + 2*df_stats['std_review_count_product']
	if verbose:
		print(df_stats.head())

	return df_stats

def get_product_daily_review_n(df, verbose=True):
	'''
	Get product daily review count
	:param df: dataframe
	'''
	groups = df.groupby(['asin','reviewTime'])

	df_counts = groups['overall'].count()
	df_counts = df_counts.to_frame().reset_index().rename(columns={'overall':'daily_review_count_product'})
	if verbose:
		print("Successfully computed daily review count for each product")

	print(df_counts.head())
	df_reviewTime = get_reviewTime_dataframe(products_stats)
	print(df_reviewTime.head())
	df_counts = pd.merge(df_counts, df_reviewTime, on=['asin','reviewTime'], how='outer')
	df_counts.fillna(value=0, inplace=True)

	return df_counts

def get_product_week_stats(fp, verbose=True):
	'''
	:param fp: file path to read from
	'''
	df = pd.read_csv(fp, low_memory=False)
	df = pd.merge(df, get_word_count_threshold(fp), on='asin')
	df = pd.merge(df, get_burstiness_threshold(fp), on='asin')

	product_daily_review_n = get_product_daily_review_n(df)

	df['word_count_2std_product'] = np.where(df['word_count'] > df['threshold_word_count_product'], 1, 0)
	df['word_count_2std_product'] = np.where(df['word_count'] > df['threshold_word_count_product'], 1, 0)

	groups = df.groupby(['asin','week'])

