from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import json, time, random


class InstaCrawler:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-A102U; a10e; exynos7885; en_US; 239490550)")
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities, options=options)
        self.__config()
        self.keyword = None

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

    @staticmethod
    def log_filter(log):
        return (log["method"] == "Network.responseReceived" and "json" in log["params"]["response"]["mimeType"])

    def __log_res_for_tag(self, logs):
        keyword = self.keyword
        result = []
        target_urls = (f'https://i.instagram.com/api/v1/tags/{keyword}/sections/',
                       f'https://www.instagram.com/explore/tags/{keyword}/?__a=1')
        for log in filter(self.log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            if resp_url in target_urls:
                item = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                result.append({'network_id': request_id, 'url': resp_url, 'item': item})
        return result

    def __get_content_list(self):
        logs_raw = self.driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
        return self.__log_res_for_tag(logs)

    def __get_tag_result(self):
        tag_result = []
        for i in range(0, 10):
            tag_result = self.__get_content_list()
            if len(tag_result) > 0:
                break
            time.sleep(random.uniform(1, 2))
        return tag_result

    def main(self, keyword: str, count: int = 5):
        self.keyword = keyword.lower()
        result = []
        url = f'https://www.instagram.com/explore/tags/{self.keyword}/'
        self.driver.get(url)
        result.extend(self.__get_tag_result())

        for i in range(0, count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            result.extend(self.__get_tag_result())

        return result


if __name__ == '__main__':
    import pickle
    c = InstaCrawler()
    is_running = True
    while is_running:
        input_keyword = input("(Required) 키워드를 입력하세요")
        input_count = input("(Optional) 수집할 페이지 수를 입력하세요(10 이상 입력 금지). 입력 하지 않거나 정수가 아닐시 5로 고정")
        try:
            input_count = int(input_count)
        except Exception as e:
            input_count = 5
        res = c.main(input_keyword, input_count)

        with open(f'{input_keyword}_res.pickle', 'wb') as f:
            pickle.dump(res, f, pickle.HIGHEST_PROTOCOL)
        run_status = input("종료 하시겠습니까? (Y/N)")
        is_running = True if run_status in ['Y', 'N'] and run_status == 'N' else False

    # TODO
    """
    현 인스타그램 크롤러는 한번 실행 후 종료되어 새로운 세션을 계속 만들어야 합니다.
    인스타그램에서는 이를 어뷰징으로 판단하여 점점 수집이 어려워집니다. 그래서 로그인을 유지한 상태에서 input 값을 받아 실행해야 합니다.
    이에 대한 아이디어로 main 아래에
    while True:
        keyword = input("키워드를 입력")
        res = c.main(keyword)
        # res -> save to db
    """