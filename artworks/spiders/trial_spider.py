import re
from typing import Dict, Union, List
import scrapy
from ..items import ArtItem
from ..enum.options import Options


class TrialSpider(scrapy.Spider):
    """
    A Scrapy spider for scraping art-related data from a website.

    Attributes:
        name (str): The name of the spider.
        start_urls (List[str]): The list of starting URLs for the spider.
        categories (List[str]): A list to store the categories of art items.

    Methods:
        _verify_category(categories: List[str], subcat_text: str) -> bool:
            Check if a subcategory is valid or if there are any categories available.
        _extract_with_css(response: scrapy.http.Response, query: str) -> str:
            Extract data from a Scrapy response using a CSS selector.
        _extract_dimensions(input_string: str) -> Union[None, Dict[str, float]]:
            Extract dimensions (height and width) from a string.
        _parse_title(art_title: str) -> Union[str, None]:
            Parse and clean an art title.

        parse(response: scrapy.http.Response, categories: List[str]):
            Parse the main response and follow subcategory links.
        parse_art_urls(response: scrapy.http.Response, categories: List[str]):
            Parse art item URLs and follow pagination links.
        parse_art(response: scrapy.http.Response, categories: List[str]):
            Parse and extract data from individual art item pages.
    """

    name = "trial"
    start_urls = ["http://pstrial-2019-12-16.toscrape.com/browse/"]
    categories = []

    @staticmethod
    def _verify_category(categories: List[str], subcat_text: str) -> bool:
        """
        Check if a subcategory is valid or if there are any categories available.

        Args:
            categories (List[str]): A list of categories.
            subcat_text (str): Text representing a subcategory.

        Returns:
            bool: True if the subcategory is valid or if categories exist, otherwise False.
        """

        if subcat_text in Options.categories:
            return True
        if categories:
            return True

    @staticmethod
    def _extract_with_css(response: scrapy.http.Response, query: str) -> str:
        """
        Extract data from a Scrapy response using a CSS selector.

        Args:
            response (scrapy.http.Response): The Scrapy response object.
            query (str): The CSS selector query.

        Returns:
            str: Extracted data as a string.
        """

        return response.css(query).get(default="").strip()

    @staticmethod
    def _extract_dimensions(input_string: str) -> Union[None, Dict[str, float]]:
        """
        Extract dimensions (height and width) from a string.

        Args:
            input_string (str): The input string containing dimensions.

        Returns:
            Union[None, Dict[str, float]]: A dictionary containing height and width, or None if not found.
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
    def _parse_title(art_title: str) -> Union[str, None]:
        """
        Parse and clean an art title.

        Args:
            art_title (str): The art title to be parsed.

        Returns:
            Union[str, None]: The cleaned art title or None if it cannot be cleaned.
        """

        result = re.sub(r"^untitled\s*,*", "", art_title, flags=re.IGNORECASE)
        result = re.sub(r"^([\[(])(.+?)([])])$", r"\2", result)

        return result.strip() if result else None

    def parse(self, response: scrapy.http.Response, categories=[]):
        """
        Parse the main response and follow subcategory links.

        Args:
            response (scrapy.http.Response): The Scrapy response object.
            categories (List[str]): A list of categories.
        """

        subcat = response.xpath('//*[(@id = "subcats")]/div')
        if subcat:
            anchors = subcat.xpath(".//a[h3]")
            for anchor in anchors:
                subcat_text = anchor.css("::text").get()
                if self._verify_category(categories, subcat_text):
                    temp_list = categories.copy()
                    temp_list.append(subcat_text)
                    yield response.follow(
                        url=anchor,
                        callback=self.parse,
                        cb_kwargs={"categories": temp_list},
                    )

        yield from self.parse_art_urls(response, categories)

    def parse_art_urls(self, response: scrapy.http.Response, categories: List[str]):
        """
        Parse art item URLs and follow pagination links.

        Args:
            response (scrapy.http.Response): The Scrapy response object.
            categories (List[str]): A list of categories.
        """

        art_urls = response.xpath(
            '//*[@id="body"]/div[2]/a[contains(@href,"/item")]'
        ).css("a")
        if art_urls.get():
            yield from response.follow_all(
                urls=art_urls,
                callback=self.parse_art,
                cb_kwargs={"categories": categories},
            )

            next_page = response.css("[class='nav next'] [name='page']")[0].attrib[
                "value"
            ]
            if response.url[-1:].isnumeric():
                split_url = response.url.split("page=")
                next_url = split_url[0] + "page=" + next_page
                yield response.follow(
                    next_url,
                    callback=self.parse_art_urls,
                    cb_kwargs={"categories": categories},
                )
            else:
                yield response.follow(
                    response.url + "?page=1",
                    callback=self.parse_art_urls,
                    cb_kwargs={"categories": categories},
                )

    def parse_art(self, response: scrapy.http.Response, categories: List[str]):
        """
        Parse and extract data from individual art item pages.

        Args:
            response (scrapy.http.Response): The Scrapy response object.
            categories (List[str]): A list of categories.
        """

        item = ArtItem()
        artists = self._extract_with_css(response, "h2::text")
        if artists:
            artists = [artist.strip() for artist in artists.split(";")]
            item["artist"] = [
                re.search(r":\s*(.*)", artist).group(1)
                for artist in artists
                if re.search(r":\s*(.*)", artist)
            ]

        title = self._parse_title(self._extract_with_css(response, "h1::text"))
        if title:
            item["title"] = title

        description = self._extract_with_css(response, "p::text")
        if description:
            item["description"] = description

        item["image"] = (
            "http://pstrial-2019-12-16.toscrape.com" + response.css("img").attrib["src"]
        )
        item["url"] = response.url
        dimensions = response.xpath(
            '//td[@class="key" and text()="Dimensions"]/following-sibling::td['
            '@class="value"]/text()'
        ).get()
        dimensions_dict = self._extract_dimensions(dimensions)
        if dimensions_dict:
            item["height"] = dimensions_dict["height"]
            item["width"] = dimensions_dict["width"]

        item["categories"] = categories
        yield item
