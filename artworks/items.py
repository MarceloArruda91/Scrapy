from typing import Optional, Dict, Union
import scrapy


class ArtItem(scrapy.Item):
    """
    Scrapy Item representing information about an art piece.

    Attributes:
        artist (str): The artist's name.
        title (str): The title of the art piece.
        description (str): A description of the art piece.
        image (str): URL of the art piece's image.
        url (str): URL of the art piece's page.
        height (float): The height dimension of the art piece (in cm).
        width (float): The width dimension of the art piece (in cm).
        categories (list of str): Categories associated with the art piece.
    """

    artist = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    image = scrapy.Field()
    url = scrapy.Field()
    width = scrapy.Field()
    height = scrapy.Field()
    categories = scrapy.Field()

    def to_dict(
        self, omit_none: Optional[bool] = True
    ) -> Dict[str, Union[str, float, list]]:
        """
        Convert the ArtItem instance to a dictionary and optionally omit None values.

        Args:
            omit_none (bool, optional): Whether to omit fields with None values. Default is True.

        Returns:
            dict: A dictionary representation of the ArtItem.
        """
        if omit_none:
            return {key: value for key, value in self.items() if value is not None}
        return super()
