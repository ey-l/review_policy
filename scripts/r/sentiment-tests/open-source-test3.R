########################## load library ############################
## for data manipulation
library(plyr)
library(dplyr)
library(tidyr)
library(stringr)
library(reshape)

## for plotting
library(ggplot2)
library(ggmosaic)
library(plotly)
library(ggpubr)

## for modelling
library(plm)
library(mgcv)
library(GoodmanKruskal)

## for sentiment analysis
library(tidytext)
library(textdata)
library(gutenbergr)
library(scales)
library(tm)



############################ load data #############################
## load raw data
reviews2.csv <- read.csv('~/Dropbox/Eugenie/data/arslan-reviews2.csv')

## turn numeric values to factors
reviews2.csv$is_deleted <- as.factor(reviews2.csv$is_deleted)
reviews2.csv$incentivized <- as.factor(reviews2.csv$incentivized)
reviews2.csv$verified_purchaser <- as.factor(reviews2.csv$verified_purchaser)

levels(reviews2.csv$verified_purchaser) <- c("unverified", "verified")
levels(reviews2.csv$incentivized) <- c("non-incentivized", "incentivized")
levels(reviews2.csv$is_deleted) <- c("kept", "deleted")

## remove extreme outlier
#reviews2.csv <- reviews2.csv[reviews2.csv$recid != 35676004,]

##### a tidy approach for sentiment analysis for review2.csv #######

## get relevant columns
cols <- c('recid', 'item_id', 'user_id', 'text')
reviews2.text <- as.data.frame(reviews2.csv[, cols])

## turn numeric values to factors
reviews2.text$recid <- as.factor(reviews2.text$recid)

## turn to lowercase and remove special chars
reviews2.text$text <- tolower(reviews2.text$text)
reviews2.text$text <- gsub('[[:punct:]]', ' ', reviews2.text$text)

## turn factors to char vectors for tidy unnest_tokens
reviews2.text$text <- as.character(reviews2.text$text)

## get tidy tokens for each review record
tidy.reviews2.text <- reviews2.text %>% 
  unnest_tokens(word, text)

## get stop words, use snowball lexicon
data(stop_words)
snowball <- stop_words[stop_words$lexicon=='snowball',]

## remove stop words
tidy.reviews2.text <- tidy.reviews2.text %>%
  anti_join(snowball)

tidy.reviews2.text %>% count(word, sort=TRUE) %>%
  filter(n > 20000) %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(word, n))+
  geom_col()+
  xlab(NULL)+
  coord_flip()



### sentiment analysis with three lexicons ###

## inner join with afinn sentiments
afinn.reviews2 <- tidy.reviews2.text %>%
  inner_join(get_sentiments('afinn')) 

## sum the sentiment of words by record
afinn.reviews2 <- afinn.reviews2 %>%
  group_by(recid) %>%
  mutate(word.count=n()) %>%
  mutate(afinn.sentiment=sum(value)) %>%
  mutate(method='AFINN')

## left join
reviews2.sentiment <- merge(reviews2.csv[,c('recid', 'item_id', 'rating', 'incentivized', 'is_deleted', 'verified_purchaser', 'text', 'title','word_count')], 
                            afinn.reviews2[,c('recid', 'afinn.sentiment')], by='recid', all.x = T)
## observe missing values: ~86205 records don't have an afinn sentiment index



## inner join with bing sentiments
bing.reviews2 <- tidy.reviews2.text %>%
  inner_join(get_sentiments('bing')) 

## get sentiments of records by counting the number of positive vs. negative words per record
bing.reviews2 <- bing.reviews2 %>%
  group_by(recid) %>%
  summarise(positive.count=sum(sentiment=='positive'),
            negative.count=sum(sentiment=='negative'))

bing.reviews2 <- bing.reviews2 %>%
  mutate(bing.sentiment=positive.count-negative.count) %>%
  mutate(word.count=positive.count+negative.count) %>%
  mutate(method='BING')

## left join
reviews2.sentiment <- merge(reviews2.sentiment, bing.reviews2[,c('recid', 'bing.sentiment')], by='recid', all.x = T)

## remove duplicates
reviews2.sentiment <- reviews2.sentiment %>% distinct()

## find number of rows with na in both indecies
sentiment.na.summary <- data.frame(table(lapply(reviews2.sentiment[,c('afinn.sentiment','bing.sentiment')], is.na)))
sentiment.na.summary <- ddply(sentiment.na.summary, .(), mutate, Freq_pct = Freq/sum(Freq)*100)[-1]
## observe 22% of total records are missing all three lexicons sentiment indecies
## observe 5% of total records are missing all two lexicons sentiment indecies with snowball lexicon

## investigate na's
sentiment.na <- reviews2.sentiment[is.na(reviews2.sentiment$afinn.sentiment)&
                                     is.na(reviews2.sentiment$bing.sentiment),]

## significantly shorter
summary(sentiment.na$word_count)
summary(reviews2.csv$word_count)


