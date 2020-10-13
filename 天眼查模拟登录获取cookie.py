# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:21:21 2020
selenium模拟登录天眼查
难点1：获取验证前后两张图片后，获取滑块拼图的位置
    方法1：通过PIL库，对比验证码前后两张图的像素大小，给与一定的差异取值范围，超过的差异值的区域返回出来；（本实例选择方法一，相对简单）
    方法2：通过PIL.difference的方法，对比两张图，范围不同的区域，和方法一大同小异，但是对于有干扰项的滑块验证码图片识别效率不高，需要对PIL.difference的方法的源码进行修改
难点2：获取滑块滑动距离后，模拟人类操作滑动滑块
    步骤一：制作一个规矩函数，加入加速度和减速带，获取规矩列表
    步骤二：修改selenium源码中的webdriver.ActionChains方法，将滑动间隔时间修改到10ms左右，修改完成后，需要重启Spyder，重新运行
存在问题：
    滑动距离和时间滑块距离有一定的误差，但是在可接受的距离之内，可能的原因：
    1  滑块规矩列表函数get_track()可能存在问题
    2  图片对比函数get_gap()输出的距离可能有问题
    具体原因有待深究
@author: 强延飞
"""

from selenium import webdriver
import time
from PIL import Image
import random

def get_gap(image1, image2):
	"""
	获取缺口偏移量
	:param image1: 不带缺口图片
	:param image2: 带缺口图片
	:return:
	"""
	left = 60
	for i in range(left, image1.size[0]):
		for j in range(image1.size[1]):
			if not is_pixel_equal(image1, image2, i, j):
				left = i
				return left
	return left

def is_pixel_equal(image1, image2, x, y):
	"""
	判断两个像素是否相同
	:param image1: 图片1
	:param image2: 图片2
	:param x: 位置x
	:param y: 位置y
	:return: 像素是否相同
	"""
	# 取两个图片的像素点
	pixel1 = image1.load()[x, y]
	pixel2 = image2.load()[x, y]
	threshold = 60
	if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
			pixel1[2] - pixel2[2]) < threshold:
		return True
	else:
		return False


def get_track(distance):
	'''
	模拟人类操作制作滑块滑动轨迹列表
	'''
	track = []
	current = 0
	mid = distance * 3 / 5
	t = random.randint(2, 3) / 10
	v = 0
	while current < distance:
		if current < mid:
			a = 2
		else:
			a = -3
		v0 = v
		v = v0 + a * t
		move = v0 * t + 1 / 2 * a * t * t
		current += move
		track.append(move)
	return track


def slide_block(image1, image2, circle_button, driver, length):
	'''
	模拟操作滑块进行滑动，成功率不高，所以加上了函数后，进行循环操作
	'''
	distance = int(get_gap(image1, image2)) + length
	#    print('distance:',distance)

	#
	a = random.uniform(-0.8, -0.6)
	track_list = get_track(distance) + [a, a, a, a, a, a, a, a, a, a, a, a]
	track_list_sum = sum(track_list)

	gap_d = distance - track_list_sum
	#    print('gap_d:',gap_d)
	g = gap_d / 20
	l_g = [g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g,
		   g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g, g,
		   g, g, g, g, g]

	track_list = track_list + l_g
	#    print('track_list:',track_list)
	time.sleep(1)

	action = webdriver.ActionChains(driver)

	action.click_and_hold(circle_button).perform()
	time.sleep(0.1)

	for track in track_list:
		y = random.uniform(-1, 1)
		action.move_by_offset(track, y)

	time.sleep(0.1)
	action.release(circle_button).perform()

	time.sleep(3)
	html = driver.page_source
	#    print(len(html))
	return len(html)


def main():
	url = 'https://www.tianyancha.com/login'
	driver = webdriver.Chrome(r'D:\chromedriver')
	driver.get(url)
	time.sleep(3)
	driver.find_element_by_xpath('//*[@id="web-content"]/div/div[2]/div/div/div[3]/div[3]/div[1]/div[2]').click()
	time.sleep(0.2)
	driver.find_element_by_xpath('//*[@id="mobile"]').send_keys('15251711240')
	time.sleep(0.3)
	driver.find_element_by_xpath('//*[@id="password"]').send_keys('pq8330866')
	time.sleep(3)

	# 点击登录按钮
	driver.find_element_by_xpath('//*[@id="web-content"]/div/div[2]/div/div/div[3]/div[3]/div[2]/div[4]').click()
	time.sleep(5)

	# 上一步点击按钮有概率会点击无效，需要加上试错操作，如果点击失败后，重新点击获取截图
	try:
		# 验证码初始图片截图
		verification_code = driver.find_element_by_xpath(
			'/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]/a[1]/div[1]')
		verification_code.screenshot(r'D:\r.png')
		time.sleep(3)
	except:
		driver.find_element_by_xpath('//*[@id="web-content"]/div/div[2]/div/div/div[3]/div[3]/div[2]/div[4]').click()
		time.sleep(5)

		# 验证码初始图片截图
		verification_code = driver.find_element_by_xpath(
			'/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]/a[1]/div[1]')
		verification_code.screenshot(r'D:\r.png')
		time.sleep(3)

	# 定位拖动滑动的圆圈位置
	circle_button = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]')
	circle_button.click()
	time.sleep(3)

	# 验证码拼图图片再次截图
	verification_code1 = driver.find_element_by_xpath(
		'/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]/a[2]/div[1]')
	verification_code1.screenshot(r'D:\r1.png')

	image1 = Image.open(r'D:\r.png')
	image2 = Image.open(r'D:\r1.png')

	# 循环五次模拟操作滑动滑块，给与一定的差异值
	for i in [20, 30, 10, 35, 15, 25]:
		html_len = slide_block(image1, image2, circle_button, driver, i)

		if html_len > 200000:
			break
	print(html_len)
	if html_len > 200000:
		cookie_items = driver.get_cookies()
		cookie_str = ''
		# 组装cookie字符串
		for item_cookie in cookie_items:
			item_str = item_cookie["name"] + "=" + item_cookie["value"] + "; "
			cookie_str += item_str
			print(item_cookie)
		# 打印出来看一下
		print('cookie_str:',cookie_str)
	else:
		cookie_str = ''
	driver.close()
	return cookie_str

if __name__ == '__main__':
	for i in range(100):
		cookie_str = main()
		if len(cookie_str)>0:
			break



