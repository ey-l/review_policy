import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from functools import reduce
from utils import COLS, NON_TEXT

'''
Perform statistical analysis based on products' characteristics

'''

def get_products_stats(fp, save_to, verbose=True):
	'''
	Get stats for each product
	:param fp: file path to read from
	:param save_to: the file path saved to
	'''
	df = pd.read_csv(fp, low_memory=False)
	groups = df.groupby(['asin'])

	review_counts = groups['reviewTime'].count()
	df_counts = review_counts.to_frame().reset_index().rename(columns={'reviewTime':'total_review_count'})
	if verbose:
		print("Successfully computed total review count for each product")

	days = groups['reviewTime'].nunique()
	df_days = days.to_frame().reset_index().rename(columns={'reviewTime':'day_count'})
	if verbose:
		print("Successfully computed day count for each product")

	df_length = groups['word_count'].mean()
	df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count_product'})
	if verbose:
		print("Successfully computed average word count for each product")

	df_length_std = groups['word_count'].std()
	df_length_std = df_length_std.to_frame().reset_index().rename(columns={'word_count':'std_word_count_product'})
	if verbose:
		print("Successfully computed standar deviation of word count for each product")

	dfs = [df_counts, df_days, df_length, df_length_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)
	if verbose:
		print("Successfully merged statistics computed above")

	df_merged = pd.merge(df, df_stats, on='asin')
	print(df_merged.columns)
	df_merged['threshold_word_count_product'] = df_merged['avg_word_count_product'] + 2*df_merged['std_word_count_product']
	df_merged['word_count_2std_product'] = np.where(df_merged['word_count'] > df_merged['threshold_word_count_product'], 1, 0)
	df_merged['avg_word_count_category'] = df_merged['word_count'].mean()
	df_merged['std_word_count_category'] = df_merged['word_count'].std()

	groups = df_merged.groupby(['asin'])

	df_length_2std = groups['word_count_2std_product'].sum()
	df_length_2std = df_length_2std.to_frame().reset_index().rename(columns={'word_count_2std_product':'word_count_2std_n_product'})
	if verbose:
		print("Successfully counted reviews that exceed 2std threshold for each product")

	df_stats = pd.merge(df_stats, df_length_2std, on='asin')
	print(df_stats.columns)
	df_stats['word_count_2std_prop_product'] = df_stats['word_count_2std_n_product']/df_stats['total_review_count']

	df_stats.to_csv(save_to, index=False)
	if verbose:
		print("Successfully saved product statistics to {}".format(save_to))

def get_burstiness_stats(fp, save_to, verbose=True):
	df = pd.read_csv(fp, low_memory=False)
	groups = df.groupby(['asin','reviewTime'])

	df_counts = groups['overall'].count()
	df_counts = df_counts.to_frame().reset_index().rename(columns={'overall':'daily_review_count'})
	if verbose:
		print("Successfully computed daily review count for each product")

	df_counts['avg_daily_review_count_category'] = df_counts['daily_review_count'].mean()
	df_counts['std_daily_review_count_category'] = df_counts['daily_review_count'].std()
	df_counts['threshold_daily_review_count_category'] = df_counts['avg_daily_review_count_category'] + 2*df_counts['std_daily_review_count_category']
	df_counts['daily_review_count_2std_category'] = np.where(df_counts['daily_review_count'] > df_counts['threshold_daily_review_count_category'], 1, 0)

	groups = df_counts.groupby(['asin'])

	df_category_2std = groups['daily_review_count_2std_category'].sum()
	df_category_2std = df_category_2std.to_frame().reset_index().rename(columns={'daily_review_count_2std_category':'review_count_2std_n_category'})
	if verbose:
		print("Successfully counted reviews that exceed 2std threshold for each product")

	df_product_mean = groups['daily_review_count'].mean()
	df_product_mean = df_product_mean.to_frame().reset_index().rename(columns={'daily_review_count':'avg_review_count_product'})
	if verbose:
		print("Successfully computed avg review count for each product")

	df_product_std = groups['daily_review_count'].std()
	df_product_std = df_product_std.to_frame().reset_index().rename(columns={'daily_review_count':'std_review_count_product'})
	if verbose:
		print("Successfully computed review count std for each product")

	dfs = [df_category_2std, df_product_mean, df_product_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)
	if verbose:
		print("Successfully merged statistics computed above")

	df_merged = pd.merge(df_counts, df_stats, on='asin')
	df_merged = pd.merge(df, df_merged, on=['asin','reviewTime'])

	df_merged['threshold_review_count_product'] = df_merged['avg_review_count_product'] + 2*df_merged['std_review_count_product']
	df_merged['review_count_2std_product'] = np.where(df_merged['daily_review_count'] > df_merged['threshold_review_count_product'], 1, 0)

	groups = df_merged.groupby(['asin'])

	df_product_2std = groups['review_count_2std_product'].sum()
	df_product_2std = df_product_2std.to_frame().reset_index().rename(columns={'review_count_2std_product':'review_count_2std_n_product'})
	if verbose:
		print("Successfully counted reviews that exceed 2std threshold for each product")

	df_stats = pd.merge(df_merged, df_product_2std, on='asin')
	print(df_stats.columns)
	cols = ['asin','avg_daily_review_count_category', 'std_daily_review_count_category','threshold_daily_review_count_category',
		'review_count_2std_n_category','avg_review_count_product', 
		'std_review_count_product','threshold_review_count_product', 'review_count_2std_n_product']
	df_stats = df_stats[cols].drop_duplicates(keep='first')
	df_stats.to_csv(save_to, index=False)
	if verbose:
		print("Successfully saved product statistics to {}".format(save_to))


def get_category_stats(fp, save_to, verbose=True):
	'''
	Get stats for each category
	:param fp: file path to read from
	:param save_to: the file path saved to
	'''
	df = pd.read_csv(fp, low_memory=False)
	groups = df.groupby(['category'])

	df_length = groups['word_count'].mean()
	df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count_category'})
	if verbose:
		print("Successfully computed average word count for each category")

	df_length_std = groups['word_count'].std()
	df_length_std = df_length_std.to_frame().reset_index().rename(columns={'word_count':'std_word_count_category'})
	if verbose:
		print("Successfully computed standar deviation of word count for each category")

