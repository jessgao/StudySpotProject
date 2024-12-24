import os
import json
import pandas as pd
from dotenv import load_dotenv
import serpapi

# each SerpAPI account has a unique api key to perform searches
# this reads our .env file for our SerpAPI key so that we can scrape in Python
load_dotenv('apikey.env', override = True)

api_key = os.getenv('SERPAPI_KEY')

locations = []
# SerpAPI has a limit of 100 searches per month, so we will use 40 on the locations and 40 for each location's reviews
for i in range (0, 41, 20):
    client = serpapi.Client(api_key=api_key)
    locs = client.search({
        'engine': 'google_maps', # desired search engine
        'type': 'search',
        'q': 'places to study', # search query
        'll': '@34.07100342918671,-118.4448019289779,15z', # starting location
        'start': i
    })

# compile search results into a dataframe
    locs_dict = locs.as_dict()
    if 'local_results' in locs_dict:
        locs_df = pd.json_normalize(locs_dict, 'local_results')
        locations.append(locs_df)
locations_df = pd.concat(locations, ignore_index = True)

#include only necessary columns
loc_cols = ['title', 'place_id', 'rating', 'reviews', 'type', 'address', 'gps_coordinates.latitude', 'gps_coordinates.longitude',
            'operating_hours.monday', 'operating_hours.tuesday', 'operating_hours.wednesday', 'operating_hours.thursday',
            'operating_hours.friday', 'operating_hours.saturday', 'operating_hours.sunday']
locations_df = locations_df[loc_cols]
locations_df

reviews = []
# reviews search by id from locations search
for id in locations_df['place_id']:
    place_reviews = client.search({
        'engine': 'google_maps_reviews', # different search engine
        'type': 'search',
        'place_id': id, # search by id
        'sort_by': 'mostRecent' # return 8 most recent reviews, for consistency
    })
    # append reviews data to list
    place_reviews_dict = place_reviews.as_dict()['reviews']
    df = pd.json_normalize(place_reviews_dict)
    df['place_id'] = id
    reviews.append(df)

# create reviews dataframe with desired columns
reviews_df = pd.concat(reviews, ignore_index=True)
rev_cols = ['place_id', 'rating', 'iso_date', 'likes', 'extracted_snippet.original', 'details.service', 'details.food', 'details.atmosphere']
reviews_df = reviews_df[rev_cols]

reviews_df = reviews_df.set_index('place_id')
reviews_df = reviews_df.reset_index()
reviews_df
