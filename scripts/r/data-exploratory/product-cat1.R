########################## load source files ############################
source("~/Dropbox/Eugenie/scripts/utils.R")


## add category data as extra columns
reviews2.temp <- reviews2.csv

## check records w/o a category
cat_sum <- reviews2.temp %>%
  group_by(product_cat) %>%
  summarise(product.count = n()) %>%
  mutate(product.pct = product.count/sum(product.count)*100)

## plot the percentage of records w/ and w/o a category
cat_sum <- data.frame(rowSums(reviews2.temp[,c('phone_batteries','phone_cables','screen_protectors')]))
names(cat_sum) <- 'cat_sum'
cat_sum$cat_sum <- as.factor(cat_sum$cat_sum)
cat_sum <- cat_sum %>%
  mutate(cat='Category')

ggplot(data=cat_sum, aes(cat))+ geom_bar(aes(fill=cat_sum), position="fill")

## turn factor to date variable
reviews2.temp$date <- as.Date(reviews2.temp$date, "%Y-%m-%d")

## do brief time series analysis by year
## get year attribute
reviews2.temp['year'] <- format(reviews2.temp$date,"%Y")
reviews2.temp$year <- as.factor(reviews2.temp$year)

## skewed counts by year
table(reviews2.temp$year)

## drop records before 2012
reviews2.temp <- reviews2.temp[as.numeric(as.character(reviews2.temp$year))>2013,]

## check incentivized reviews after it got banned
cat_sum <- reviews2.temp %>%
  mutate(is_after = ifelse(date > '2016-10-03','after being banned','before being banned')) %>%
  group_by(incentivized,is_after) %>%
  summarise(review.count = n()) %>%
  mutate(review.pct = review.count/sum(review.count)*100)

## percentage of rating vs. year
ggplot(data=reviews2.temp, aes(year))+
  geom_bar(aes(fill=as.factor(rating)), position="fill")+
  scale_fill_brewer(palette="RdBu")+
  ylab('proportion')

## percentage of rating vs. product_cat
ggplot(data=reviews2.temp, aes(product_cat))+
  geom_bar(aes(fill=as.factor(rating)), position="fill")+
  scale_fill_brewer(palette="RdBu")+
  ylab('proportion')+
  labs(fill='rating')

## plot median rating over time by product_cat
reviews.product <- reviews2.temp[,c('recid','item_id','incentivized','product_cat','rating','word_count','helpful_yes','date','year')]
reviews.product[is.na(reviews.product)] <- 0
reviews.product$month <- format(reviews.product$date, '%Y-%m')
reviews.product$month <- as.Date(paste0(reviews.product$month,'-01'),'%Y-%m-%d')

## get week dates
reviews.product$weeks <- floor_date(reviews.product$date, "week")

## mean rating by day
reviews.product <- reviews.product %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

## mean rating by week
reviews.product <- reviews.product %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

## mean rating by month
reviews.product <- reviews.product %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

