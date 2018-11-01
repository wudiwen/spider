import urllib.request
from lxml import etree
import time
import os

def handle_request(url,page):
	url_page = url.format(page)
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
		'Connection': 'keep-alive',
		'Referer': 'http://www.mzitu.com/',
	}
	#构建请求对象
	request = urllib.request.Request(url=url_page,headers=headers)
	return request

def parse_content(content):
	# 获取tree对象
	tree = etree.HTML(content)
	#获取图片地址
	hrefs = tree.xpath('//div[@class="postlist"]/ul/li/a/img/@data-original')
	# print(hrefs)
	title = tree.xpath('//div[@class="postlist"]/ul/li/a/img/@alt')
	dirname = 'meizi'
	for href in hrefs:
		headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
		'Connection': 'keep-alive',
		'Referer': 'http://www.mzitu.com/',
	}
		request1 = urllib.request.Request(url=href,headers=headers)
		response1 = urllib.request.urlopen(request1)
		#图片名称
		img_name = title[hrefs.index(href)] + '.' + href.split('.')[-1]
		print('正在下载--%s--' % img_name)
		filepath = os.path.join(dirname,img_name)
		with open(filepath,'wb') as fp:
			fp.write(response1.read())
		print('结束下载--%s--' % img_name)
		time.sleep(2)


def main():
	start_page = int(input('请输入起始页码：'))
	end_page = int(input('请输入结束页码：'))
	url = 'http://www.mzitu.com/page/{}/'

	for page in range(start_page,end_page+1):
		print('正在下载--第%s页--......' % page)
		request = handle_request(url,page)
		#发送请求，得到响应
		response = urllib.request.urlopen(request)
		#获取响应内容字符串格式
		content = response.read().decode('utf8')
		# print(content)
		parse_content(content)
		print('结束下载--第%s页--......' % page)


if __name__ == '__main__':
	main()






