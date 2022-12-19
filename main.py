import aiohttp
import asyncio
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import img2pdf
import glob
import os

from image_util import ImageSaver
from PIL import Image
from io import BytesIO

SCROLL_PAUSE_TIME = 0.5
PRODUCTS_PER_PAGE=36
HEIGHT=1920
WIDTH=1080
BASE_URL='https://www.spar.hu/onlineshop/search/'
INDEX_URL=f"{BASE_URL}?query=*&q=*&hitsPerPage={PRODUCTS_PER_PAGE}&filter=is-on-promotion:Minden%20aj%C3%A1nlat&page=1"

SAVE_LOCATION='tmp'

BODY = None
PAGE_URL=None

imageSaver = ImageSaver(saveLocation=SAVE_LOCATION)

async def get_html(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()
            print(resp.status)
            html = await resp.text()
            print(html)
            return html

def hide_footer():
    driver.execute_script('document.getElementsByTagName("footer")[0].style.display="none";')

def hanlde_first_page():

    try:
    
        print('Search cookie modal close btn')
        shadow_host = driver.find_element(by=By.ID,value='cmpwrapper')
        script = 'return arguments[0].shadowRoot'
        shadow_root = driver.execute_script(script, shadow_host)

        closeBtn = shadow_root.find_element(by=By.CLASS_NAME,value='cmpclose')
        
        closeBtn.find_element(by=By.TAG_NAME,value='a').click()
        driver.refresh()


    except Exception as e:
        print("There isn't cookie modal close button"+str(e))

    try:
        
        print('Search cookie btn')
        cookieBtn = driver.find_element(by=By.XPATH, value='//*[@id="cmpwelcomebtnyes"]/a')
        cookieBtn.click()
    except Exception as e:
        print("There isn't cookie button")

    try:
        print('Search close btn')
        closeBtn = driver.find_element(by=By.XPATH, value= '//div[@id="header"]//button[@aria-label="Bezárás"]')

        closeBtn.click()
    except Exception as e:
        print("There isn't close button"+str(e))


def savePage(page):
    print(f'Get page#{page}...', flush=True)

    global BODY
    global PAGE_URL
    if PAGE_URL is None:
        PAGE_URL = INDEX_URL
    
    driver.get(PAGE_URL);
    BODY = driver.find_element(by=By.TAG_NAME, value="body")
    
    WebDriverWait(driver= driver,timeout=30,poll_frequency=5).until(EC.presence_of_all_elements_located((By.CLASS_NAME,'productBoxImage')))

    if page == 1:
        hanlde_first_page()

    try:
        nextBtn = driver.find_element(by=By.CLASS_NAME,value='next')
        nextLink = nextBtn.find_element(by=By.TAG_NAME,value='a')
        nextPageURL = nextLink.get_attribute('href')
        PAGE_URL = nextPageURL
        print("Go to next page")
        return True
    except Exception as e:
        take_screenshots_of_items(page)
        print("Finished")
        return False

def take_screenshots_of_items(page):

    for item in driver.find_elements(by=By.CLASS_NAME,value='productGridSingleElement'):

        raw = Image.open(BytesIO(item.screenshot_as_png))
        imageSaver.addImage(raw)

def creaet_i2pdf():
    with open("out/spar_all_actions.pdf", "wb") as pdf:
        files = glob.glob(SAVE_LOCATION+"/*.png")
        files = sorted(files, key=lambda t: os.stat(t).st_mtime)
        pdf.write(img2pdf.convert(files,viewer_fit_window=True))


async def run():
    print('Start...')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless=True
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--verbose')
    chrome_options.add_argument('--log-path=/tmp/ChromeDriver.log')
    chrome_options.add_argument('--disable-site-isolation-trials')
    chrome_options.add_experimental_option("prefs", {"profile.default_content_setting_values.cookies": '2'})
    chrome_options.add_experimental_option("prefs", {"profile.block_third_party_cookies":"false"})
    

    global driver
    
    driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'),options=chrome_options)
    driver.set_window_size(WIDTH, HEIGHT)
    
    page = 1
    while savePage(page):
        hide_footer()
        take_screenshots_of_items(page)
        page = page + 1

    imageSaver.save()
    creaet_i2pdf()
    print('Close...')
    driver.close()
    driver.quit()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    asyncio.run(run())
