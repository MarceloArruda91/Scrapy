import re
from typing import Dict, List, Union

import scrapy


class Extract:
    @staticmethod
    def extract_with_css(response: scrapy.http.Response, query: str) -> str:
        """
        Extract data from a Scrapy response using a CSS selector.

        :param response: The Scrapy response object.
        :param query: The CSS selector query.
        :return: The extracted data as a string.
        """
        return response.css(query).get(default="").strip()

    @classmethod
    def extract_artist(cls, response: scrapy.http.Response) -> List[str]:
        """
        Extract artist information from the response.

        :param response: The Scrapy response object.
        :return: List of extracted artist names.
        """
        artist_text = cls.extract_with_css(response=response, query="h2::text")
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
                if not (artist.upper().startswith("AFTER"))
                and (artist.upper() != "N/E")
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
                return {"width": float(values[0]), "height": float(values[2])}
        else:
            return None

    @classmethod
    def extract_title(
        cls, response: scrapy.http.Response
    ) -> Union[Dict[str, Union[str, None]]]:
        """
        Extract artwork title and description from the response.

        :param response: The Scrapy response object.
        :return: A dictionary with 'title' and 'description' keys, where values are strings or None.
        """
        art_title = cls.extract_with_css(response=response, query="h1::text")

        title = re.sub(r"^untitled\s*,*", "", art_title, flags=re.IGNORECASE)

        clean_text = re.sub(r"^([\[(])(.+?)([])])$", r"\2", title).strip()

        is_description = (title.startswith("[") and title.endswith("]")) or (
            title.startswith("(") and title.endswith(")")
        )
        if is_description:
            return {"title": None, "description": clean_text}
        else:
            return {"title": clean_text, "description": None}

    @classmethod
    def extract_description(cls, response, title):
        """
        Extract artwork description from the response.

        :param response: The Scrapy response object.
        :param title: A dictionary with 'title' and 'description' keys.
        :return: A string containing the artwork description.
        """
        description = cls.extract_with_css(response, "p::text")

        if description and title["description"]:
            return description + ", " + title["description"]
        elif description:
            return description
        elif title["description"]:
            return title["description"]
