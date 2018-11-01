# -*- coding: utf-8 -*-
import scrapy
import os

from imagepro.items import ImageproItem 


class ImageSpider(scrapy.Spider):
    name = 'image'
    allowed_domains = ['699pic.com']
    start_urls = ['http://699pic.com/people.html']

    # 400页的图片全都要，图片的信息保存到文件中

    def parse(self, response):
        # 解析什么呢？获取所有图片的详情页链接
        href_list = response.xpath('//div[@class="list"]/a/@href').extract()
        # 遍历，依次向详情页发送请求
        for href in href_list:
            yield scrapy.Request(url=href, callback=self.parse_detail)

    def parse_detail(self, response):
        # 创建一个对象
        item = ImageproItem()
        # 获取名字
        item['name'] = response.xpath('//div[@class="photo-view"]/h1/text()').extract()[0].replace(' ', '')
        # 发布时间
        item['publish_time'] = response.css('.publicityt::text').extract()[0].strip(' 发布')
        #获取浏览量
        item['look'] = response.xpath('//span[@class="look"]/read/text()').extract()[0]
        #获取收藏数量
        item['collect'] = response.xpath('//span[@class="collect"]/text()').extract()[0]
        #获取下载数量
        item['download'] = response.xpath('//span[@class="download"]/text()').extract()[1].replace(' ','').strip()
        # 获取图片地址
        item['image_src'] = response.xpath('//img[@id="photo"]/@src').extract()[0]

        # fields = ['name','publish_time','look','collect','download','image_src']
       
        image_src =  item['image_src']
        name = item['name']
        yield scrapy.Request(url=item['image_src'],callback=self.download,meta={'image_src':image_src,'name':name})
        # 将item扔给引擎
        yield item


    def download(self,response):
        dirname = 'picture'
        name = response.meta['name']
        image_src = response.meta['image_src']
        filename = name + '.' + image_src.split('.')[-1]
        filepath = os.path.join(dirname,filename)
        with open(filepath,'wb') as fp:
            fp.write(response.body)

