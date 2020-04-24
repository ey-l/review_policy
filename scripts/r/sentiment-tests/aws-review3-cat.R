
## read .xlsx files
library(readxl)

## pretty tables
library(pander)

########################## load source files ############################
source("~/Dropbox/Eugenie/scripts/utils.R")
aws_reviews <- read.csv("~/Dropbox/Eugenie/data/processed/sentiment/aws-reviews3.csv")
good_asin <- read_excel('~/Dropbox/Eugenie/data/raw/phones-tablets.xlsx')

## check if there's na value
aws_reviews[aws_reviews=='NA'] <- NA
na_reviews <- aws_reviews[rowSums(is.na(aws_reviews))>0,]


########################## data processing #############################

## merge with more columns
reviews2.temp <- aws_reviews[,c('recid','item_id','child_id','rating','incentivized',
                                'is_deleted','verified_purchaser')]

#reviews3.temp <- merge(reviews2.temp, good_asin, by='item_id', all.x = T)
tablets <- good_asin[good_asin$tablets == 1, c('item_id','product_cat')]
cell_phones <- good_asin[good_asin$cell_phones == 1, c('item_id','product_cat')]
  
## add product category
reviews2.temp['tablets'] <- ifelse(reviews2.temp$item_id %in% tablets$item_id | 
                                             reviews2.temp$child_id %in% tablets$item_id, 1, 0)
reviews2.temp['cell_phones'] <- ifelse(reviews2.temp$item_id %in% cell_phones$item_id | 
                                          reviews2.temp$child_id %in% cell_phones$item_id, 1, 0)

## drop this column when saving the result; this is just for better plotting and analysis
reviews2.temp['product_cat'] <- ifelse(reviews2.temp$cell_phones == 1, 'cell_phones', 
                                       ifelse(reviews2.temp$tablets == 1, 'tablets', 'none'))
reviews2.temp$product_cat <- as.factor(reviews2.temp$product_cat)
reviews2.temp$item_id <- as.character(reviews2.temp$item_id)
reviews2.temp$child_id <- as.character(reviews2.temp$child_id)

reviews3.temp <- reviews2.temp[,c('recid','tablets','cell_phones','product_cat')]
aws_reviews <- merge(aws_reviews, reviews3.temp, by='recid')
reviews2.temp <- aws_reviews

reviews3.ids <- c(unique(reviews2.temp[,c('item_id')]), unique(reviews2.temp[,c('child_id')]))
reviews3.ids <- unique(reviews3.ids)
