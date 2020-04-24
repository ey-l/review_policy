## download qdap package
library(devtools)
# install_github("trinker/qdapDictionaries")
# install_github("trinker/qdapRegex")
# install_github("trinker/qdapTools")

## this line doesn't work
#install_github("trinker/qdap")

## this line worked
#install.packages("qdap", INSTALL_opts = "--no-multiarch")

remove.packages('rJava')
install.packages('rJava')


########################## load source files ############################
source("utils.R")
library(rJava)
library(qdapRegex)
library(qdapDictionaries)
library(qdapTools)
library(qdap)

library(syuzhet)

##### a qdap approach for sentiment analysis for review2.csv #######

## get relevant columns
cols <- c('recid', 'item_id', 'user_id', 'rating', 'text')
reviews2.text <- as.data.frame(reviews2.csv[, cols])

## sample with top six records
reviews2.text$recid <- as.numeric(as.character(reviews2.text$recid))
temp <- head(reviews2.text)

## text cleanning
check_text(temp$text)
temp$text <- replace_contraction(temp$text)
temp$text <- replace_number(temp$text)
temp$text <- add_missing_endmark(temp$text)
temp$text <- add_comma_space(temp$text)
temp.split_text <- sentSplit(temp, "text")

## get polarity of the sample text
pol.temp <- with(temp.split_text, polarity(text.var = text, grouping.var = recid))
qdap.temp <- colsplit2df(scores(pol.temp))
qdap.temp <- qdap.temp[,1:4]
names(qdap.temp) <- c('recid','qdap.sentence_count','qdap.word_count','qdap.mean_sentiment')


plot(pol.temp)
plot(scores(pol.temp))
cumulative(pol.temp)

sentiment.temp <- merge(temp, sentiment_reviews_sentence, by='recid')
names(sentiment.temp) <- c('recid','item_id','user_id','rating','text','sentimentr.mean_sentiment','sentimentr.sentence_count')
sentiment.temp <- merge(sentiment.temp, qdap.temp, by='recid')

## END OF SAMPLING

## actual text ##

## text cleanning
check_text(reviews2.text$text)
reviews2.text$text <- replace_contraction(reviews2.text$text)
reviews2.text$text <- replace_number(reviews2.text$text)
reviews2.text$text <- add_missing_endmark(reviews2.text$text)
reviews2.text$text <- add_comma_space(reviews2.text$text)

## takes 1 hour to split sentences
reviews2.text.qdap <- sentSplit(reviews2.text, "text")

## write the sentiment file to data folder
## since the sentiment function takes a long time to execute
#write.csv(reviews2.text.qdap, file = "reviews2-text-qdap.csv",row.names=FALSE)
#reviews2.text.qdap <- read.csv('~/Dropbox/Eugenie/data/processed/reviews2-text-qdap.csv')

## get polarity of the sample text
## takes 3 hours to run
#pol.reviews2.text <- with(reviews2.text.qdap, polarity(text.var = text, grouping.var = recid))
#qdap.reviews2.text <- colsplit2df(scores(pol.reviews2.text))
#write.csv(qdap.reviews2.text, file = "qdap-reviews2-text.csv",row.names=FALSE)
qdap.reviews2.text <- read.csv('~/Dropbox/Eugenie/data/processed/qdap-reviews2-text.csv')

qdap.reviews2.text$recid <- as.numeric(qdap.reviews2.text$recid)
reviews2.csv$recid <- as.numeric(as.character(reviews2.csv$recid))
qdap.reviews2 <- merge(reviews2.csv[,c('recid','rating','text','incentivized','is_deleted','verified_purchaser')], qdap.reviews2.text, by='recid')
#write.csv(qdap.reviews2, file = "qdap-reviews2.csv",row.names=FALSE)
#qdap.reviews2 <- read.csv('~/Dropbox/Eugenie/data/processed/qdap-reviews2.csv')

## summary stats
qdap.reviews2[, c('incentivized','ave.polarity')] %>%
  group_by(incentivized) %>%
  summarize_all(mean, na.rm = TRUE)

## same sample for sentimentr
qdap.sample_100125154 <- qdap.reviews2[qdap.reviews2$recid==100125154,]

## check the records with na values for the ave.polarity
qdap.nas <- qdap.reviews2[is.na(qdap.reviews2$ave.polarity),]


##### a syuzhet approach for sentiment analysis for review2.csv #######
temp <- head(reviews2.text)
syuzhet.temp <- temp %>%
  mutate(syuzhet.sentiment = syuzhet::get_sentiment(temp$text))

## 4-5 mins to run
syuzhet.reviews2 <- reviews2.text[,c('recid','rating','text')] %>%
  mutate(syuzhet.sentiment = syuzhet::get_sentiment(reviews2.text$text))

syuzhet.reviews2 <- merge(reviews2.csv[,c('recid','incentivized','is_deleted','verified_purchaser')], syuzhet.reviews2, by='recid')
#write.csv(syuzhet.reviews2, file = "syuzhet-reviews2.csv",row.names=FALSE)
#syuzhet.reviews2 <- read.csv('~/Dropbox/Eugenie/data/processed/syuzhet-reviews2.csv')

## summary stats
syuzhet.reviews2[, c('incentivized','syuzhet.sentiment')] %>%
  group_by(incentivized) %>%
  summarize_all(mean, na.rm = TRUE)

## same sample for sentimentr
syuzhet.sample_100125154 <- syuzhet.reviews2[syuzhet.reviews2$recid==100125154,]

syuzhet.reviews2 <- syuzhet.reviews2 %>%
  mutate(afinn.sentiment = syuzhet::get_sentiment(syuzhet.reviews2$text, 'afinn'))

syuzhet.reviews2 <- syuzhet.reviews2 %>%
  mutate(nrc.sentiment = syuzhet::get_sentiment(syuzhet.reviews2$text, 'nrc')) %>%
  mutate(bing.sentiment = syuzhet::get_sentiment(syuzhet.reviews2$text, 'bing'))







