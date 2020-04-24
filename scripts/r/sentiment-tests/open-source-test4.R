####################### load source files ##########################
source("~/Dropbox/Eugenie/scripts/utils.R")


##### a tidy approach for sentiment analysis for review2.csv #######

## get relevant columns
cols <- c('recid', 'item_id', 'user_id', 'text')
reviews2.text <- as.data.frame(reviews2.csv[, cols])

## split the dataset into tokens, while removing stop-words
reviews_words <- reviews2.csv %>%
  unnest_tokens(word, text) %>%
  filter(str_detect(word, "[a-z']$"),
         !word %in% snowball$word)


################# sentiment analysis by review ###################

## try giving individual reviews a sentiment score by taking the mean of words
sentiment_messages <- reviews_words %>%
  inner_join(get_sentiments("afinn"), by = "word") %>%
  group_by(recid) %>%
  summarize(sentiment = mean(value),
            words = n()) %>%
  ungroup()


############### sentiment analysis by sentence ###################

## get sentiment by sentence using sentimentr package
# reviews_sentences <- reviews2.text %>%
#   get_sentences(text) %>%
#   mutate(sentence_sentiment = sentimentr::sentiment(text)$sentiment)

## write the sentiment file to data folder
## since the sentiment function takes a long time to execute
#write.csv(reviews_sentences, file = "reviews_sentences.csv",row.names=FALSE)

## read the sentiment analysis result (using sentimentr package)
reviews_sentences <- read.csv('~/Dropbox/Eugenie/data/processed/reviews_sentences.csv')

## get sentiment by reviews by taking the mean of sentences
sentiment_reviews_sentence <- reviews_sentences %>%
  group_by(recid) %>%
  summarize(review_sentiment = mean(sentence_sentiment),
            sentence_count = n()) %>%
  ungroup()

## join the mean sentiment score 
cols <- c('recid','item_id','rating','helpful_yes','helpful_total',
          'image_count','word_count','brand_repeat',
          'incentivized','is_deleted','verified_purchaser')
reviews2.text <- reviews2.csv[,cols]
reviews2.text <- merge(reviews2.text, sentiment_reviews_sentence, by='recid')

## summary stats checks
reviews2.text[, c('incentivized','review_sentiment')] %>%
  group_by(incentivized) %>%
  summarize_all(mean, na.rm = TRUE)
## Notes: incentivized sentiment mean is lower 

## boxplot: rating vs. sentence_sentiment
plot_ly(reviews2.text, x = ~as.factor(rating), y = ~review_sentiment, type = 'box',
        marker = list(color = 'rgb(8,81,156)',
                      outliercolor = 'rgba(219, 64, 82, 0.6)',
                      line = list(outliercolor = 'rgba(219, 64, 82, 1.0)',
                                  outlierwidth = 2)),
        line = list(color = 'rgb(8,81,156)')) %>%
  layout(xaxis = list(title=""))

## fix effect linear model
## Use sentence sentiment score to replce rating
formula.fe <- review_sentiment ~ incentivized + is_deleted + verified_purchaser
model.fe <- plm(data = reviews2.text, formula = formula.fe, index = c('item_id'), model = 'within')
# get the model summary
summary(model.fe)

## correlation: rating vs. review sentiment
cor(reviews2.text$rating, reviews2.text$review_sentiment, method = c("pearson", "kendall", "spearman"))
cor.test(reviews2.text$rating, reviews2.text$review_sentiment, method=c("pearson", "kendall", "spearman"))

## corr scatter plot
ggscatter(reviews2.text, x = 'rating', y = 'review_sentiment', 
          add = "reg.line", conf.int = TRUE, 
          cor.coef = TRUE, cor.method = "pearson",
          xlab = "Review Rating", ylab = "Review Sentiment by Sentence")




##################### bigrams approach ############################
## get bigrams
reviews_bigrams <- reviews2.text %>%
  unnest_tokens(bigram, text, token = "ngrams", n = 2)

## filter bigrams with stop words
bigrams_separated <- reviews_bigrams %>%
  separate(bigram, c("word1", "word2"), sep = " ")

bigrams_filtered <- bigrams_separated %>%
  filter(!word1 %in% stop_words$word) %>%
  filter(!word2 %in% stop_words$word)

## new bigram counts:
bigram_counts <- bigrams_filtered %>% 
  count(word1, word2, sort = TRUE)

bigrams_united <- bigrams_filtered %>%
  unite(bigram, word1, word2, sep = " ")

## analysis with bigrams
## bigrams separated by 'not'
bigrams_separated %>%
  filter(word1 == "not") %>%
  count(word1, word2, sort = TRUE)

## get AFINN sentiment lexicon
AFINN <- get_sentiments("afinn")

## examine the most frequent words that were preceded by “not” and were associated with a sentiment
not_words <- bigrams_separated %>%
  filter(word1 == "not") %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word2, value, sort = TRUE)

## visualize the 20 most frequent words that are preceeded by "not"
not_words %>%
  mutate(contribution = n * value) %>%
  arrange(desc(abs(contribution))) %>%
  head(20) %>%
  mutate(word2 = reorder(word2, contribution)) %>%
  ggplot(aes(word2, n * value, fill = n * value > 0)) +
  geom_col(show.legend = FALSE) +
  xlab("Words preceded by \"not\"") +
  ylab("Sentiment score * number of occurrences") +
  coord_flip()

## "not" isn't the only negative word
negation_words <- c("not", "no", "never", "without")

negated_words <- bigrams_separated %>%
  filter(word1 %in% negation_words) %>%
  inner_join(AFINN, by = c(word2 = "word")) %>%
  count(word1, word2, value, sort = TRUE)









