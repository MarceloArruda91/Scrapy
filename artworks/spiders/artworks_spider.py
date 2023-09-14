import re
from typing import Dict, Union, List
import scrapy

from ..enum.options import Options
from ..items import ArtItem


class TrialSpider(scrapy.Spider):
    """
    A Scrapy spider for scraping art information from a website.
    """

    name = "artworks"
    start_urls = ["http://pstrial-2019-12-16.toscrape.com/browse/"]
    categories = []

    @staticmethod
    def _verify_category(categories: List[str], subcat_text: str) -> bool:
        """
        Check if the provided subcategory text is valid.

        Args:
            categories (List[str]): List of categories.
            subcat_text (str): Subcategory text to verify.

        Returns:
            bool: True if the subcategory text is valid, otherwise False.
        """

        if subcat_text in Options.categories:
            return True
        if categories:
            return True

    @staticmethod
    def _extract_with_css(response: scrapy.http.Response, query: str) -> str:
        """
        Extract content from the response using a CSS selector.

        Args:
            response (scrapy.http.Response): Scrapy HTTP response object.
            query (str): CSS selector query.

        Returns:
            str: Extracted content.
        """

        return response.css(query).get(default="").strip()

    @staticmethod
    def _extract_dimensions(input_string: str) -> Union[None, Dict[str, float]]:
        """
        Extract dimensions from an input string.

        Args:
            input_string (str): Input string containing dimensions.

        Returns:
            Union[None, Dict[str, float]]: A dictionary with 'height' and 'width' keys
                                           or None if dimensions are not found.
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
        Parse the art title.

        Args:
            art_title (str): Art title to parse.

        Returns:
            Union[str, None]: Parsed art title or None if it cannot be parsed.
        """

        result = re.sub(r"^untitled\s*,*", "", art_title, flags=re.IGNORECASE)
        result = re.sub(r"^([\[(])(.+?)([])])$", r"\2", result)

        return result.strip() if result else None

    def parse(self, response: scrapy.http.Response, categories: List[str] = []):
        """
        Parse the main page and follow subcategories.

        Args:
            response (scrapy.http.Response): Scrapy HTTP response object.
            categories (List[str], optional): List of categories. Defaults to [].
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
        Parse art URLs on a page.

        Args:
            response (scrapy.http.Response): Scrapy HTTP response object.
            categories (List[str]): List of categories.
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
        Parse art information on a page.

        Args:
            response (scrapy.http.Response): Scrapy HTTP response object.
            categories (List[str]): List of categories.
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
