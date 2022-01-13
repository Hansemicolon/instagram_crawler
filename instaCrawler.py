from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import DesiredCapabilities
from selenium import webdriver
import json
import time


class InstaCrawler:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 9; SM-A102U Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Instagram 155.0.0.37.107 Android (28/9; 320dpi; 720x1468; samsung; SM-A102U; a10e; exynos7885; en_US; 239490550)")
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities, options=options)
        self.__config()

    def __config(self):
        self.driver.get('https://www.instagram.com/accounts/login/')
        input("인스타그램 로그인을 진행해주세요.")

    @staticmethod
    def log_filter(log):
        return (log["method"] == "Network.responseReceived" and "json" in log["params"]["response"]["mimeType"])

    def __log_res_for_tag(self, logs, keyword):
        result = []
        target_urls = (f'https://i.instagram.com/api/v1/tags/{keyword}/sections/',
                       f'https://www.instagram.com/explore/tags/{keyword}/?__a=1')
        for log in filter(self.log_filter, logs):
            request_id = log["params"]["requestId"]
            resp_url = log["params"]["response"]["url"]
            if resp_url in target_urls:
                item = self.driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                result.append({request_id: item})
        return result

    def __get_content_list(self, keyword):
        logs_raw = self.driver.get_log("performance")
        logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
        return self.__log_res_for_tag(logs, keyword)

    def main(self, keyword, count: int = 5):
        result = []
        url = f'https://www.instagram.com/explore/tags/{keyword}/'
        self.driver.get(url)
        time.sleep(2)
        result.extend(self.__get_content_list(keyword))

        for i in range(0, count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            result.extend(self.__get_content_list(keyword))

        return result


if __name__ == '__main__':
    import pickle
    keyword = 'istj'
    c = InstaCrawler()
    res = c.main(keyword)

    with open(f'{keyword}_res.pickle', 'wb') as f:
        pickle.dump(res, f, pickle.HIGHEST_PROTOCOL)

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