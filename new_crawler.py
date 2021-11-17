from typing import Counter
from playwright.sync_api import sync_playwright
import hashlib
from bs4 import BeautifulSoup
import sys
import time
import datetime
import requests
import re
import math
import os
import datetime
import json
import pickle




# selectorleri çağırdığımız yer
def get_selectors(domain_subscription_id):
    with open("./category_selectors.json","r") as f:
        domain_selectors = json.loads(f.read()) 
    return domain_selectors.get(str(domain_subscription_id))

    
def get_results(domain_subscription_id):

    subscription_selectors = get_selectors(domain_subscription_id)
    name = subscription_selectors.get("name")
    base_url = subscription_selectors.get("base_url")
    domains_subscription_id1 = subscription_selectors.get("domains_subscription_id")
    render = subscription_selectors.get("render")
    urls = subscription_selectors.get("urls")
    scroll = subscription_selectors.get("scroll")
    contains = subscription_selectors.get("contains")
    product_href_selector = subscription_selectors.get("product_href_selector")
    next_page = subscription_selectors.get("next_page")
    next = subscription_selectors.get("next")
    is_active = subscription_selectors.get("is_active")
    time = subscription_selectors.get("time")
    popup_close = subscription_selectors.get("popup_close")
    country_select = subscription_selectors.get("country_select")
    is_category = subscription_selectors.get("is_category")
    total_product_count = subscription_selectors.get("total_product_count")
    one_page_count = subscription_selectors.get("one_page_count")
    next_page_path = subscription_selectors.get("next_page_path")
    select_attribute = subscription_selectors.get("select_attribute")
    split_after_count_text = subscription_selectors.get("split_after_count_text")
    split_before_count_text = subscription_selectors.get("split_before_count_text")
    wait_before_load = subscription_selectors.get("wait_before_load")
    # is active true olarak başlanan yer
    if is_active:
        createFolder('./{0}/'.format(name)) 
        path1 = './{0}/{1}.txt'.format(name,domains_subscription_id1) 
        file_category = open(path1,"a")
        for key, value in urls.items():
            link = value
            # Browser açılan yer 
            if render:
                for category_link in link:
                    print("Go To link:", category_link)
                    with sync_playwright() as playwright:
                        chromium = playwright.firefox  # or "firefox" or "webkit".
                        browser = chromium.launch(headless=False)
                        context = browser.new_context(ignore_https_errors=True, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
                        page = context.new_page()
                        page.set_default_navigation_timeout(1000000000)
                        page.goto(category_link)
                        page.wait_for_load_state()
                        # bekletme koymak için
                        if wait_before_load:
                            page.wait_for_timeout(wait_before_load)
                        page_content = page.content()
                        soup = BeautifulSoup(page_content, 'html.parser')
                        #page.wait_for_timeout(30000000)
                        if country_select:
                            page.evaluate(country_select)
                            page.wait_for_timeout(3000)
                        if scroll:
                            while True: 
                                scroll_page(page,time)
                                if next:
                                    try:
                                        page.click(next_page)
                                        page.wait_for_timeout(6000)
                                    except:
                                        print("not click")
                                        break
                                else:
                                    break  
                            links = page.query_selector_all(product_href_selector)
                            for a in links:
                                product_href=a.get_attribute("href")
                                category_select = []
                                # çoklu ulr lerde category alanını seçmek için
                                if is_category:
                                    category_is_select = soup.select(is_category)
                                    for r in category_is_select:
                                        text = r.text.replace(">","")
                                        text =text.strip()
                                        category_select.append(text)
                                    category = ' / '.join([str(x) for x in category_select])
                                else:
                                    category = key    
                                write_file(path1,product_href,base_url,domains_subscription_id1,category)
                            page.wait_for_timeout(3000)
                            if popup_close:
                                while True:
                                    try: 
                                        page.evaluate(popup_close)
                                        page.wait_for_timeout(1000)
                                        break
                                    except:
                                        print("not Popup")
                                        break
                            page.keyboard.press("Escape")   
                        else:
                            while True: 
                                scroll_page(page,time)
                                links = page.query_selector_all(product_href_selector)
                                for a in links:
                                    product_href=a.get_attribute("href")
                                    category_select = []
                                    if is_category:
                                        category_is_select = soup.select(is_category)
                                        for r in category_is_select:
                                            text = r.text.replace(">","")
                                            text =text.strip()
                                            category_select.append(text)

                                        category = ' / '.join([str(x) for x in category_select])
                                    else:
                                        category = key    
                                    
                                    write_file(path1,product_href,base_url,domains_subscription_id1,category)
                                page.wait_for_timeout(3000)
                                if popup_close:
                                    while True:
                                        try: 
                                            page.evaluate(popup_close)
                                            page.wait_for_timeout(1000)
                                            break
                                        except:
                                            print("not Popup")
                                            break
                                page.keyboard.press("Escape")
                                
                                if next:
                                    try:
                                        page.click(next_page)
                                        page.wait_for_timeout(6000)
                                    except:
                                        print("not click")
                                        break
                                else:
                                    break

                        browser.close()
            # render false
            else:
                # Browser açılmayan yer  
                for category_link in link:
                    print("go to category link",category_link)
                    response = requests.get(category_link) 
                    page_content = response.content
                    soup = BeautifulSoup(page_content, 'html.parser')
                    count = soup.select(total_product_count)
                    if count:
                        total_text = count[0].text
                        if split_after_count_text:
                            total_text_split_after = total_text.split(split_after_count_text)[1]
                        if split_before_count_text:
                            total_text_split_after = total_text_split_after.split(split_before_count_text)[0]
                            total_text = total_text_split_after
                    else:
                        total_text = "1"
                    
                    page_count_text = total_text.replace(",","").replace(".","")
                    page_count_one = page_count(page_count_text,one_page_count)
                    print("page_count_one-------------",page_count_one)
                    url_next_path =  next_page_path_control(next_page_path,category_link, product_href_selector)
                    for page in range(1,page_count_one+1):
                        url = category_link + url_next_path+"{0}".format(page)
                        response = requests.get(url)
                        print("Go to url ------",url)
                        soup = BeautifulSoup(response.content,"lxml")
                        result = soup.select(product_href_selector)
                        if result:
                            if len(result) > 1:
                                if select_attribute:
                                    for r in result:
                                        product_href = r[select_attribute] 
                                        print(product_href)
                                        category_select = []
                                        # çoklu ulr lerde category alanını seçmek için
                                        if is_category:
                                            category_is_select = soup.select(is_category)
                                            for r in category_is_select:
                                                text = r.text.replace(">","")
                                                text =text.strip()
                                                category_select.append(text)
                                            category = ' / '.join([str(x) for x in category_select])
                                        else:
                                            category = key    
                                        write_file(path1,product_href,base_url,domains_subscription_id1,category)
                            
                            
def next_page_path_control(next_page_path, category_link,product_href_selector):
    for key, value in next_page_path.items():
        if key == "path_1":
            key_path = value
            url = category_link + key_path+"{0}".format(1)
            response = requests.get(url)
            print("Go to url ------",url)
            soup = BeautifulSoup(response.content,"lxml")
            result = soup.select(product_href_selector)
            if result:
                if len(result) > 1:
                    return key_path
                    
        elif key == "path_2":
            key_path = value
            url = category_link + key_path+"{0}".format(1)
            response = requests.get(url)
            print("Go to url ------",url)
            soup = BeautifulSoup(response.content,"lxml")
            result = soup.select(product_href_selector)
            if result:
                if len(result) > 1:
                    return key_path
                                              
# page count hesaplanan yer
def page_count(page_count_text,one_page_count):
    p = '[\d]+[.,\d]+|[\d]*[.][\d]+|[\d]+'
    if re.search(p, page_count_text) is not None:
        for catch in re.finditer(p, page_count_text):
            count = catch[0]

    page_count = math.ceil(int(count) / int(one_page_count))
    return page_count

# dosyaya yazma işlemleri
def write_file(path1,product_href,base_url,domains_subscription_id1,category):    
    file_category = open(path1,"r")
    if base_url in product_href:
        productlink = product_href
        if "aliexpress.com" in productlink:
            productlink = productlink.split("?")[0]
            has = hashlib.md5(productlink.encode("utf-8")).hexdigest()
            product_link1 = ("{0};#;{1};#;{2};#;{3}".format(domains_subscription_id1,productlink,has,category))
            campaingisnot = file_category.read().find(product_link1)
            if campaingisnot !=-1:
                print("*******************there is******************")
            else:    
                link_write = open(path1,"a")
                link_write.write("{0};#;{1};#;{2};#;{3}\n".format(domains_subscription_id1,productlink,has,category))
                print(productlink)

        else:
            has = hashlib.md5(productlink.encode("utf-8")).hexdigest()
            product_link1 = ("{0};#;{1};#;{2};#;{3}".format(domains_subscription_id1,productlink,has,category))
            campaingisnot = file_category.read().find(product_link1)
            if campaingisnot !=-1:
                print("*******************there is******************")
            else:    
                link_write = open(path1,"a")
                link_write.write("{0};#;{1};#;{2};#;{3}\n".format(domains_subscription_id1,productlink,has,category))
                print(productlink)
    else:
        productlink = base_url + product_href
        if "aliexpress.com" in productlink:
            productlink = productlink.split("?")[0]
            has = hashlib.md5(productlink.encode("utf-8")).hexdigest()
            product_link1 = ("{0};#;{1};#;{2};#;{3}".format(domains_subscription_id1,productlink,has,category))
            campaingisnot = file_category.read().find(product_link1)
            if campaingisnot !=-1:
                print("*******************there is******************")
            else:    
                link_write = open(path1,"a")
                link_write.write("{0};#;{1};#;{2};#;{3}\n".format(domains_subscription_id1,productlink,has,category))
                print(productlink)
        else:
            has = hashlib.md5(productlink.encode("utf-8")).hexdigest()
            product_link1 = ("{0};#;{1};#;{2};#;{3}".format(domains_subscription_id1,productlink,has,category))
            campaingisnot = file_category.read().find(product_link1)
            if campaingisnot !=-1:
                print("*******************there is******************")
            else:    
                link_write = open(path1,"a")
                link_write.write("{0};#;{1};#;{2};#;{3}\n".format(domains_subscription_id1,productlink,has,category))
                print(productlink)

# ne klasör açılan yer
def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

# scroll yapılan yer
def scroll_page(page,time):
    while page.evaluate("document.body.scrollHeight") - page.evaluate("window.scrollY") > 720 :
        print(page.evaluate("window.scrollY") ,page.evaluate("document.body.scrollHeight"))
        next = page.evaluate("window.innerHeight")
        next = next -300
        print(next)
        page.evaluate(f"window.scrollBy(0,{next});")
        page.wait_for_timeout(time)
    return

        
if __name__ == "__main__":
    domains_subscription = [3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,19,20,21,22,23,24,25,26,27,28,29,30,31,33,34,
        35,36,38,39,40,41,44,45,46,47,49,50,51,52,53,54,55,56,57,69,70,71,72,73,74,75,76,77,85,86,88,89,96,98,99,105,
        112,113,115,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,59,60,61,62,63,64,65,66,67,68
        ]
    
    for k in domains_subscription:
        try:
            get_results("{0}".format(k))
        except:
            print("is active False")
    