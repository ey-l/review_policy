import json
import pandas as pd
import gzip

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

# Read the files
df = getDF('../data/Cell_Phones_and_Accessories.json.gz')
#asin = pd.read_csv('../data/cable_top200.csv')

# Make a list of all ids
#asin_list = list(asin['asin'])

# Get reviews with an id in asin
df_asin = df.loc[df['asin'] == 'B00QUU8NVM']

# Drop the index column for now
#df_asin.drop(df_asin.columns[0], axis=1, inplace=True)

# Drop the 'style' column for now
#df_asin.drop(['style'], axis=1, inplace=True)

# Save as .csv
df_asin.to_csv('reviews_B00QUU8NVM.csv')