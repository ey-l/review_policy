# This file is used to extract user_id's from the review data 
# to obtain all the reviews written by a user

# Load review data
source("~/Dropbox/Eugenie/scripts/eugenie-reviews.R")

# Get user_id, drop duplicates
user_ids <- as.data.frame(reviews2.csv$user_id) %>% distinct()

# Rename the column
names(user_ids) <- 'user_id'

# Create a .csv file and store the data
write.csv(user_ids, file = "user_ids.csv",row.names=FALSE)
