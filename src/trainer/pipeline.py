import pandas as pd
import src.trainer.db as write
import src.server.db as read
import src.trainer.date as date
import src.trainer.geo as geo

# load flickr pictures
photos = read.flickr_photo()

print(photos)
# # filter 
# valid_geo = geo.processing.first_filter(photos)
# valid_dates = date.processing.first_filter(photos)
# write.mark_photo(valid_geo)
# write.mark_photo(valid_dates)

# # sample

# """
# start the app
# - shows status
# - check flickr for updates
# - download new pics

# - load data
# - filtered_status
# - filter

# """