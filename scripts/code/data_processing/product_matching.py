# Import libraries
import json
import pandas as pd
import gzip
import math
from datetime import datetime

# Graphing
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# Doc2vec
from gensim.models import doc2vec
from collections import namedtuple
from datetime import datetime
import re
import string
from sklearn import utils
from sklearn.model_selection import train_test_split
# Generate cosine similarity matrix from vectors
from sklearn.metrics.pairwise import cosine_similarity

# NLP
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm") # Set up NLP
DIR_PATH = '../data/Processed_Julian_Amazon_data'

# Ignore warnings
#import warnings
#warnings.filterwarnings('ignore')


# Clean text
from bs4 import BeautifulSoup
def cleanText(text):
    soup = BeautifulSoup(text, "lxml")
    text = soup.get_text() # Remove url
    text = "".join([c for c in text if c not in string.punctuation]) # Remove punctuation
    text = text.lower() # To lower case
    return text

def tokenize_text(texts, ids):
    tokens = []
    # Organize data (assign each review a tag 0 to i)
    analyzedDocument = namedtuple('AnalyzedDocument', 'words tags')
    for i, text in enumerate(texts):
        words = text.split()
        #tags = [ids[i]]
        tags = [i]
        tokens.append(analyzedDocument(words, tags))
    return tokens

def setZero(x,t):
    if x < t:
        return 0
    return x

def makeTuple(x,col):
    return (col, float(x))

def get_review_lemma(doc):
    doc = nlp(doc)
    lemma = ""
    for token in doc:
        lemma += " " + token.lemma_
    print('hey')
    return lemma

def getNegation_tree(x):
    doc = nlp(x)
    negation_tokens = [tok for tok in doc if tok.text in ['not','no']]
    negation_head_tokens = [token.head.text for token in negation_tokens]
    negation_ancestors = []
    for n in negation_tokens:
        n_tokens = n.ancestors
        # The first jump
        for i in n_tokens:
            negation_ancestors.append(i.text)
            children = i.children
            # The second jump
            for j in children:
                negation_ancestors.extend([t.text for t in children])
    result = negation_ancestors + negation_head_tokens
    if len(result) > 0:
        return list(set(result))
    return []

def ifNegation_tree(x, incentivized_flags):
    negation_head_tokens = getNegation_tree(x)
    for i in negation_head_tokens:
        if i in incentivized_flags:
            return 1
    return 0

def get_doc2vec(dataset, df_path):
    # Read the merged review file
    reviews = pd.read_csv(df_path, low_memory=False)
    reviews = reviews[reviews['title'].map(str).map(len) < 1000]

    # Remove asin with less than 10 reviews
    reviews['review_count'] = reviews.groupby('asin')['asin'].transform('count') # Count reviews/asin
    reviews = reviews.loc[reviews['review_count'] > 10]

    # Drop all columns except for item_id and text
    item_id = 'asin'
    text_col = 'description' #'reviewText'
    df = reviews[[item_id, text_col]].drop_duplicates(keep='first')

    # Drop records with empty reviews
    df = df[pd.notnull(df[text_col])]
    df[text_col] = df[text_col].apply(cleanText)

    # ==================================================================================================
    # Generate list of item ids and review texts 
    ids = list(df[item_id])
    texts = list(df[text_col])

    # Input all reviews
    train_corpus = tokenize_text(texts, ids)

    # Train the model
    model = doc2vec.Doc2Vec(vector_size = 100, min_count=1)
    model.build_vocab(train_corpus)
    model.train(train_corpus, total_examples = model.corpus_count, epochs = model.epochs)

    # Create a dictionary with key value pair (Product ID : List of review vector values)
    final_dict = {}
    for i in range(len(ids)):
        if ids[i] in final_dict:
            final_dict[ids[i]].append(model.docvecs[i])
        else:
            new_list = []
            new_list.append(model.docvecs[i])
            final_dict[ids[i]] = new_list

    # Find mean of values and update dictionary to reflect new values 
    for key in final_dict.keys():
        current_list = final_dict[key]
        vector_avg = sum(current_list)/len(current_list)
        final_dict[key] = vector_avg

    # Write dictionary to Pandas dataframe
    vectors = pd.DataFrame.from_dict(final_dict, orient = 'index')
    log = '../data/Processed_Julian_Amazon_data/doc2vec/'+dataset+'_description.csv'
    vectors.to_csv(log)
    print(dataset + " is logged!")

