import re
import scrapy
from ..enum.options import Options


class SpiderUtils:
    @staticmethod
    def extract_with_css(response: scrapy.http.Response, query: str) -> str:
        """
        Extract text from the response using a CSS selector.

        Args:
            response (scrapy.http.Response): The response from the URL.
            query (str): The CSS selector query.

        Returns:
            str: The extracted text or an empty string if not found.
        """
        return response.css(query).get(default="").strip()

    @staticmethod
    def verify_category(categories: list, subcat_text: str) -> bool:
        """
        Verify if a subcategory matches the desired categories.

        Args:
            categories (list): The list of desired categories.
            subcat_text (str): The text of the subcategory.

        Returns:
            bool: True if the subcategory matches any desired category or if categories is not empty; False otherwise.
        """
        if subcat_text in Options.categories:
            return True
        if categories:
            return True

    def extract_artist(self, response: scrapy.http.Response, query: str) -> list:
        """
        Extract artist information from the response.

        Args:
            response (scrapy.http.Response): The response from the URL.
            query (str): The CSS selector query for artist information.

        Returns:
            list: A list of filtered artist names.
        """
        artist_text = self.extract_with_css(response=response, query=query)
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

    @staticmethod
    def extract_dimensions(response: scrapy.http.Response, query: str) -> dict:
        """
        Extract artwork dimensions from the response.

        Args:
            response (scrapy.http.Response): The response from the URL.
            query (str): The XPath query for dimensions information.

        Returns:
            dict: A dictionary with 'height' and 'width' keys representing dimensions.
                  Returns None if dimensions are not found.
        """
        input_string = response.xpath(query).get()

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

    def extract_title(self, response: scrapy.http.Response, query: str) -> str:
        """
        Extract the artwork title from the response.

        Args:
            response (scrapy.http.Response): The response from the URL.
            query (str): The CSS selector query for the artwork title.

        Returns:
            str: The extracted artwork title or None if not found.
        """
        art_title = self.extract_with_css(response=response, query=query)

        result = re.sub(r"^untitled\s*,*", "", art_title, flags=re.IGNORECASE)
        result = re.sub(r"^([\[(])(.+?)([])])$", r"\2", result)

        return result.strip() if result else None
