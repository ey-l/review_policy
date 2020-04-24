import json
import pandas as pd
import gzip
import math
from datetime import datetime

# To count frequency in lists
import collections

def parse(path):
  g = gzip.open(path, 'rb')
  for l in g:
    yield json.loads(l.decode('utf-8'))

def getDF(path):
  i = 0
  df = {}
  for d in parse(path):
    df[i] = d
    i += 1
  return pd.DataFrame.from_dict(df, orient='index')

def numImg(x): 
    if (type(x) is str):
        return x.count(',')
    return 0

def numVote(x):
    if (type(x) is str):
        return float(int(x.replace(',', '')))
    if (math.isnan(x)):
        return 0
    return x

def ifAmazon (x):
    if x == 'Amazon' or x == 'AmazonBasics':
        return 1
    return 0

def common_member(a): 
    a_set = set(a) 
    b_set = set(cats) 
    if (a_set & b_set): 
        return True 
    else: 
        return False

def remove_uncommon(x):
    return list(set(x) & set(cats))

def create_cols(df):
    for i in cats:
        df[i] = df['category'].apply(lambda x: int(i in x))


#def get_product_review_count(product_path, review_path):
# Read the files
reviews = getDF('../data/Cell_Phones_and_Accessories.json.gz')
df = getDF('../data/meta_Cell_Phones_and_Accessories.json.gz')

# Drop irrelevant columns
df.drop(['image', 'feature', 'also_buy', 'also_view', 'similar_item', 'date', 'details', 'tech1', 'tech2', 'fit'], axis=1, inplace=True)

# Drop records with nan in category
df = df.dropna(subset=['category'])

# Add amazon label to each product
df['amazon'] = df['brand'].apply(ifAmazon)

# 1459641600 is the Unix timestamp of 2016-04-03
# 1491177600 is the Unix timestamp of 2017-04-03
# Get reviews within the 1 year time frame
reviews = reviews.loc[reviews['unixReviewTime'].apply(lambda x: x > 1459641600 and x < 1491177600)]

# Drop the index column for now
reviews.drop(reviews.columns[0], axis=1, inplace=True)

# Drop irrelevant columns
reviews.drop(['style'], axis=1, inplace=True)

# Process reviews
reviews['image'] = reviews['image'].apply(numImg) # Add image count
reviews['vote'] = reviews['vote'].apply(numVote) # Add vote count
reviews['reviewTime'] = reviews['reviewTime'].apply(lambda x: str(datetime.strptime(x, '%m %d, %Y').date()))

# All records have the same category labels
cats = []
df['category'].apply(lambda x: cats.extend(x))

# Get the top 10 subcategories as a list
cats = collections.Counter(cats)
cats = {k: v for k, v in reversed(sorted(cats.items(), key = lambda item: item[1]))}
cats = list(cats.keys())[0:1]

# Get products within top subcategories
df = df.loc[df['category'].apply(common_member)]

# Remove subcategories not in tops
df['category'] = df['category'].apply(remove_uncommon)

# Create a binary column for each subcategory
create_cols(df)

# Join
df_merged = pd.merge(reviews, df, on='asin')

# Remove asin with less than 10 reviews
df_merged['review_count'] = df_merged.groupby('asin')['asin'].transform('count') # Count reviews/asin
df_merged = df_merged.loc[df_merged['review_count'] > 10]

# Count the number products in each subcategory
cols = ['asin','amazon'] + cats
df_asin = df_merged[cols].drop_duplicates()
products_count = df_asin.groupby([df_asin['amazon']]).sum().astype(int)

# Count the number reviews in each subcategory
reviews_count = df_merged.groupby([df_merged['amazon']]).sum().astype(int)[cats]

# Print
print(products_dict)
print(reviews_dict)

# Save as .csv
#reviews.to_csv('reviews_asin.csv')