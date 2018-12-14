# coding:utf-8

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from PIL import Image
import time

"""
1.输入用户名、密码，点击登录按钮
2.弹出验证按钮，获取验证按钮并点击
3.出现滑块验证码，获取网页截图1
4.点击滑块按钮，出现缺口，获取网页截图2
5.比较截图1中和截图2中像素点，获取移动距离
6.模拟人的行为习惯，根据总位移得到行为轨迹
7.根据行为轨迹进行滑动
"""

def get_screenshot(browser):
    """
    获取网页截图
    :return:
    """
    browser.save_screenshot('page.png')
    screenshot_obj = Image.open('page.png')

    return screenshot_obj

def get_image(browser):
    """
    获取滑动验证码的图片
    :param browser:
    :return: 验证码图片
    """
    wait = WebDriverWait(browser, 10)
    img = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_canvas_bg')))
    location = img.location
    size = img.size

    top = location['y']
    bottom = location['y'] + size['height']
    left = location['x']
    right = location['x'] + size['width']

    screenshot_obj = get_screenshot(browser)
    crop_image_obj = screenshot_obj.crop((left,top,right,bottom))

    return crop_image_obj

def get_distance(image1,image2):
    """
    对比获得的两张图片，从而确定滑动距离
    :param image1: 无缺口图片
    :param image2: 有缺口图片
    :return: 滑动距离
    """
    threshold = 60
    left = 60
    for i in range(left,image1.size[0]):
        for j in range(image1.size[1]):
            rgb1 = image1.load()[i,j]
            rgb2 = image2.load()[i,j]
            res1 = abs(rgb1[0]-rgb2[0])
            res2 = abs(rgb1[1]-rgb2[1])
            res3 = abs(rgb1[2]-rgb2[2])

            if not (res1 < threshold and res2 < threshold and res3 < threshold):
                return i
    return i

def get_tracks(distance):
    """
    获取移动轨迹，移动轨迹用位移列表表示
    :param distance:
    :return: 移动轨迹
    """
    v = 0 # 初始速度为0
    t = 0.2 # 间隔时间设置为0.2s
    tracks = [] # 保存移动轨迹的列表
    current = 0 # 当前的位移
    mid = distance * 4 / 5 # 设置的分隔点，在该点前加速运动，在该点后减速运动

    while current < distance:
        if current < mid:
            a = 2 # 在前半段，加速度的值
        else:
            a = -3 # 在后半段，加速度的值
        v0 = v
        s = v0 * t + 1 / 2 * a * t * t # 0.2s内的位移
        current += s #
        tracks.append(current)
        v = v0 + a * t # 作为下一个小段的初始速度

    return tracks

def crack(browser):
    """
    破解滑动验证
    :param browser:
    :return:
    """
    # 1.点击按钮，获取没有缺口的图片
    wait = WebDriverWait(browser,10)
    first_button = wait.until(EC.presence_of_element_located(
        (By.CLASS_NAME, 'geetest_radar_tip')))  # browser.find_element_by_class_name('geetest_radar_tip')
    first_button.click()

    # 2.获取没有缺口的图片
    image1 = get_image(browser)

    # 3.点击滑动按钮，获得有缺口的图片
    second_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'geetest_slider_button')))
    second_button.click()

    # 4.获得有缺口的图片
    image2 = get_image(browser)

    # 5.对比两张图片，找出移动距离
    distance = get_distance(image1,image2)

    # 6.获取行为轨迹
    tracks = get_tracks(distance)
    # print(tracks)

    # 7.按照行动轨迹，先正向滑动，后反向滑动
    button = browser.find_element_by_class_name('geetest_slider_button')
    ActionChains(browser).click_and_hold(button).perform()
    for track in tracks:
        ActionChains(browser).move_by_offset(xoffset=track,yoffset=0).perform()

    time.sleep(0.5)
    ActionChains(browser).release().perform()

def login(username,password):
    """
    登录博客园后台网站
    :return:
    """
    # 1.登录
    browser = webdriver.Chrome()
    # wait = WebDriverWait(browser,10)
    browser.get('https://passport.cnblogs.com/user/signin')
    input_username = browser.find_element_by_id('input1')
    input_pwd = browser.find_element_by_id('input2')
    signin = browser.find_element_by_id('signin')

    input_username.send_keys(username)
    input_pwd.send_keys(password)
    signin.click()

    # 2.破解滑动验证码
    crack(browser)


if __name__ == '__main__':
    login(username='lzl5893719',password='')




