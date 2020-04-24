########################## load library ############################
## for data manipulation
library(plyr)
library(dplyr)
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


############################ load data #############################
## load raw data
reviews2.csv <- read.csv('~/Dropbox/Eugenie/data/arslan-reviews2.csv')


############ data exploratory analysis for review2.csv #############

## turn numeric values to factors
reviews2.csv$is_deleted <- as.factor(reviews2.csv$is_deleted)
reviews2.csv$incentivized <- as.factor(reviews2.csv$incentivized)
reviews2.csv$verified_purchaser <- as.factor(reviews2.csv$verified_purchaser)

levels(reviews2.csv$verified_purchaser) <- c("unverified", "verified")
levels(reviews2.csv$incentivized) <- c("non-incentivized", "incentivized")
levels(reviews2.csv$is_deleted) <- c("kept", "deleted")


## explore the counts of each group
reviews2.summary <- data.frame(table(reviews2.csv[,c('incentivized', 'is_deleted', 'verified_purchaser')]))

## get the percentage of each group
reviews2.summary2 <- data.frame(table(reviews2.csv[,c('is_deleted', 'verified_purchaser', 'incentivized')]))
reviews2.summary2 <- ddply(reviews2.summary2, .(), mutate, Freq_pct = Freq/sum(Freq)*100)

## get the percentage of each group
reviews2.summary <- data.frame(table(reviews2.csv[,c('verified_purchaser', 'incentivized', 'is_deleted')]))
reviews2.summary <- ddply(reviews2.summary, .(is_deleted), mutate, Freq_pct = Freq/sum(Freq)*100)

## cast for readibility
cast(reviews2.summary, verified_purchaser~incentivized~is_deleted, mean, value = 'Freq_pct')

## cast to a matrix for readibility
reviews2.summary.matrix <- cast(reviews2.summary, incentivized~is_deleted~verified_purchaser, mean, value = 'Freq_pct')

## correlation of the groups
reviews2.corr.matrix <- reviews2.csv[,c('incentivized', 'is_deleted', 'verified_purchaser')]

## chi-square tests
chisq.test(reviews2.csv$incentivized, reviews2.csv$is_deleted, correct = FALSE)
chisq.test(reviews2.csv$incentivized, reviews2.csv$verified_purchaser, correct = FALSE)
chisq.test(reviews2.csv$is_deleted, reviews2.csv$verified_purchaser, correct = FALSE)


## Goodman and Kruskal's tau to calculate the effect size (strength of association)
reviews2.temp <- reviews2.csv[,c('incentivized', 'is_deleted', 'verified_purchaser')]
GKmatrix1<- GKtauDataframe(reviews2.temp)
plot(GKmatrix1, corrColors = "blue")


## get the mean of incentivized vs. non-incentivized reviews
aggregate(reviews2.csv[, 'rating'], list(reviews2.csv$incentivized), mean)
aggregate(reviews2.csv[, 'rating'], list(reviews2.csv$incentivized, reviews2.csv$item_id), mean)

## get the mean of is_deleted vs. non-deleted reviews
aggregate(reviews2.csv[, 'rating'], list(reviews2.csv$is_deleted), mean)
aggregate(reviews2.csv[, 'rating'], list(reviews2.csv$is_deleted, reviews2.csv$item_id), mean)

## get the mean of verified_purchaser vs. non-verified_purchaser reviews
aggregate(reviews2.csv[, 'rating'], list(reviews2.csv$verified_purchaser), mean)
aggregate(reviews2.csv[, 'rating'], list(reviews2.csv$verified_purchaser, reviews2.csv$item_id), mean)


## plot incentivized vs. non-incentivized reviews
p1 <- ggplot(reviews2.csv[reviews2.csv$incentivized == 'incentivized',], aes(x=rating)) + 
  geom_bar(fill='#00AFBB') +
  geom_text(stat='count', aes(label=..count..), vjust=-1)
p0 <- ggplot(reviews2.csv[reviews2.csv$incentivized == 'non-incentivized',], aes(x=rating)) + 
  geom_bar(fill='#FFDB6D') +
  geom_text(stat='count', aes(label=..count..), vjust=-1)
ggarrange(p0, p1,
          labels = c("non-incentivized", "incentivized"),
          ncol = 2, nrow = 1)

## plot is_deleted vs. non-deleted reviews
p1 <- ggplot(reviews2.csv[reviews2.csv$is_deleted == 'deleted',], aes(x=rating, fill=incentivized)) + geom_bar()
p0 <- ggplot(reviews2.csv[reviews2.csv$is_deleted == 'kept',], aes(x=rating, fill=incentivized)) + geom_bar()
ggarrange(p0, p1,
          labels = c("undeleted", "is_deleted"),
          ncol = 2, nrow = 1)

## plot verified_purchaser vs. non-verified_purchaser reviews, fill with incentivized
p1 <- ggplot(reviews2.csv[reviews2.csv$verified_purchaser == 'verified',], aes(x=rating, fill=incentivized)) + geom_bar()
p0 <- ggplot(reviews2.csv[reviews2.csv$verified_purchaser == 'unverified',], aes(x=rating, fill=incentivized)) + geom_bar()
ggarrange(p0, p1,
          labels = c("non-verified_purchaser", "verified_purchaser"),
          ncol = 2, nrow = 1)

