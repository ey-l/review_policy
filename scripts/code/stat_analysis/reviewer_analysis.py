import sys
#sys.path.append('..')

import pandas as pd
import numpy as np
from utils import COLS, NON_TEXT

def get_reviewers(fp, category='Office Products'):
	df = pd.read_csv(fp, low_memory=False, index_col=0)
	sub_df = df.loc[df['category'] == category]
	reviewerIDs = list(set(sub_df.reviewerID))
	return reviewerIDs

def get_reviews_from_list(p, reviewerIDs, save_to, verbose=True):
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
