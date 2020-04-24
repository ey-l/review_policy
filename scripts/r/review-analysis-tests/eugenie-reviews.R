## read .xlsx files
library(readxl)

############################ load data #############################
## load raw data
reviews2.csv <- read.csv('~/Dropbox/Eugenie/data/raw/arslan-reviews2.csv')
good_asin <- read_excel('~/Dropbox/Eugenie/data/raw/good_asin.xlsx')

## turn numeric values to factors
reviews2.csv$is_deleted <- as.factor(reviews2.csv$is_deleted)
reviews2.csv$incentivized <- as.factor(reviews2.csv$incentivized)
reviews2.csv$verified_purchaser <- as.factor(reviews2.csv$verified_purchaser)
reviews2.csv$recid <- as.factor(reviews2.csv$recid)

levels(reviews2.csv$verified_purchaser) <- c("unverified", "verified")
levels(reviews2.csv$incentivized) <- c("non-incentivized", "incentivized")
levels(reviews2.csv$is_deleted) <- c("kept", "deleted")

## turn factor variables to char strings
reviews2.csv$text <- as.character(reviews2.csv$text)
reviews2.csv$title <- as.character(reviews2.csv$title)

## turn factor variables to numeric
reviews2.csv$helpful_yes <- as.numeric(as.character(reviews2.csv$helpful_yes))
reviews2.csv$helpful_total <- as.numeric(as.character(reviews2.csv$helpful_total))
reviews2.csv$image_count <- as.numeric(as.character(reviews2.csv$image_count))


########################### add product category #########################
## add category data as extra columns
reviews2.csv['phone_batteries'] <- ifelse(reviews2.csv$item_id %in% good_asin$`PHONE BATTERIES` | 
                                            reviews2.csv$child_id %in% good_asin$`PHONE BATTERIES`, 1, 0)
reviews2.csv['phone_cables'] <- ifelse(reviews2.csv$item_id %in% good_asin$`PHONE CABLES` | 
                                         reviews2.csv$child_id %in% good_asin$`PHONE CABLES`, 1, 0)
reviews2.csv['screen_protectors'] <- ifelse(reviews2.csv$item_id %in% good_asin$`SCREEN PROTECTORS` | 
                                              reviews2.csv$child_id %in% good_asin$`SCREEN PROTECTORS`, 1, 0)

## drop this column when saving the result; this is just for better plotting and analysis
reviews2.csv['product_cat'] <- ifelse(reviews2.csv$phone_batteries == 1, 'phone_batteries', 
                                      ifelse(reviews2.csv$phone_cables == 1, 'phone_cables', 
                                             ifelse(reviews2.csv$screen_protectors == 1, 'screen_protectors', 'none')))
reviews2.csv$product_cat <- as.factor(reviews2.csv$product_cat)


########################### join test results ############################
test_results <- read.csv("~/Dropbox/Eugenie/data/processed/analysis-tests/test-results.csv")
count_test.stats <- read.csv("~/Dropbox/Eugenie/data/processed/analysis-tests/count-test-stats.csv")
length_test.stats <- read.csv("~/Dropbox/Eugenie/data/processed/analysis-tests/length-test-stats.csv")

## drop duplicate columns
reviews2.drop <- c('date')
test_results.drop <- c('item_id','word_count','product_cat')
reviews2.csv <- reviews2.csv[,!(names(reviews2.csv) %in% reviews2.drop)]
test_results <- test_results[,!(names(test_results) %in% test_results.drop)]

## merge AWS sentiment, review count, review length tests results to raw review data
reviews2.csv <- merge(reviews2.csv, test_results, by='recid')


################################## NOTE ####################################
## count_test.stats contains the mean, variance, and sd for the review daily count test.
## length_test.stats contains the mean, variance, and sd for the review length test.
## reviews2.csv contains test results from AWS and the two tests above.

## Data is dropped when:
## It has no product category.
## It occurs prior to 2012 or after 2018-10-07.
## It has no reviews prior to 2016-10-03.

## END of note