## plot verified_purchaser vs. non-verified_purchaser reviews, fill with is_deleted
p1 <- ggplot(reviews2.csv[reviews2.csv$verified_purchaser == 'verified',], aes(x=rating, fill=is_deleted)) + geom_bar()
p0 <- ggplot(reviews2.csv[reviews2.csv$verified_purchaser == 'unverified',], aes(x=rating, fill=is_deleted)) + geom_bar()
ggarrange(p0, p1,
          labels = c("non-verified_purchaser", "verified_purchaser"),
          ncol = 2, nrow = 1)

## plot percentage distribution: incentivized
reviews2.csv$rating <- as.factor(reviews2.csv$rating)

p1 <- ggplot(data=reviews2.csv, aes(incentivized))+
  geom_bar(aes(fill=rating), position="fill")+
  scale_fill_brewer(palette="RdBu")

p1 <- ggplotly(p1)

## plot percentage distribution: is_deleted
p2 <- ggplot(data=reviews2.csv, aes(is_deleted))+
  geom_bar(aes(fill=rating), position="fill")+
  scale_fill_brewer(palette="RdBu")

p2 <- ggplotly(p2)

## plot percentage distribution: verified_purchaser
p3 <- ggplot(data=reviews2.csv, aes(verified_purchaser))+
  geom_bar(aes(fill=rating), position="fill")+
  scale_fill_brewer(palette="RdBu")

p3 <- ggplotly(p3)

subplot(
  style(p1, showlegend = FALSE),
  style(p2, showlegend = FALSE),
  p3, 
  nrows = 1, margin = 0.005,
  shareY = TRUE, titleX = TRUE
)

## plot the proportion of groups
p1 <- ggplot(data=reviews2.csv, aes(incentivized))+
  geom_bar(aes(fill=is_deleted), position="fill")

p2 <- ggplot(data=reviews2.csv, aes(incentivized))+
  geom_bar(aes(fill=verified_purchaser), position="fill")

p3 <- ggplot(data=reviews2.csv, aes(is_deleted))+
  geom_bar(aes(fill=verified_purchaser), position="fill")

## plot three groups together with a mosaic plot
ggplot(data = reviews2.csv) +
  geom_mosaic(aes(x = product(incentivized, is_deleted), fill=incentivized), na.rm=TRUE)+
  facet_grid(verified_purchaser~.)+
  labs(x='is deleted?', y='is incentivized?')

ggplotly(ggplot(data = reviews2.csv) +
  geom_mosaic(aes(x = product(verified_purchaser, is_deleted), fill=incentivized), na.rm=TRUE)+
  labs(x='is deleted?', y='is verified?'))

############ general linear regression for review2.csv #############

## formula 1 hypothesis: non-/incentivized group give different ratings
F1 <- rating ~ incentivized
F1_lm <- gam(data = reviews2.csv, formula = F1)
# get the model summary
summary(F1_lm)
# check the diagnostic plots
#par(mar=c(1,1,1,1))
#gam.check(F1_lm)

## formula 2 hypothesis: non-/is_deleted group give different ratings
F2 <- rating ~ is_deleted
F2_lm <- gam(data = reviews2.csv, formula = F2)
# get the model summary
summary(F2_lm)

## formula 3 hypothesis: non-/verified_purchaser group give different ratings
F3 <- rating ~ verified_purchaser
F3_lm <- gam(data = reviews2.csv, formula = F3)
# get the model summary
summary(F3_lm)

## formula 4 hypothesis with interacts
F4 <- rating ~ incentivized * is_deleted * verified_purchaser
F4_lm <- gam(data = reviews2.csv, formula = F4)
# get the model summary
summary(F4_lm)

## formula 5 hypothesis
F5 <- rating ~ incentivized + is_deleted + verified_purchaser
F5_lm <- gam(data = reviews2.csv, formula = F5)
# get the model summary
summary(F5_lm)


############ linear fixed effect model for review2.csv #############

# in model.fe, index = c('item_id') defines 'item_id' as the entity
formula.fe <- rating ~ incentivized + is_deleted + verified_purchaser
model.fe <- plm(data = reviews2.csv, formula = formula.fe, index = c('item_id'), model = 'within')
# get the model summary
summary(model.fe)


############ linear pooling model for review2.csv #################

# in model.pooled, index = c('item_id') defines 'item_id' as the entity
model.pooled <- plm(data = reviews2.csv, formula = formula.fe, index = c('item_id'), model = 'pooling')
# get the model summary
summary(model.pooled)

## the result shows the null hypothesis of no fixed effects is rejected
pFtest(model.fe, model.pooled)


############ linear random effect model for review2.csv #################

## random effect test
## the null hypothesis of zero variance in individual-specific errors is rejected
## therefore, heterogeneity among individuals may be significant
plmtest(model.pooled, effect="individual")

## model
model.ran <- plm(data = reviews2.csv, formula = formula.fe, index = c('item_id'), model = 'random')
# get the model summary
summary(model.ran)

## however the null hypothesis of "individual random effects are exogenous" is rejected
## seems that fixed effect model is the solution
phtest(model.fe, model.ran)




