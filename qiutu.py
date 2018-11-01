import urllib.request
import re
import time
import os

def handle_request(url,page):
	url_page = url.format(page)
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
	}
	#构建请求对象
	request = urllib.request.Request(url=url_page,headers=headers)
	return request

def parse_content(content):
	pattern = re.compile(r'<div class="thumb">.*?<img src="(.*?)" alt="(.*?)" />.*?</div>',re.S)
	ret = pattern.findall(content)
	dirname = 'qiutu'
	for info in ret:
		#图片地址
		img_src = 'http:' + info[0]
		#图片名称
		img_name = info[1] + '.' + img_src.split('.')[-1]
		print('正在下载--%s--' % img_name)
		filepath = os.path.join(dirname,img_name)
		try:
			urllib.request.urlretrieve(img_src,filepath)
		except:
			print('二货，没有这个图片')
		
		print('结束下载--%s--' % img_name)
		time.sleep(2)


def main():
	start_page = int(input('请输入起始页码：'))
	end_page = int(input('请输入结束页码：'))
	url = 'https://www.qiushibaike.com/pic/page/{}/'

	for page in range(start_page,end_page+1):
		print('正在下载--第%s页--......' % page)
		request = handle_request(url,page)
		#发送请求，得到响应
		response = urllib.request.urlopen(request)
		#获取响应内容字符串格式
		content = response.read().decode('utf8')
		parse_content(content)
		print('结束下载--第%s页--......' % page)


if __name__ == '__main__':
	main()






