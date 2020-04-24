########################## load source files ############################
source("~/Dropbox/Eugenie/scripts/utils.R")


## add category data as extra columns
reviews2.temp <- reviews2.csv
reviews2.temp <- reviews2.temp[as.numeric(as.character(reviews2.temp$year))>2013,]
reviews2.temp <- reviews2.temp[reviews2.temp$product_cat != 'none',]

reviews.product <- reviews2.temp[,c('recid','item_id','incentivized','product_cat','rating','word_count','helpful_yes',
                                    'date','year','month','week')]

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

## plot by week
ggplot(NULL, aes(x = week, y = week_rating))+
  geom_point(data=reviews.product, aes(color = "weekly ave rating"), alpha = 0.7,size=0.2)+
  geom_smooth(data=reviews.product,method = 'auto',aes(color='weekly ave rating line'),size=1,alpha = 0.6)+
  theme_minimal()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  labs(x='day',y='mean rating',fill='category',title='Product Category Mean Rating by Week')

## percentage of rating vs. week
ggplot(data=reviews.product, aes(week))+
  geom_bar(aes(fill=as.factor(rating)), position="fill")+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  scale_fill_brewer(palette="RdBu")+
  ylab('proportion')

## count
ggplot(reviews.product, aes(week, fill=as.factor(rating)))+
  geom_bar()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  scale_fill_brewer(palette="RdBu")


########################## incentivized ############################

## percentage of rating vs. week
ggplot(data=reviews.product, aes(week))+
  geom_bar(aes(fill=incentivized), position="fill")+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  ylab('proportion')

## count
ggplot(reviews.product, aes(week, fill=incentivized))+
  geom_bar()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)


########################## review length ############################
bins <- c(-1,50,100,200,500,Inf)
reviews.product['word_count.binned'] <- cut(reviews.product$word_count, 
                                        breaks=bins, labels=c('0-50','50-100','100-200','200-500','500+'))
reviews.product$word_count.binned <- as.factor(reviews.product$word_count.binned)

## percentage of rating vs. week
ggplot(data=reviews.product, aes(week))+
  geom_bar(aes(fill=word_count.binned), position="fill")+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  scale_fill_brewer(palette="RdBu")+
  ylab('proportion')

## count
ggplot(reviews.product, aes(week, fill=word_count.binned))+
  geom_bar()+
  facet_grid(rows=vars(product_cat))+
  geom_vline(xintercept = as.Date('2016-10-03'), color = "black", size=0.3)+
  scale_fill_brewer(palette="RdBu")

