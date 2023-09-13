import re
from typing import Dict, Union
import scrapy
from ..items import ArtItem
from ..enum.options import Options


class TrialSpider(scrapy.Spider):
    """oi"""
    name = 'trial'
    start_urls = ['http://pstrial-2019-12-16.toscrape.com/browse/']
    categories = []

    @staticmethod
    def _verify_category(categories, subcat_text):
        if subcat_text in Options.categories:
            return True
        if categories:
            return True

    def parse(self, response, categories):
        """oi"""
        subcat = response.xpath('//*[(@id = "subcats")]/div')
        if subcat:
            anchors = subcat.xpath('.//a[h3]')
            for anchor in anchors:
                subcat_text = anchor.css('::text').get()
                if self._verify_category(categories, subcat_text):
                    temp_list = categories.copy()
                    temp_list.append(subcat_text)
                    yield response.follow(url=anchor, callback=self.parse, cb_kwargs={'categories': temp_list})

        yield from self.parse_art_urls(response, categories)

    def parse_art_urls(self, response, categories):
        """oi"""
        art_urls = response.xpath('//*[@id="body"]/div[2]/a[contains(@href,"/item")]').css('a')
        if art_urls.get():
            yield from response.follow_all(urls=art_urls, callback=self.parse_art, cb_kwargs={'categories': categories})

            next_page = response.css("[class='nav next'] [name='page']")[0].attrib['value']
            if response.url[-1:].isnumeric():
                split_url = response.url.split('page=')
                next_url = split_url[0] + 'page=' + next_page
                yield response.follow(next_url, callback=self.parse_art_urls, cb_kwargs={'categories': categories})
            else:
                yield response.follow(response.url + '?page=1', callback=self.parse_art_urls,
                                      cb_kwargs={'categories': categories})

    @staticmethod
    def parse_art(response, categories):
        """oi"""
        def extract_with_css(query: str) -> str:
            return response.css(query).get(default="").strip()

        def extract_dimensions(input_string: str) -> Union[None, Dict[str, float]]:
            if not input_string:
                return None
            match = re.search(r'\((\d[^)]+)\)', input_string)

            if match:
                values = match.group(0).replace('(', '').replace(')', '').replace('cm', '').split()

                if len(values) > 1:
                    return {'height': float(values[0]), 'width': float(values[2])}
            else:
                return None

        def parse_title(art_title: str) -> Union[str, None]:
            result = re.sub(r'^untitled\s*,*', '', art_title, flags=re.IGNORECASE)
            result = re.sub(r'^([\[(])(.+?)([])])$', r'\2', result)

            return result.strip() if result else None

        item = ArtItem()
        artists = extract_with_css('h2::text')
        if artists:
            artists = [artist.strip() for artist in artists.split(';')]
            item['artist'] = [re.search(r':\s*(.*)', artist).group(1) for artist in artists if
                              re.search(r':\s*(.*)', artist)]

        title = parse_title(extract_with_css('h1::text'))
        if title:
            item['title'] = title

        description = extract_with_css('p::text')
        if description:
            item['description'] = description

        item['image'] = 'http://pstrial-2019-12-16.toscrape.com' + response.css('img').attrib['src']
        item['url'] = response.url
        dimensions = response.xpath('//td[@class="key" and text()="Dimensions"]/following-sibling::td['
                                    '@class="value"]/text()').get()
        dimensions_dict = extract_dimensions(dimensions)
        if dimensions_dict:
            item['height'] = dimensions_dict['height']
            item['width'] = dimensions_dict['width']

        item['categories'] = categories
        yield item
