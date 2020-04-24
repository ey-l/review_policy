########################## load library ############################
## for data manipulation
library(plyr)
library(dplyr)
library(tidyr)
library(purrr)
library(readr)
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
library(textclean)
library(gutenbergr)
library(scales)
library(tm)
library(sentimentr)



############################ load data #############################
## Load raw data
reviews2.csv <- read.csv("~/Dropbox/Eugenie/data/raw/amazon_basics_cable reviews.csv")

## Load processed data
reviews3.csv <- read.csv('~/Dropbox/Eugenie/data/processed/processed-reviews3.csv')

## Turn numeric values to factors for reviews2
reviews2.csv$is_deleted <- as.factor(reviews2.csv$is_deleted)
reviews2.csv$incentivized <- as.factor(reviews2.csv$incentivized)
reviews2.csv$verified_purchaser <- as.factor(reviews2.csv$verified_purchaser)
reviews2.csv$recid <- as.factor(reviews2.csv$recid)

levels(reviews2.csv$verified_purchaser) <- c("unverified", "verified")
levels(reviews2.csv$incentivized) <- c("non-incentivized", "incentivized")
levels(reviews2.csv$is_deleted) <- c("kept", "deleted")

## Turn factor variables to char strings
reviews2.csv$text <- as.character(reviews2.csv$text)
reviews2.csv$title <- as.character(reviews2.csv$title)

## Turn factor variables to numeric
reviews2.csv$recid <- as.numeric(as.character(reviews2.csv$recid))
reviews2.csv$helpful_yes <- as.numeric(as.character(reviews2.csv$helpful_yes))
reviews2.csv$helpful_total <- as.numeric(as.character(reviews2.csv$helpful_total))
reviews2.csv$image_count <- as.numeric(as.character(reviews2.csv$image_count))

## Turn numeric values to factors for reviews3
reviews3.csv$is_deleted <- as.factor(reviews3.csv$is_deleted)
reviews3.csv$incentivized <- as.factor(reviews3.csv$incentivized)
reviews3.csv$verified_purchaser <- as.factor(reviews3.csv$verified_purchaser)
reviews3.csv$recid <- as.factor(reviews3.csv$recid)

levels(reviews3.csv$verified_purchaser) <- c("unverified", "verified")
levels(reviews3.csv$incentivized) <- c("non-incentivized", "incentivized")
levels(reviews3.csv$is_deleted) <- c("kept", "deleted")

## Turn factor variables to char strings for reviews3
reviews3.csv$text <- as.character(reviews3.csv$text)
reviews3.csv$title <- as.character(reviews3.csv$title)

## Turn factor variables to numeric for reviews3
reviews3.csv$recid <- as.numeric(as.character(reviews3.csv$recid))
reviews3.csv$helpful_yes <- as.numeric(as.character(reviews3.csv$helpful_yes))
reviews3.csv$helpful_total <- as.numeric(as.character(reviews3.csv$helpful_total))
reviews3.csv$image_count <- as.numeric(as.character(reviews3.csv$image_count))

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


############################# add time data ###########################
## turn factor to date variable
reviews2.csv$date <- as.Date(reviews2.csv$date, "%Y-%m-%d")

## do brief time series analysis by year
## get year attribute
reviews2.csv['year'] <- format(reviews2.csv$date,"%Y")
reviews2.csv$year <- as.factor(reviews2.csv$year)

reviews2.csv[is.na(reviews2.csv)] <- 0
reviews2.csv$month <- format(reviews2.csv$date, '%Y-%m')
reviews2.csv$month <- as.Date(paste0(reviews2.csv$month,'-01'),'%Y-%m-%d')

## get week dates
reviews2.csv$week <- floor_date(reviews2.csv$date, "week")

############################# add time data ###########################
## turn factor to date variable
reviews3.csv$date <- as.Date(reviews3.csv$date, "%Y-%m-%d")

## do brief time series analysis by year
## get year attribute
reviews3.csv['year'] <- format(reviews3.csv$date,"%Y")
reviews3.csv$year <- as.factor(reviews3.csv$year)

reviews3.csv[is.na(reviews3.csv)] <- 0
reviews3.csv$month <- format(reviews3.csv$date, '%Y-%m')
reviews3.csv$month <- as.Date(paste0(reviews3.csv$month,'-01'),'%Y-%m-%d')

## get week dates
reviews3.csv$week <- floor_date(reviews3.csv$date, "week")

############################# sentiment ###########################
## Get stop words, use snowball lexicon
data(stop_words)
snowball <- stop_words[stop_words$lexicon=='snowball',]

## Remove special chars
reviews2.csv <- reviews2.csv %>%
  filter(str_detect(text, "^[^>]+[A-Za-z\\d]") | text == "")

## Write the processed files
write.csv(reviews2.csv, file = "processed-amazonbasics-cables.csv",row.names=FALSE)
write.csv(reviews3.csv, file = "processed-reviews3.csv",row.names=FALSE)

