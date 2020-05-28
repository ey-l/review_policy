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

	earlist = groups['reviewTime'].min()
	df_earlist = earlist.to_frame().reset_index().rename(columns={'reviewTime':'first_reviewTime'})
	if verbose:
		print("Successfully obtained the first reviewTime for each product")

	latest = groups['reviewTime'].max()
	df_latest = latest.to_frame().reset_index().rename(columns={'reviewTime':'last_reviewTime'})
	if verbose:
		print("Successfully obtained the last reviewTime for each product")

	df_length = groups['word_count'].mean()
	df_length = df_length.to_frame().reset_index().rename(columns={'word_count':'avg_word_count_product'})
	if verbose:
		print("Successfully computed average word count for each product")

	df_length_std = groups['word_count'].std()
	df_length_std = df_length_std.to_frame().reset_index().rename(columns={'word_count':'std_word_count_product'})
	if verbose:
		print("Successfully computed standar deviation of word count for each product")

	dfs = [df_counts, df_days, df_length, df_length_std, df_latest, df_earlist]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='asin'), dfs)
	if verbose:
		print("Successfully merged product-level statistics computed above")

	df_stats['first_reviewTime'] = pd.to_datetime(df_stats['first_reviewTime'])
	df_stats['last_reviewTime'] = pd.to_datetime(df_stats['last_reviewTime'])
	df_stats['product_life_length'] = df_stats['last_reviewTime']-df_stats['first_reviewTime']
	df_stats['product_life_length'] = df_stats['product_life_length'].apply(lambda x: x.days)

	df_merged = pd.merge(df, df_stats, on='asin')
	print(df_merged.head())
	df_merged['threshold_word_count_product'] = df_merged['avg_word_count_product'] + 2*df_merged['std_word_count_product']
	df_merged['word_count_2std_product'] = np.where(df_merged['word_count'] > df_merged['threshold_word_count_product'], 1, 0)

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

def get_reviewTime_dataframe(fp, verbose=True):
	'''
	Make a dataframe where each product has a row for every day within its product life length
	:param fp: file path to read from
	:return: return a dataframe at the product-reviewTime level
	'''
	df = pd.read_csv(fp, low_memory=False)
	df_reviewTime = [] 
	for tup in df.itertuples():
		index = pd.period_range(start=tup.first_reviewTime, end=tup.last_reviewTime, freq='D')
		new_df = pd.DataFrame([(tup.asin)] * len(index), index=index)
		new_df['reviewTime'] = new_df.index
		df_reviewTime.append(new_df)
	df_reviewTime = pd.concat(df_reviewTime, axis=0)
	df_reviewTime.columns = ['asin','reviewTime']
	if verbose:
		print("Successfully returned reviewTime records between the first and last reviews")
	return df_reviewTime

def get_product_burstiness_stats(fp, products_stats, save_to, verbose=True):
	'''
	Get burstiness stats for each product
	:param fp: file path to read from
	:param products_stats: product-level stats to get product life length
	:param save_to: the file path saved to
	'''
	df = pd.read_csv(fp, low_memory=False)
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

	groups = df_counts.groupby(['asin'])

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

	df_merged = pd.merge(df_counts, df_stats, on='asin')
	df_merged = pd.merge(df, df_merged, on=['asin','reviewTime'])

	df_merged['threshold_review_count_product'] = df_merged['avg_review_count_product'] + 2*df_merged['std_review_count_product']
	df_merged['review_count_2std_product'] = np.where(df_merged['daily_review_count_product'] > df_merged['threshold_review_count_product'], 1, 0)

	groups = df_merged.groupby(['asin'])

	df_product_2std = groups['review_count_2std_product'].sum()
	df_product_2std = df_product_2std.to_frame().reset_index().rename(columns={'review_count_2std_product':'review_count_2std_n_product'})
	if verbose:
		print("Successfully counted reviews that exceed 2std threshold for each product")

	df_stats = pd.merge(df_merged, df_product_2std, on='asin')
	print(df_stats.columns)
	cols = ['asin','avg_review_count_product', 'std_review_count_product','threshold_review_count_product', 'review_count_2std_n_product']
	df_stats = df_stats[cols].drop_duplicates(keep='first')
	df_stats.to_csv(save_to, index=False)
	if verbose:
		print("Successfully saved product statistics to {}".format(save_to))

