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

	# For each product
	groups = df.groupby(['asin'])

	# Computed total review count
	review_counts = groups['reviewTime'].count()
	df_counts = review_counts.to_frame().reset_index().rename(columns={'reviewTime':'total_review_count_before_ban'})

	# Computed average word count
	df_length = groups['word_count'].mean()
	df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count_product'})

	# Computed standar deviation of word count
	df_length_std = groups['word_count'].std()
	df_length_std = df_length_std.to_frame().reset_index().rename(columns={'word_count':'std_word_count_product'})

	# Merged product-level statistics computed
	dfs = [df_counts, df_length, df_length_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)

	df_stats['threshold_word_count_product'] = df_stats['avg_word_count_product'] + 2*df_stats['std_word_count_product']
	if verbose:
		print("Successfully merged product-level statistics computed above")
		print(df_stats.head())

	return df_stats

def get_burstiness_threshold(fp, products_stats, verbose=True):
	'''
	Get burstiness threshold for each product using pre-treatment data
	:param fp: file path to read from
	:param products_stats: product-level stats to get product life length
	'''
	df = pd.read_csv(fp, low_memory=False)
	df = df[df['reviewTime'] < '2016-10-03']

	# Get product daily review count to compute burstiness, group by product
	groups = get_product_daily_review_n(df, products_stats).groupby(['asin'])

	# Computed avg review count
	df_product_mean = groups['daily_review_count_product'].mean()
	df_product_mean = df_product_mean.to_frame().reset_index().rename(columns={'daily_review_count_product':'avg_review_count_product'})

	# Computed review count std
	df_product_std = groups['daily_review_count_product'].std()
	df_product_std = df_product_std.to_frame().reset_index().rename(columns={'daily_review_count_product':'std_review_count_product'})

	# Merged statistics computed 
	dfs = [df_product_mean, df_product_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)

	# Compute threshold
	df_stats['threshold_review_count_product'] = df_stats['avg_review_count_product'] + 2*df_stats['std_review_count_product']
	if verbose:
		print("Successfully merged statistics computed above")
		print(df_stats.head())

	return df_stats

def get_product_daily_review_n(df, products_stats, verbose=True):
	'''
	Get product daily review count
	:param df: dataframe
	'''
	groups = df.groupby(['asin','reviewTime'])

	df_counts = groups['overall'].count()
	df_counts = df_counts.to_frame().reset_index().rename(columns={'overall':'daily_review_count_product'})
	df_counts['week'] = df_counts['reviewTime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d') - timedelta(days=datetime.strptime(x, '%Y-%m-%d').weekday()))

	#df_reviewTime = get_reviewTime_dataframe(products_stats)
	#df_counts = pd.merge(df_counts, df_reviewTime, on=['asin','reviewTime'], how='outer')
	#df_counts.fillna(value=0, inplace=True)
	if verbose:
		print("Successfully computed daily review count for each product and outer joined with reviewTime_dataframe")
	
	return df_counts

def get_product_week_stats(fp, products_stats, save_to, verbose=True):
	'''
	:param fp: file path to read from
	'''
	df = pd.read_csv(fp, low_memory=False)
	word_count_threshold = get_word_count_threshold(fp)
	df = pd.merge(df, word_count_threshold, on='asin')
	df['word_count_2std_product'] = np.where(df['word_count'] > df['threshold_word_count_product'], 1, 0)
	
	groups = df.groupby(['asin','week','category'])
	# Computed total review count
	review_counts = groups['reviewTime'].count()
	review_counts = review_counts.to_frame().reset_index().rename(columns={'reviewTime':'weekly_review_count'})

	# Compute number of reviews exceed the word count threshold
	df_word_count = groups['word_count_2std_product'].sum()
	df_word_count = df_word_count.to_frame().reset_index().rename(columns={'word_count_2std_product':'word_count_2std_n_product'})
	df_word_count = pd.merge(df_word_count, word_count_threshold, on=['asin'])

	product_daily_review_n = get_product_daily_review_n(df, products_stats)
	burstiness_threshold = get_burstiness_threshold(fp, products_stats)
	product_daily_review_n = pd.merge(product_daily_review_n, burstiness_threshold, on='asin')
	product_daily_review_n['review_count_2std_product'] = np.where(product_daily_review_n['daily_review_count_product'] > product_daily_review_n['threshold_review_count_product'], 1, 0)

	# Compute number of reviews exceed the burstiness threshold
	groups = product_daily_review_n.groupby(['asin','week'])
	df_burstiness = groups['review_count_2std_product'].sum()
	df_burstiness = df_burstiness.to_frame().reset_index().rename(columns={'review_count_2std_product':'review_count_2std_n_product'})
	df_burstiness = pd.merge(df_burstiness, burstiness_threshold, on=['asin'])

	# Merged statistics computed 
	df_word_count.week = pd.to_datetime(df_word_count.week)
	df_burstiness.week = pd.to_datetime(df_burstiness.week)
	review_counts.week = pd.to_datetime(review_counts.week)
	dfs = [df_word_count, df_burstiness, review_counts]
	result = reduce(lambda x, y: pd.merge(x, y, on=['asin','week']), dfs)
	result.drop_duplicates(keep='first', inplace=True)

	# Compute proportion of reviews exceed the word count threshold
	result['word_count_2std_prop_product'] = result['word_count_2std_n_product']/result['weekly_review_count']
	result['review_count_2std_prop_product'] = result['review_count_2std_n_product']/result['weekly_review_count']

	# Merge total review count and product category
	groups = result.groupby(['asin'])
	review_counts = groups['weekly_review_count'].sum()
	review_counts = review_counts.to_frame().reset_index().rename(columns={'weekly_review_count':'total_review_count'})
	dfs = [result, review_counts]
	result = reduce(lambda x, y: pd.merge(x, y, on=['asin']), dfs)

	result.to_csv(save_to, index=False)
	if verbose:
		print("Successfully saved product-week statistics to {}".format(save_to))