def get_similar_products(dataset, df_path, vector_path, n):
    # Read the merged review file
    df = pd.read_csv(df_path, low_memory=False)
    #df.rename(columns={'image_y': 'image'}, inplace=True)

    # Read doc2vec file
    vectors = pd.read_csv(vector_path, index_col=0, low_memory=False)

    # Get a list of Amazon product ids
    df_amazon = df.loc[df['amazon'] == 1]
    asin_amazon = df_amazon['asin'].drop_duplicates(keep='first')
    print(df_amazon.columns)
    print(df_amazon.head())
    print(vectors.index)

    # Get Amazon product vectors
    vec_amazon = vectors[vectors.index.isin(asin_amazon)]
    print(vec_amazon)

    # Take set difference
    vectors = pd.concat([vectors, vec_amazon, vec_amazon]).drop_duplicates(keep=False)

    # Get cosine similarity 
    sims = cosine_similarity(vectors, vec_amazon)
    sims = pd.DataFrame(sims)
    sims.columns = vec_amazon.index
    sims.index = vectors.index

    # Get the number of non-Amazon products for each Amazon product at each similarity threshold
    sim_threshold = [0.95, 0.90, 0.8, 0.7, 0.5] #[0.99, 0.985, 0.98, 0.975, 0.97]
    sim_size = {}
    for t in sim_threshold:
        size = []
        for i in range(len(sims.columns)):
            size.append(len(sims.loc[sims[sims.columns[i]] > t]))
        sim_size[t] = size
    df_size = pd.DataFrame.from_dict(sim_size)
    df_size.index = sims.columns
    log = '../data/Processed_Julian_Amazon_data/sim_threshold/'+dataset+'_sim_threshold.csv'
    df_size.to_csv(log, index=False)

    # Get the top 100 most similar non-Amazon products for each Amazon product
    df_sims = {}
    all_sims = []
    #n = 100
    for i in range(len(sims.columns)):
        topn = list(pd.DataFrame(sims[sims.columns[i]]).sort_values(sims.columns[i]).iloc[::-1].head(n).index)
        df_sims[sims.columns[i]] = topn
        all_sims.extend(topn)
    df_sims = pd.DataFrame(df_sims)
    all_sims = list(set(all_sims))

    # Get the similarity index for top 100 non-amazon products
    sims_n = sims.loc[sims.index.map(lambda x: x in all_sims)]
    print('There are '+str(sims_n.shape[0])+' distinct non-Amazon products in '+dataset)

    thresholds = df_sims.iloc[9,:].to_dict()
    keys = list(thresholds.keys())
    for i in range(len(keys)):
        threshold = sims_n.loc[sims_n.index == thresholds[keys[i]]][keys[i]].item()
        thresholds[keys[i]] = threshold

    keys = list(thresholds.keys())
    values = list(range(1, len(keys)+1))
    sims_dict = dict(zip(keys, values))

    for i in range(len(sims_n.columns)):
        col = sims_n.columns[i]
        t = thresholds[col]
        sims_n[col] = sims_n[col].apply(lambda x: setZero(x, t))
        sims_n[col] = sims_n[col].apply(lambda x: makeTuple(x,col))

    for index, row in sims_n.iterrows():
        new_row = sorted(list(row), key=lambda x: x[1])[::-1]
        for i in range(len(new_row)):
            asin = new_row[i][0]
            sim_index = new_row[i][1]
            if sim_index > 0:
                #row[i] = sims_dict[asin] # 1-9 as value
                row[i] = asin # asin as value
            else:
                row[i] = 0

    # Rename the cols to store the most similar Amazon product for each non-Amazon product
    # since some non-Amazon products get to mapped to multiple Amazon products
    col_names = ['sim' + str(x) for x in range(1, len(sims_n.columns) + 1)]
    sims_n.columns = col_names

    # Get the number of non-Amazon products in each category
    amazon_sims = list(vec_amazon.index)
    amazon_sims.extend(all_sims)
    df_na = df.loc[df['asin'].apply(lambda x: x in all_sims)] # Dataframe of all non-Amazon products 
    df_all = df.loc[df['asin'].apply(lambda x: x in amazon_sims)] # Dataframe of all non-Amazon products 

    # Merge with the review data (i.e., df_all, df_na)
    sims_n['asin'] = sims_n.index
    df_test = pd.merge(df_all, sims_n, on='asin', how='left')
    df_test[col_names] = df_test[col_names].fillna(0)
    df_test.loc[df_test['asin'].apply(lambda x: x not in all_sims),'sim1'] = df_test['asin']
    log = '../data/Processed_Julian_Amazon_data/sim_reviews/'+dataset+'_'+str(n)+'_similar_reviews.csv'
    df_test.to_csv(log, index=False)

    #return df_test
    print(dataset + " is logged!")

