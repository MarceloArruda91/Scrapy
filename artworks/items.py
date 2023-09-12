# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ArtworksItem(scrapy.Item):
    url = scrapy.Field(serializer=str)
    artist = scrapy.Field(serializer=list)
    title = scrapy.Field(serializer=str)
    image = scrapy.Field(serializer=str)
    height = scrapy.Field(serializer=float)
    width = scrapy.Field(serializer=float)
    description = scrapy.Field(serializer=str)
    categories = scrapy.Field(serializer=list)
