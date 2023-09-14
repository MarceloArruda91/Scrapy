import re
from typing import List
import scrapy
from ..items import ArtItem
from ..util.spider_utils import SpiderUtils


class TrialSpider(scrapy.Spider):
    """
    A Scrapy spider to scrape artwork information.
    """

    name = "artworks"
    start_urls = ["http://pstrial-2019-12-16.toscrape.com/browse/"]
    categories = []

    def __init__(self):
        super().__init__()
        self.spider_utils = SpiderUtils()

    def parse(self, response: scrapy.http.Response, categories: List[str] = []):
        """
        Parse the response and extract subcategories and artwork URLs.

        :param response: The response object.
        :param categories: List of categories.
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

    def parse_art_urls(self, response: scrapy.http.Response, categories: List[str]):
        """
        Parse the response and extract artwork URLs.

        :param response: The response object.
        :param categories: List of categories.
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
        Parse the response and extract artwork information.

        :param response: The response object.
        :param categories: List of categories.
        """

        item = ArtItem()
        artists = self.spider_utils.extract_with_css(response, "h2::text")
        if artists:
            artists = [artist.strip() for artist in artists.split(";")]
            item["artist"] = [
                re.search(r":\s*(.*)", artist).group(1)
                for artist in artists
                if re.search(r":\s*(.*)", artist)
            ]

        title = self.spider_utils.extract_title(
            self.spider_utils.extract_with_css(response, "h1::text")
        )
        if title:
            item["title"] = title

        description = self.spider_utils.extract_with_css(response, "p::text")
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
        dimensions_dict = self.spider_utils.extract_dimensions(dimensions)
        if dimensions_dict:
            item["height"] = dimensions_dict["height"]
            item["width"] = dimensions_dict["width"]

        item["categories"] = categories
        yield item