## plot by day
ggplot(NULL, aes(x = date, y = day_rating))+
  geom_point(data=reviews.product, aes(color = "daily ave rating"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product,method = 'auto',aes(color='daily ave rating line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='day',y='mean rating',fill='category',title='Product Category Mean Rating by Day')

## plot by week
ggplot(NULL, aes(x = weeks, y = week_rating))+
  geom_point(data=reviews.product, aes(color = "weekly ave rating"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product,method = 'auto',aes(color='weekly ave rating line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='day',y='mean rating',fill='category',title='Product Category Mean Rating by Week')

## plot by month
ggplot(NULL, aes(x = month, y = month_rating))+
  geom_point(data=reviews.product, aes(color = "monthly ave rating"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product,method = 'auto',aes(color='monthly ave rating line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='day',y='mean rating',fill='category',title='Product Category Mean Rating by Month')

################################# split on date #############################
## split on date
reviews.product_non <- reviews.product[reviews.product$date<'2016-10-03'&reviews.product$incentivized=='non-incentivized',]
reviews.product_incentivized <- reviews.product[reviews.product$date<'2016-10-03'&reviews.product$incentivized=='incentivized',]
reviews.product_after <- reviews.product[reviews.product$date>'2016-10-03',]

## mean rating by day
reviews.product_non <- reviews.product_non %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

reviews.product_incentivized <- reviews.product_incentivized %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

reviews.product_after <- reviews.product_after %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

## mean rating by week
reviews.product_non <- reviews.product_non %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

reviews.product_incentivized <- reviews.product_incentivized %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

reviews.product_after <- reviews.product_after %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

## mean rating by month
reviews.product_non <- reviews.product_non %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

reviews.product_incentivized <- reviews.product_incentivized %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

reviews.product_after <- reviews.product_after %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

## plot by day
ggplot(NULL, aes(x = date, y = day_rating))+
  geom_point(data=reviews.product_incentivized, aes(color = "incentivized"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non, aes(color = "non-incentivized"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_after, aes(color = "unidentified"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product_incentivized,method = 'auto',aes(color='incentivized-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non,method = 'auto',aes(color='non-incentivized-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_after,method = 'auto',aes(color='unidentified-line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='day',y='mean rating',fill='category',title='Product Category Mean Rating by Day')

## by week
ggplot(NULL, aes(x = weeks, y = week_rating))+ 
  geom_point(data=reviews.product_incentivized, aes(color = "incentivized"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non, aes(color = "non-incentivized"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_after, aes(color = "unidentified"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product_incentivized,method = 'auto',aes(color='incentivized-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non,method = 'auto',aes(color='non-incentivized-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_after,method = 'auto',aes(color='unidentified-line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='week',y='mean rating',fill='category',title='Product Category Mean Rating by Week')

## by month
ggplot(NULL, aes(x = month, y = month_rating, color = product_cat))+
  geom_point(data=reviews.product_incentivized, aes(color = "incentivized"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non, aes(color = "non-incentivized"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_after, aes(color = "unidentified"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product_incentivized,method = 'auto',aes(color='incentivized-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non,method = 'auto',aes(color='non-incentivized-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_after,method = 'auto',aes(color='unidentified-line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-02'), color = "black", size=0.3)+
  labs(x='month',y='mean rating',fill='category',title='Product Category Mean Rating by Month')


############################ more exploratory ###########################

## split on date
reviews.product_non1 <- reviews.product[reviews.product$date<'2016-10-03'&reviews.product$incentivized=='non-incentivized',]
reviews.product_incentivized1 <- reviews.product[reviews.product$date<'2016-10-03'&reviews.product$incentivized=='incentivized',]
reviews.product_non2 <- reviews.product[reviews.product$date>'2016-10-03'&reviews.product$incentivized=='non-incentivized',]
reviews.product_incentivized2 <- reviews.product[reviews.product$date>'2016-10-03'&reviews.product$incentivized=='incentivized',]

## mean rating by day
reviews.product_non1 <- reviews.product_non1 %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

reviews.product_incentivized1 <- reviews.product_incentivized1 %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

reviews.product_non2 <- reviews.product_non2 %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

reviews.product_incentivized2 <- reviews.product_incentivized2 %>%
  group_by(product_cat, date) %>%
  mutate(day_rating = mean(rating))

## mean rating by week
reviews.product_non1 <- reviews.product_non1 %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

reviews.product_incentivized1 <- reviews.product_incentivized1 %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

reviews.product_non2 <- reviews.product_non2 %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

reviews.product_incentivized2 <- reviews.product_incentivized2 %>%
  group_by(product_cat, year, week(date)) %>%
  mutate(week_rating = mean(rating))

## mean rating by month
reviews.product_non1 <- reviews.product_non1 %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

reviews.product_incentivized1 <- reviews.product_incentivized1 %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

reviews.product_non2 <- reviews.product_non2 %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

reviews.product_incentivized2 <- reviews.product_incentivized2 %>%
  group_by(product_cat, month) %>%
  mutate(month_rating = mean(rating))

## plot by day
ggplot(NULL, aes(x = date, y = day_rating))+
  geom_point(data=reviews.product_incentivized1, aes(color = "incentivized-before"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non1, aes(color = "non-incentivized-before"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_incentivized2, aes(color = "incentivized-after"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non2, aes(color = "non-incentivized-after"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product_incentivized1,method = 'auto',aes(color='incentivized-before-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non1,method = 'auto',aes(color='non-incentivized-before-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_incentivized2,method = 'auto',aes(color='incentivized-after-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non2,method = 'auto',aes(color='non-incentivized-after-line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='day',y='mean rating',fill='category',title='Product Category Mean Rating by Day')

## by week
ggplot(NULL, aes(x = weeks, y = week_rating))+ 
  geom_point(data=reviews.product_incentivized1, aes(color = "incentivized-before"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non1, aes(color = "non-incentivized-before"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_incentivized2, aes(color = "incentivized-after"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non2, aes(color = "non-incentivized-after"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product_incentivized1,method = 'auto',aes(color='incentivized-before-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non1,method = 'auto',aes(color='non-incentivized-before-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_incentivized2,method = 'auto',aes(color='incentivized-after-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non2,method = 'auto',aes(color='non-incentivized-after-line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='week',y='mean rating',fill='category',title='Product Category Mean Rating by Week')

## by month
ggplot(NULL, aes(x = month, y = month_rating, color = product_cat))+
  geom_point(data=reviews.product_incentivized1, aes(color = "incentivized-before"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non1, aes(color = "non-incentivized-before"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_incentivized2, aes(color = "incentivized-after"), alpha = 0.7,size=0.2)+
  geom_point(data=reviews.product_non2, aes(color = "non-incentivized-after"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product_incentivized1,method = 'auto',aes(color='incentivized-before-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non1,method = 'auto',aes(color='non-incentivized-before-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_incentivized2,method = 'auto',aes(color='incentivized-after-line'),size=1,alpha = 0.6)+
  geom_smooth(data=reviews.product_non2,method = 'auto',aes(color='non-incentivized-after-line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-02'), color = "black", size=0.3)+
  labs(x='month',y='mean rating',fill='category',title='Product Category Mean Rating by Month')





