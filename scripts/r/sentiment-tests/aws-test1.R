## Purpose: Separate the long reviews for AWS Comprehend

########################## load source files ############################
source("~/Dropbox/Eugenie/scripts/utils.R")

## load inputs
reviews2_text <- as.data.frame(reviews2.csv$recid)
names(reviews2_text) <- 'recid'

## load outputs
reviews2_aws <- read.csv('aws-reviews-test2.csv')
reviews2_aws <- reviews2_aws[,!(names(reviews2_aws) %in% c('X'))]

reviews2_text <- split_reviews.df
reviews2_text['line'] <- as.numeric(rownames(reviews2_text))

reviews2_text <- merge(reviews2_text, reviews2_aws, by='line', all.x = TRUE)
reviews2_text <- reviews2_text[,!(names(reviews2_text) %in% c('line'))]

## get average sentiment score
reviews2_text <- reviews2_text %>%
  group_by(recid) %>%
  mutate(mixed.ave = mean(mixed)) %>%
  mutate(negative.ave = mean(negative)) %>%
  mutate(neutral.ave = mean(neutral)) %>%
  mutate(positive.ave = mean(positive))

## get selected columns
reviews2_text.split <- reviews2_text[,c('recid','mixed.ave','negative.ave','neutral.ave','positive.ave')] %>% distinct()
names(reviews2_text.split) <- c('recid','mixed','negative','neutral','positive')

## get sentiment category
reviews2_text.split['sentiment_cat'] <- toupper(colnames(reviews2_text.split[,c('mixed','negative','neutral','positive')])[max.col(reviews2_text.split[,c('mixed','negative','neutral','positive')],ties.method="first")])
reviews2_text.split <- reviews2_text.split[,c('recid','sentiment_cat','mixed','negative','neutral','positive')]
reviews2_text.split$recid <- as.numeric(as.character(reviews2_text.split$recid))
aws_reviews <- na.omit(aws_reviews)
aws_reviews.all <- bind_rows(aws_reviews, reviews2_text.split)

aws_reviews.all$sentiment_cat <- as.factor(aws_reviews.all$sentiment_cat)

write.csv(aws_reviews.all, file = "aws-reviews2.csv",row.names=FALSE)

## note that the NA's are from review texts that exceed comprehend's maxium length per call
## will need some special treatment there

aws_reviews <- read.csv("~/Dropbox/Eugenie/data/processed/aws-reviews2.csv")
aws_reviews[aws_reviews=='NA'] <- NA
na_reviews <- aws_reviews[rowSums(is.na(aws_reviews))>0,]

## investgate na rows; theoritically, it's because they're too long
na_reviews <- merge(na_reviews, reviews2.csv[,c('recid','text','rating','word_count','incentivized')], by='recid')
long_reviews <- reviews2.csv[reviews2.csv$word_count>968,c('recid','rating','word_count','text')]

## split into something
split_reviews.df <- data.frame(text=character(), recid=factor()) 

for(i in 1:nrow(long_reviews)) {
  ## split by period
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

## export the split text
write.csv(as.data.frame(split_reviews.df[,'text']), file = "aws-reviews2-split.csv",row.names=FALSE)


