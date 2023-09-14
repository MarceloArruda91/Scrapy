from typing import List
import scrapy
from ..items import ArtItem
from ..util.spider_utils import SpiderUtils


class TrialSpider(scrapy.Spider):
    """
    A Scrapy spider for scraping artworks.

    """

    name: str = "artworks"
    start_urls: List[str] = ["http://pstrial-2019-12-16.toscrape.com/browse/"]
    categories: List[str] = []

    def __init__(self) -> None:
        """
        Initialize the spider and set up utility functions.
        """
        super().__init__()
        self.spider_utils = SpiderUtils()

    def parse(
        self, response: scrapy.http.Response, categories: List[str] = []
    ) -> scrapy.Request:
        """
        Parse the response for subcategories and art URLs.

        Args:
            response (scrapy.http.Response): The response from the URL.
            categories (List[str], optional): The list of categories. Defaults to [].

        Returns:
            scrapy.Request: A request to follow URLs for subcategories and art.
        """
        subcat = response.xpath('//*[(@id = "subcats")]/div')
        if subcat:
            anchors = subcat.xpath(".//a[h3]")
            for anchor in anchors:
                subcat_text = anchor.css("::text").get()
                if self.spider_utils.verify_category(categories, subcat_text):
                    temp_list = categories.copy()
                    temp_list.append(subcat_text)
                    yield response.follow(
                        url=anchor.attrib["href"],
                        callback=self.parse,
                        cb_kwargs={"categories": temp_list},
                    )

        yield from self.parse_art_urls(response, categories)

    def parse_art_urls(
        self, response: scrapy.http.Response, categories: List[str]
    ) -> scrapy.Request:
        """
        Parse art URLs from the response.

        Args:
            response (scrapy.http.Response): The response from the URL.
            categories (List[str]): The list of categories.

        Returns:
            scrapy.Request: A request to follow art URLs.
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

    def parse_art(
        self, response: scrapy.http.Response, categories: List[str]
    ) -> ArtItem:
        """
        Parse art information from the response.

        Args:
            response (scrapy.http.Response): The response from the URL.
            categories (List[str]): The list of categories.

        Returns:
            ArtItem: An instance of ArtItem containing art information.
        """
        item = ArtItem()

        artist = self.spider_utils.extract_artist(response=response, query="h2::text")
        if artist:
            item["artist"] = artist

        title = self.spider_utils.extract_title(response=response, query="h1::text")
        if title:
            item["title"] = title

        description = self.spider_utils.extract_with_css(response, "p::text")
        if description:
            item["description"] = description

        item["image"] = (
            "http://pstrial-2019-12-16.toscrape.com" + response.css("img").attrib["src"]
        )

        item["url"] = response.url

        dimensions_dict = self.spider_utils.extract_dimensions(
            response=response,
            query='//td[@class="key" and text('
            ')="Dimensions"]/following-sibling::td[ '
            '@class="value"]/text()',
        )
        if dimensions_dict:
            item["height"] = dimensions_dict["height"]
            item["width"] = dimensions_dict["width"]

        item["categories"] = categories
        return item
