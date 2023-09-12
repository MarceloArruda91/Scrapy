# -*- coding: utf-8 -*-
import scrapy


# Any additional imports (items, libraries,..)


class TrialSpider(scrapy.Spider):
    name = 'trial'
    start_urls = ['http://pstrial-2019-12-16.toscrape.com/browse/']  # put your start urls here

    @staticmethod
    def parse_art(response):
        def extract_with_css(query):
            return response.css(query).get(default="").strip()

        data = {
            "tittle": extract_with_css('h1::text'),
            "description": extract_with_css('p::text'),
            "artist": extract_with_css('h2::text').split(';'),
            "url": response.url,
            "image": response.css('img').attrib['src'],
            "height": '',
            "width": '',
            "categories": '',

        }
        yield data

    def parse(self, response):
        if response.url == 'http://pstrial-2019-12-16.toscrape.com/browse/':
            for subcat in response.xpath('//*[(@id = "subcats")]/div'):
                if subcat.css('h3::text').get() == "In Sunsh" or subcat.css('h3::text').get() == "Summertime":
                    yield response.follow(subcat.css('a')[0], self.parse)

        else:
            subcat = response.xpath('//*[(@id = "subcats")]/div')
            if subcat:
                anchors = subcat.css('a')
                #nao ta pegando caso n exista subcategoria na classe
                yield from response.follow_all(anchors, callback=self.parse)
            else:
                anchors = response.xpath('//*[@id="body"]/div[2]/a[contains(@href,"/item")]').css('a')
                if anchors:
                    yield from response.follow_all(anchors, callback=self.parse_art)

                    next_page = response.css("[class='nav next']").css("[name='page']")[0].attrib['value']
                    if response.url[-1:].isnumeric():
                        split_url = response.url.split('page=')
                        next_url = split_url[0] + 'page=' + next_page
                        yield response.follow(next_url, callback=self.parse)
                    else:
                        yield response.follow(response.url + '?page=1', callback=self.parse)
