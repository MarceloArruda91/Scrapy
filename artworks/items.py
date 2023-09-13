import scrapy


class ArtItem(scrapy.Item):
    """Oi"""

    artist = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    height = scrapy.Field()
    width = scrapy.Field()
    categories = scrapy.Field()

    # Define a to_dict method to convert the item to a dictionary and omit empty fields
    def to_dict(self, omit_none=True):
        """Oi"""
        if omit_none:
            return {key: value for key, value in self.items() if value is not None}
        return super()
