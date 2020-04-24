## The purpose of this script is to merge reviews2 and reviews3

reviews2.csv <- read.csv("~/Dropbox/Eugenie/data/processed/processed-reviews2.csv")
reviews3.csv <- read.csv("~/Dropbox/Eugenie/data/processed/processed-reviews3.csv")

# Get the common columns
reviews2.cm <- reviews2.csv[,!(names(reviews2.csv) %in% c("phone_batteries","phone_cables","screen_protectors"))]
reviews3.cm <- reviews3.csv[,!(names(reviews3.csv) %in% c("tablets","cell_phones"))]

# Merge the common columns
reviews.cm <- rbind(reviews2.cm, reviews3.cm)

# Create a binary column for each product category
reviews.cm['phone_batteries'] <- ifelse(reviews.cm$product_cat == 'phone_batteries', 1, 0)
reviews.cm['phone_cables'] <- ifelse(reviews.cm$product_cat == 'phone_cables', 1, 0)
reviews.cm['screen_protectors'] <- ifelse(reviews.cm$product_cat == 'screen_protectors', 1, 0)
reviews.cm['tablets'] <- ifelse(reviews.cm$product_cat == 'tablets', 1, 0)
reviews.cm['cell_phones'] <- ifelse(reviews.cm$product_cat == 'cell_phones', 1, 0)

# Save the results
write.csv(reviews.cm, file = "merged-reviews.csv",row.names=FALSE)