def merge_datasets(f1, f2, save_to, onkey, verbose=True):
	'''
	Merge dataset f1 and f2
	:param f1: file path to read from
	:param f2: file path to read from
	:param save_to: the file path saved to
	'''
	products = pd.read_csv(f1, low_memory=False)
	burstiness = pd.read_csv(f2, low_memory=False)
	df = pd.merge(products, burstiness, on=onkey)
	df.to_csv(save_to, index=False)
	if verbose:
		print('Successfully saved merged data {} and {} to {}'.format(f1, f2, save_to))

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

	dfs = [df_length, df_length_std]
	df_stats = reduce(lambda x, y: pd.merge(x, y, on='category'), dfs)
	if verbose:
		print("Successfully merged category-level statistics computed above")

	df_stats['threshold_word_count_category'] = df_stats['avg_word_count_category'] + 2*df_stats['std_word_count_category']
	df_merged = pd.merge(df, df_stats, on='category')
	cols = list(df_stats.columns)
	cols.append('asin')
	df_merged = df_merged[cols].drop_duplicates(keep='first')
	df_merged.to_csv(save_to, index=False)
	if verbose:
		print("Successfully saved category statistics to {}".format(save_to))

def get_category_burstiness_stats(fp, products_stats, save_to, verbose=True):
	'''
	Get burstiness stats for each category
	:param fp: file path to read from
	:param products_stats: product-level stats to get product life length
	:param save_to: the file path saved to
	'''
	df = pd.read_csv(fp, low_memory=False)
	df_reviewTime = get_reviewTime_dataframe(products_stats)
	df = pd.merge(df, df_reviewTime, on=['asin','reviewTime'], how='outer')
	df.fillna(value=0, inplace=True)
	groups = df.groupby(['category','reviewTime'])

	df_counts = groups['overall'].count()
	df_counts = df_counts.to_frame().reset_index().rename(columns={'overall':'daily_review_count_category'})
	if verbose:
		print("Successfully computed daily review count for each category")

	print(df_counts.head())

	df_counts['avg_daily_review_count_category'] = df_counts['daily_review_count_category'].mean()
	df_counts['std_daily_review_count_category'] = df_counts['daily_review_count_category'].std()
	df_counts['threshold_daily_review_count_category'] = df_counts['avg_daily_review_count_category'] + 2*df_counts['std_daily_review_count_category']

	groups = df.groupby(['asin','reviewTime','category'])

	df_counts_product = groups['overall'].count()
	df_counts_product = df_counts_product.to_frame().reset_index().rename(columns={'overall':'daily_review_count_product'})
	if verbose:
		print("Successfully computed daily review count for each product")

	df_counts = pd.merge(df_counts, df_counts_product, on=['category','reviewTime'])
	df_counts['daily_review_count_2std_category'] = np.where(df_counts['daily_review_count_product'] > df_counts['threshold_daily_review_count_category'], 1, 0)

	groups = df_counts.groupby(['asin'])

	df_category_2std = groups['daily_review_count_2std_category'].sum()
	df_category_2std = df_category_2std.to_frame().reset_index().rename(columns={'daily_review_count_2std_category':'review_count_2std_n_category'})
	if verbose:
		print("Successfully counted reviews that exceed 2std threshold for each product")

	df_stats = pd.merge(df_counts, df_category_2std, on='asin')
	cols = ['threshold_daily_review_count_category', 'asin', 'review_count_2std_n_category']
	df_stats = df_stats[cols].drop_duplicates(keep='first')
	df_stats.to_csv(save_to, index=False)
	if verbose:
		print("Successfully saved category statistics to {}".format(save_to))

if __name__ == "__main__":
	"""
	Use case
	"""
	q = []
	#q.append(('../data/merged_Cell_Phones_&_Accessories.csv', 'Cell_Phones_and_Accessories'))
	#q.append(('../data/merged_Tools_&_Home_Improvement.csv', 'Tools_and_Home_Improvement'))
	q.append(('../data/merged_Office_Products.csv', 'Office_Products'))

	fp = DIR_PATH+'/did/reviews_mcauley_office_full.csv'
	#reviews_w_text = DIR_PATH+'/stat_analysis/office_reviews.csv'
	#reviews_numeric = DIR_PATH+'/stat_analysis/office_reviews_numeric.csv'
	products_stats = DIR_PATH+'/stat_analysis/office_products_stats.csv'
	burstiness_stats = DIR_PATH+'/stat_analysis/office_burstiness_stats.csv'

	get_products_stats(fp, products_stats)
	get_burstiness_stats(fp, burstiness_stats)
	products = pd.read_csv(products_stats, low_memory=False)
	burstiness = pd.read_csv(burstiness_stats, low_memory=False)
	df = pd.merge(products, burstiness, on='asin')
	df.to_csv(DIR_PATH+'/stat_analysis/office_products_stats.csv', index=False)



