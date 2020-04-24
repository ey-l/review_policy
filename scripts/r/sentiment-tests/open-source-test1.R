
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


##### a tidy approach for sentiment analysis for review2.csv #######

## get relevant columns
cols <- c('recid', 'item_id', 'user_id', 'text')
reviews2.text <- as.data.frame(reviews2.csv[, cols])

## turn numeric values to factors
reviews2.text$recid <- as.factor(reviews2.text$recid)

## turn factors to char vectors for tidy unnest_tokens
reviews2.text$text <- as.character(reviews2.text$text)

## get tidy tokens for each review record
tidy.reviews2.text <- reviews2.text %>% 
  unnest_tokens(word, text)

## remove stop words
data(stop_words)
tidy.reviews2.text <- tidy.reviews2.text %>% 
  anti_join(stop_words)

tidy.reviews2.text %>% count(word, sort=TRUE) %>%
  filter(n > 20000) %>%
  mutate(word = reorder(word, n)) %>%
  ggplot(aes(word, n))+
  geom_col()+
  xlab(NULL)+
  coord_flip()



### sentiment analysis with three lexicons ###

loughran.pos.neg <- get_sentiments("loughran") %>% 
  filter(sentiment %in% c("positive", "negative"))

## inner join with afinn sentiments
afinn.reviews2 <- tidy.reviews2.text %>%
  inner_join(get_sentiments('afinn')) 

## sum the sentiment of words by record
afinn.reviews2 <- afinn.reviews2 %>%
  group_by(recid) %>%
  summarise(afinn.sentiment=sum(value)) %>%
  mutate(method='AFINN')

## scale to -1 to 1 index
afinn.reviews2$afinn.sentiment.std <- rescale(afinn.reviews2$afinn.sentiment, to=c(-1,1))

## left join
reviews2.sentiment <- merge(reviews2.text, afinn.reviews2[,c('recid', 'afinn.sentiment', 'afinn.sentiment.std')], by='recid', all.x = T)
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
  mutate(method='BING')

## scale to -1 to 1 index
bing.reviews2$bing.sentiment.std <- rescale(bing.reviews2$bing.sentiment, to=c(-1,1))
## observe outliers, which make the standardize tool not so helpful

## left join
reviews2.sentiment <- merge(reviews2.sentiment, bing.reviews2[,c('recid', 'bing.sentiment', 'bing.sentiment.std')], by='recid', all.x = T)

## find number of rows with na in both indecies
table(lapply(reviews2.sentiment[,c('afinn.sentiment','bing.sentiment')], is.na))



## inner join with loughrun sentiments
loughran.reviews2 <- tidy.reviews2.text %>%
  inner_join(loughran.pos.neg)

## get sentiments of records by counting the number of positive vs. negative words per record
loughran.reviews2 <- loughran.reviews2 %>%
  group_by(recid) %>%
  summarise(positive.count=sum(sentiment=='positive'),
            negative.count=sum(sentiment=='negative'))

loughran.reviews2 <- loughran.reviews2 %>%
  mutate(loughran.sentiment=positive.count-negative.count) %>%
  mutate(method='LOUGHRAN')

## scale to -1 to 1 index
loughran.reviews2$loughran.sentiment.std <- rescale(loughran.reviews2$loughran.sentiment, to=c(-1,1))

## summary info, a lot more positive reviews
summary(loughran.reviews2)

## left join
reviews2.sentiment <- merge(reviews2.sentiment, loughran.reviews2[,c('recid', 'loughran.sentiment', 'loughran.sentiment.std')], by='recid', all.x = T)

## find number of rows with na in both indecies
sentiment.na.summary <- data.frame(table(lapply(reviews2.sentiment[,c('afinn.sentiment','bing.sentiment', 'loughran.sentiment')], is.na)))
sentiment.na.summary <- ddply(sentiment.na.summary, .(), mutate, Freq_pct = Freq/sum(Freq)*100)[-1]
## observe 22% of total records are missing all three lexicons sentiment indecies



### plots: sentiment index/score vs. rating ###

## merge on recid to get selected selected columns from the original data
reviews2.sentiment <- merge(reviews2.sentiment, reviews2.csv[,c('recid', 'rating', 'incentivized', 'is_deleted', 'verified_purchaser')])

## remove records with any na, so only 40% of the data is available for ploting
reviews2.sentiment.all <- na.omit(reviews2.sentiment)

## plot 
## plot the top 10 positive/negative words from bing
bing.reviews2 <- tidy.reviews2.text %>%
  inner_join(get_sentiments('bing')) %>%
  count(word, sentiment, sort = TRUE) %>%
  ungroup() %>%
  group_by(sentiment) %>%
  top_n(10) %>%
  ungroup() %>%
  mutate(word = reorder(word, n))

ggplot(bing.reviews2, aes(word, n, fill = sentiment)) +
  geom_col(show.legend = FALSE) +
  facet_wrap(~sentiment, scales = "free_y") +
  labs(y = "Contribution to sentiment",
       x = NULL) +
  coord_flip()

temp <- reviews2.sentiment.all %>%
  group_by(rating, afinn.sentiment) %>%
  summarise(count=n())

## boxplot afinn vs. rating
## less spread out than expected, but the trend is preserved
ggplot(reviews2.sentiment.all, aes(as.factor(rating), afinn.sentiment))+
  geom_boxplot()

ggplot(reviews2.sentiment.all, aes(as.factor(rating), afinn.sentiment.std))+
  geom_boxplot()


