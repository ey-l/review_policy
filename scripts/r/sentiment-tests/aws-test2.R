
## read .xlsx files
library(readxl)

## pretty tables
library(pander)

########################## load source files ############################
source("~/Dropbox/Eugenie/scripts/utils.R")
aws_reviews <- read.csv("~/Dropbox/Eugenie/data/processed/sentiment/aws-reviews2-all.csv")
good_asin <- read_excel('~/Dropbox/Eugenie/data/raw/good_asin.xlsx')

## check if there's na value
aws_reviews[aws_reviews=='NA'] <- NA
na_reviews <- aws_reviews[rowSums(is.na(aws_reviews))>0,]


########################## data processing #############################

## merge with more columns
reviews2.temp <- merge(aws_reviews, reviews2.csv[,c('recid','item_id','child_id','rating','incentivized',
                                                    'is_deleted','verified_purchaser')])

## add product category
reviews2.temp['phone_batteries'] <- ifelse(reviews2.temp$item_id %in% good_asin$`PHONE BATTERIES` | 
                                             reviews2.temp$child_id %in% good_asin$`PHONE BATTERIES`, 1, 0)
reviews2.temp['phone_cables'] <- ifelse(reviews2.temp$item_id %in% good_asin$`PHONE CABLES` | 
                                          reviews2.temp$child_id %in% good_asin$`PHONE CABLES`, 1, 0)
reviews2.temp['screen_protectors'] <- ifelse(reviews2.temp$item_id %in% good_asin$`SCREEN PROTECTORS` | 
                                               reviews2.temp$child_id %in% good_asin$`SCREEN PROTECTORS`, 1, 0)

## drop this column when saving the result; this is just for better plotting and analysis
reviews2.temp['product_cat'] <- ifelse(reviews2.temp$phone_batteries == 1, 'phone_batteries', 
                                       ifelse(reviews2.temp$phone_cables == 1, 'phone_cables', 
                                              ifelse(reviews2.temp$screen_protectors == 1, 'screen_protectors', 'none')))
reviews2.temp$product_cat <- as.factor(reviews2.temp$product_cat)


############ linear fixed effect model for aws-review2.csv #############

# in model.fe, index = c('item_id') defines 'item_id' as the entity
formula.fe <- mixed ~ incentivized + is_deleted + verified_purchaser
model.fe <- plm(data = reviews2.temp, formula = formula.fe, index = c('item_id'), model = 'within')
# get the model summary
summary(model.fe)

# in model.fe, index = c('item_id') defines 'item_id' as the entity
formula.fe <- negative ~ incentivized + is_deleted + verified_purchaser
model.fe <- plm(data = reviews2.temp, formula = formula.fe, index = c('item_id'), model = 'within')
# get the model summary
summary(model.fe)

# in model.fe, index = c('item_id') defines 'item_id' as the entity
formula.fe <- neutral ~ incentivized + is_deleted + verified_purchaser
model.fe <- plm(data = reviews2.temp, formula = formula.fe, index = c('item_id'), model = 'within')
# get the model summary
summary(model.fe)

# in model.fe, index = c('item_id') defines 'item_id' as the entity
formula.fe <- positive ~ incentivized + is_deleted + verified_purchaser
model.fe <- plm(data = reviews2.temp, formula = formula.fe, index = c('item_id'), model = 'within')
# get the model summary
summary(model.fe)
