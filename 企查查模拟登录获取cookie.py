"""
Created on Thu Jul 30 11:04:15 2020
启用开发者模式和JS代码注入改变navigator.webdriver的属性值为false后,登录可以成功防止webdriver检测(存在不确定行)

测试加开发者模式和JS代码注入的情况下，暂时测试100%成功,成功获取到cookie，代码的稳定性还有待检验
@author: 强延飞
"""
from selenium import webdriver
import time
import random
import requests

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

def main():
	url = 'https://www.qcc.com/user_login'
	# url = 'https://login.taobao.com/member/login.jhtml'
	options = webdriver.ChromeOptions()
	options.add_experimental_option("excludeSwitches",["enable-automation"])
	driver = webdriver.Chrome(options=options)
	#driver = webdriver.Chrome()
	driver.get(url)
	script = 'Object.defineProperty(navigator,"webdriver",{get:() => false,});'
	driver.execute_script(script)

	time.sleep(1.232)
	driver.find_element_by_xpath('//*[@id="normalLogin"]').click()
	time.sleep(1.0232)
	driver.find_element_by_xpath('//*[@id="nameNormal"]').send_keys('1158654898765')
	time.sleep(1.8315)
	driver.find_element_by_xpath('//*[@id="pwdNormal"]').send_keys('987654654')

	# 滑动验证码  存在问题：滑动滑动距离distance需要确定
	square_button = driver.find_element_by_xpath('//*[@id="nc_1_n1z"]')
	distance = 370
	track_list = get_track(distance)
	action = webdriver.ActionChains(driver)
	action.click_and_hold(square_button).perform()
	for track in track_list:
		action.move_by_offset(track,0)
	action.release(square_button).perform()

	time.sleep(5)#点击登录按钮
	driver.find_element_by_xpath('//*[@id="user_login_normal"]/button').click()
	time.sleep(5)
	#获取cookie
	cookie_items = driver.get_cookies()
	cookie_str = ''
	for item_cookie in cookie_items:
		item_str = item_cookie["name"] + "=" + item_cookie["value"] + "; "
		cookie_str += item_str
		print(item_cookie)
	# 打印出来看一下
	print('cookie_str:', cookie_str)
	driver.close()

def verify_cookie(cookie_str):
	url = 'https://www.qcc.com/company_getinfos?unique=d38fd1da97458b037750ff31ebd38d59&companyname=%E5%8D%97%E4%BA%AC%E4%B8%AD%E6%96%B0%E8%B5%9B%E5%85%8B%E7%A7%91%E6%8A%80%E6%9C%89%E9%99%90%E8%B4%A3%E4%BB%BB%E5%85%AC%E5%8F%B8&p=2&tab=assets&box=zhuanli&zlpublicationyear=&zlipclist=&zlkindcode=&zllegalstatus='
	headers = {
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
			'cookie':cookie_str,
			}
	r = requests.get(url,headers=headers)
	print(r.status_code)
	html = r.text
	print(html)

if __name__ == '__main__':
	main()
