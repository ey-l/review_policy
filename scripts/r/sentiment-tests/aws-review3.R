## This file preps text files for AWS Comprehend

## Load outputs
reviews3_csv <- read.csv('~/Dropbox/Eugenie/data/raw/amazon_basics_cable reviews.csv')
reviews3_csv$text <- as.character(reviews3_csv$text)

## Get long reviews
long_reviews <- reviews3_csv[reviews3_csv$word_count>968,c('recid','rating','word_count','text')]

## Split long reviews
split_reviews.df <- data.frame(text=character(), recid=factor()) 

for(i in 1:nrow(long_reviews)) {
  ## Split by period
  text.og <- strsplit(long_reviews[i,'text'], split="[.]")[[1]]
  # Know how many groups by 5
  group_num <- length(text.og) %/% 20
  # Know how many words are left
  group_last <- length(text.og) %% 20
  
  # Generate the output
  text <- tapply(text.og, c(rep(1:group_num, each = 20), 
                            rep(group_num + 1, times = group_last)),toString)
  
  text <- as.data.frame(text) %>%
    mutate(recid = long_reviews[i,'recid']) %>%
    mutate(word_count = sapply(strsplit(text, " "), length))
  
  split_reviews.df <- rbind(split_reviews.df, text)
}

## Export the split text
write.csv(as.data.frame(split_reviews.df[,'text']), file = "reviews3-long-reviews.csv",row.names=FALSE)

## Get text
not_long_reviews <- reviews3_csv[!reviews3_csv$recid %in% long_reviews$recid,]
reviews3_aws <- as.data.frame(not_long_reviews$text)
names(reviews3_aws) <- 'text'

write.csv(reviews3_aws, file = "amazonbasics-cables-text.csv",row.names=FALSE)

## Merge the original data
aws.reviews3.short <- read.csv('aws-reviews-amazonbasics-cables.csv')
aws.reviews3.long <- read.csv('aws-reviews-test3-long.csv')

## Handle short reviews
not_long_reviews['line'] <- as.numeric(rownames(not_long_reviews))
not_long_reviews <- merge(not_long_reviews, aws.reviews3.short, by='line', all.x = TRUE)
not_long_reviews <- not_long_reviews[,c('recid','sentiment_cat','mixed','negative','neutral','positive')]

## Handle long reviews
split_reviews.df['line'] <- as.numeric(rownames(split_reviews.df))
split_reviews.df <- merge(split_reviews.df, aws.reviews3.long, by='line', all.x = TRUE)
split_reviews.df <- split_reviews.df[,!(names(split_reviews.df) %in% c('line', 'X'))]
split_reviews.df <- na.omit(split_reviews.df)
split_reviews.df <- split_reviews.df[,c('recid','mixed','negative','neutral','positive')]

## Get average sentiment score
all.reviews <- aws.reviews3.csv %>%
  group_by(recid) %>%
  mutate(mixed.ave = mean(mixed)) %>%
  mutate(negative.ave = mean(negative)) %>%
  mutate(neutral.ave = mean(neutral)) %>%
  mutate(positive.ave = mean(positive))

## Get selected columns
all.reviews <- all.reviews[,c('recid','mixed.ave','negative.ave','neutral.ave','positive.ave')] %>% distinct()
names(all.reviews) <- c('recid','mixed','negative','neutral','positive')

## Get sentiment category
all.reviews['sentiment_cat'] <- toupper(colnames(all.reviews[,c('mixed','negative','neutral','positive')])[max.col(all.reviews[,c('mixed','negative','neutral','positive')],ties.method="first")])
all.reviews <- all.reviews[,c('recid','sentiment_cat','mixed','negative','neutral','positive')]
split_reviews.df$recid <- as.numeric(as.character(split_reviews.df$recid))

## Bind
split_reviews.df$sentiment_cat <- as.factor(split_reviews.df$sentiment_cat)
aws_reviews.all <- bind_rows(not_long_reviews, split_reviews.df)
aws.reviews3.csv <- reviews3_csv
aws.reviews3.csv <- merge(aws.reviews3.csv, aws_reviews.all, by='recid', all.x = TRUE)
aws.reviews3.csv <- na.omit(aws.reviews3.csv)

## Export the split text
#aws.reviews3.csv <- merge(reviews3_csv, not_long_reviews, by='recid', all.x = TRUE)
write.csv(aws.reviews3.csv, file = "aws-amazonbasics-cables.csv",row.names=FALSE)