# Takes in a merged review file
def tag_incentive(dataset, df_path):
    # Read the merged review file
    df = pd.read_csv(df_path, low_memory=False)
    
    # Get review lemma
    df['reviewText'] = df['reviewText'].fillna(value=".")
    df.dropna(subset=['reviewText'], inplace = True)
    
    # Get a smaller dataframe
    reviewText = pd.DataFrame(df['reviewText'])
    reviewText['lemmaText'] = reviewText['reviewText'].apply(get_review_lemma)
    log = '../data/Processed_Julian_Amazon_data/lemma/'+dataset+'_wlemma.csv'
    reviewText.to_csv(log, index=False)
    print(dataset + " lemma is logged!")

    # NLP steps to identify intentivized reviews
    incentivized_flags = ['incentivize', 'incentive', 'discount', 'affiliate', 'promote', 'promotion', 'sponsor', 'sponsorship', 'discount']
    reviews = reviewText.loc[reviewText['lemmaText'].apply(lambda x: any([k in x for k in incentivized_flags]))]
    reviews['if_neg'] = reviews['lemmaText'].apply(lambda x: ifNegation_tree(x, incentivized_flags))
    reviews['incentivized'] = 1
    reviews['incentivized'] = reviews['incentivized'] - reviews['if_neg']
    reviews = reviews[['incentivized','if_neg']]
    
    # Save results
    log = '../data/Processed_Julian_Amazon_data/'+dataset+'_stats.csv'
    reviews.groupby(['if_neg']).count().to_csv(log, index=False)
    print(dataset + " incentivized review stats is logged!")

    # Merge with the full review dataset
    df_incent = pd.merge(df, reviews, left_index=True, right_index=True, how='left')
    df_incent['incentivized'] = df_incent['incentivized'].fillna(0)
    df_incent['if_neg'] = df_incent['if_neg'].fillna(int(0))

    # Remove the intermediate result
    df_incent.drop('if_neg', axis=1, inplace=True)
    
    # Save results
    log = '../data/Processed_Julian_Amazon_data/tagged/'+dataset+'_merged_reviews_tagged.csv'
    df_incent.to_csv(log, index=False)
    print(dataset + " is logged!")

# Takes in a merged review file
def tag_incentive_ngrams(dataset, df_path):
    # Read the merged review file
    df = pd.read_csv(df_path, low_memory=False)

    lemma_path = '../data/Processed_Julian_Amazon_data/lemma/'+dataset+'_wlemma.csv'
    lemma_df = pd.read_csv(lemma_path, low_memory=False)
    reviewText = pd.DataFrame(lemma_df['lemmaText'])

    merged_inc_diff = pd.read_csv('../data/reviewMeta/reviewMeta_incentive_text_ngrams.csv', low_memory=False)
    incentivized_flags = list(merged_inc_diff['ngrams'])

    reviews = reviewText.loc[reviewText['lemmaText'].apply(lambda x: any([k in x for k in incentivized_flags]))]
    reviews['incentivized_ngrams'] = 1

    # Merge with the full review dataset
    df_incent = pd.merge(df, reviews, left_index=True, right_index=True, how='left')
    df_incent['incentivized_ngrams'] = df_incent['incentivized_ngrams'].fillna(0)

    # Save results
    log = '../data/Processed_Julian_Amazon_data/'+dataset+'_stats.csv'
    df_incent.groupby(['incentivized','incentivized_ngrams']).count().to_csv(log, index=False)
    print(dataset + " incentivized review stats is logged!")

    # Save results
    log = '../data/Processed_Julian_Amazon_data/tagged/'+dataset+'_ngrams.csv'
    df_incent.to_csv(log, index=False)
    print(dataset + " is logged!")

def match_products(paths):
    '''
    Use case:
    q = []
    q.append(...)
    
    for i in q:
        match_products(i)
    '''
    df_path = paths[0]
    dataset = paths[1]

    vectors = DIR_PATH+'/doc2vec/'+dataset+'_description.csv'
    similar_df = DIR_PATH+'/sim_reviews/'+dataset+'_10_similar_reviews.csv'
    tagged_path = DIR_PATH+'/tagged/'+dataset+'_merged_reviews_tagged.csv'
    
    get_doc2vec(dataset, df_path)
    get_similar_products(dataset, df_path, vectors, 10)
    #tag_incentive(dataset, similar_df)
    #tag_incentive_ngrams(dataset, tagged_path)
