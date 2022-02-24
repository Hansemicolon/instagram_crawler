import json
import random
import time

import requests as requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import db_conn
import pandas as pd

class item_crawl:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('disable-blink-features=AutomationControlled')
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-A102U; a10e; exynos7885; en_US; 239490550)")
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities,
                                       options=options)
        self.__config()
        self.result = []

    def __config(self):
        self.driver.get('https://www.instagram.com/accounts/login/')
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]')
                                               )
            )
        except Exception as e:
            print(str(e))
            time.sleep(random.uniform(10, 15))
        self.__login()
        return

    def __login(self):
        login_fail = True
        while login_fail:
            is_login: str = input("자동으로 로그인 하시겠습니까? (Y/N) - Y 선택 시 아이디, 패스워드 직접 입력 // N 선택 시 직접 입력")
            if is_login == "Y":
                login_id = input("인스타그램 로그인 아이디를 입력해주세요")
                login_pw = input("인스타그램 로그인 비밀번호를 입력해주세요")
                self.driver.find_element(By.CSS_SELECTOR, 'input[name="username"]').send_keys(login_id)
                self.driver.find_element(By.CSS_SELECTOR, 'input[name="password"]').send_keys(login_pw)
                self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
            else:
                input("직접 로그인을 진행하세요. 그리고 아무키나 입력하세요.")

            login_fail = self.__check_login_status()

    def __check_login_status(self):
        login_fail = True
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
        except Exception as e:
            # TODO logging
            login_fail = False
            print(str(e))
        print(f"Login Fail? : {str(-login_fail)}")
        return login_fail

    def str_cleaner(self,text):
        if not isinstance(text, str):
            return ""
        text = text.replace('\n', '').replace('\r', '').replace('\t', '')
        return text

    def parse_tag(self,text):
        t = text.split(' ')[0]
        t = self.str_cleaner(t)
        return t


    def main(self):
        get_data = db_conn.get_user_id()
        user_id = '48758234916'
        for user_id in get_data:
            after = 'QVFDelRkT2NtZGNOUWNJOU1CZHNmenhkSGxLcUZUYnBpc2hvRnlqb2JfbWdzZ0lSNWNYRXBQQkpNRDl0emxOVTl0WkFIajdPLTkteG94UzM5RWdwRUxMOQ%3D%3D%22%'
            url = f'https://www.instagram.com/graphql/query/?query_hash=8c2a529969ee035a5063f2fc8602a0fd&variables=%7B%22id%22%3A%22{user_id[0]}%22%2C%22first%22%3A12%2C%22after%22%3A%22{after}7D'
            self.driver.get(url)
            html_data = self.driver.page_source
            data = html_data[html_data.find('pre-wrap;">')+11:html_data.rfind("</pre></body></html>")]
            json_data = json.loads(data)
            node_list = json_data.get("data",{}).get("user",{}).get("edge_owner_to_timeline_media",{}).get("edges",[{}])
            for node in node_list:
                try:
                    content = node.get("node",{}).get("edge_media_to_caption",{}).get("edges",[{}])[0].get("node",{}).get("text",None)
                    if content is None:
                        tag_list = []
                    else:
                        tag_list = list(map(self.parse_tag, [x for x in content.split("#")
                                                        if content[content.find(x)-1] == '#' and content.find(x) != 0]))
                except:
                    tag_list = []

                item_list = [user_id[1], user_id[0], str(tag_list)]
                print(tag_list)
                self.result.append(item_list)
            db_conn.save_post_db(self.result)



if __name__ == '__main__':
    item_crawl().main()