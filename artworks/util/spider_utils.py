import re
from typing import Dict, Union
import scrapy

from ..enum.options import Options


class SpiderUtils:
    @staticmethod
    def verify_category(categories: list[str], subcat_text: str) -> bool:
        """
        Verify if a subcategory is in the list of allowed categories.

        :param categories: List of allowed categories.
        :param subcat_text: The subcategory text to check.
        :return: True if the subcategory is in the list or if there are any categories; otherwise, False.
        """
        if subcat_text in Options.categories:
            return True
        if categories:
            return True

    @staticmethod
    def extract_with_css(response: scrapy.http.Response, query: str) -> str:
        """
        Extract data from the response using a CSS query.

        :param response: The response object.
        :param query: CSS query to extract data.
        :return: Extracted data as a string.
        """
        return response.css(query).get(default="").strip()

    @staticmethod
    def extract_dimensions(input_string: str) -> Union[None, Dict[str, float]]:
        """
        Extract dimensions (height and width) from a string.

        :param input_string: The input string containing dimensions.
        :return: A dictionary with 'height' and 'width' keys, or None if no dimensions are found.
        """
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

    @staticmethod
    def extract_title(art_title: str) -> Union[str, None]:
        """
        Extract and clean an artwork title.

        :param art_title: The artwork title to extract and clean.
        :return: Cleaned artwork title as a string, or None if no valid title is found.
        """
        result = re.sub(r"^untitled\s*,*", "", art_title, flags=re.IGNORECASE)
        result = re.sub(r"^([\[(])(.+?)([])])$", r"\2", result)

        return result.strip() if result else None
