import re
from typing import Dict, List, Union

import scrapy
from ..enum.options import Options


class SpiderUtils:
    @staticmethod
    def extract_with_css(response: scrapy.http.Response, query: str) -> str:
        """
        Extract data from response using a CSS selector.

        :param response: The Scrapy response object.
        :param query: The CSS selector query.
        :return: The extracted data as a string.
        """
        return response.css(query).get(default="").strip()

    @staticmethod
    def verify_category(categories: List[str], subcat_text: str) -> bool:
        """
        Verify if a given subcategory text is in the list of categories.

        :param categories: List of categories.
        :param subcat_text: Subcategory text to be verified.
        :return: True if subcat_text is in categories or if categories is not empty, else False.
        """
        if subcat_text in Options.categories:
            return True
        if categories:
            return True
        return False

    def extract_artist(self, response: scrapy.http.Response) -> List[str]:
        """
        Extract artist information from the response.

        :param response: The Scrapy response object.
        :return: List of extracted artist names.
        """
        artist_text = self.extract_with_css(response=response, query="h2::text")
        if artist_text:
            artist = [artist.strip() for artist in artist_text.split(";")]
            artist_list = [
                re.search(r":\s*(.*)", artist).group(1)
                for artist in artist
                if re.search(r":\s*(.*)", artist)
            ]
            filtered_artists = [
                artist
                for artist in artist_list
                if not artist.upper().startswith("AFTER")
            ]

            return filtered_artists
        else:
            return []

    @staticmethod
    def extract_dimensions(
        response: scrapy.http.Response,
    ) -> Union[None, Dict[str, float]]:
        """
        Extract dimensions (height and width) from the response.

        :param response: The Scrapy response object.
        :param query: The XPath query to extract dimensions.
        :return: A dictionary with 'height' and 'width' keys containing float values, or None if not found.
        """
        input_string = response.xpath(
            '//td[@class="key" and text('
            ')="Dimensions"]/following-sibling::td[ '
            '@class="value"]/text()'
        ).get()

        if not input_string:
            return None
        match = re.search(r"\((\d[^)]+)\)", input_string)

        if match:
            values = (
                match.group(0)
                .replace("(", "")
                .replace(")", "")
                .replace("cm", "")
                .split()
            )

            if len(values) > 1:
                return {"height": float(values[0]), "width": float(values[2])}
        else:
            return None

    def extract_title(
        self, response: scrapy.http.Response
    ) -> Union[Dict[str, Union[str, None]]]:
        """
        Extract artwork title and description from the response.

        :param response: The Scrapy response object.
        :return: A dictionary with 'title' and 'description' keys, where values are strings or None.
        """
        art_title = self.extract_with_css(response=response, query="h1::text")

        title = re.sub(r"^untitled\s*,*", "", art_title, flags=re.IGNORECASE)

        clean_text = re.sub(r"^([\[(])(.+?)([])])$", r"\2", title).strip()

        is_description = (title.startswith("[") and title.endswith("]")) or (
            title.startswith("(") and title.endswith(")")
        )
        if is_description:
            return {"title": None, "description": clean_text}
        else:
            return {"title": clean_text, "description": None}

    def extract_description(self, response, title):
        """
        Extract artwork description from the response.

        :param response: The Scrapy response object.
        :param title: A dictionary with 'title' and 'description' keys.
        :return: A string containing the artwork description.
        """
        description = self.extract_with_css(response, "p::text")

        if description and title["description"]:
            return description + ", " + title["description"]
        elif description:
            return description
        elif title["description"]:
            return title["description"]
