from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as Firefox_Options
from time import sleep
import json
 
 
 
 
user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"
 
 
 
class InstaPusher:
 
    def __init__(self, login, password, user_agent):
 
        self.__login = login
        self.__password = password
        self.__isAuth = False
        self.__id = 0
 
        self.nickname = ""
        self.following_count = 0
        self.followers_count = 0
 
        self.__profile = webdriver.FirefoxProfile()
        self.__options = Firefox_Options()
        self.__options.add_argument('-headless')
        self.__profile.set_preference("general.useragent.override", user_agent)
        self.__profile.set_preference('permissions.default.image', 2)
 
        self.__driver = webdriver.Firefox(firefox_profile=self.__profile, firefox_options=self.__options)
        self.__driver.set_window_size(360,640)
 
        self.__authorization()
 
    def __go_to_profile(self):
        self.__driver.find_element_by_css_selector("[aria-label='Профиль']").click()
        sleep(1)
 
    def __get_my_nickname(self):
        self.__go_to_profile()
        current_url = str(self.__driver.current_url)
        return str(current_url).split("/")[-2]
 
 
    def __authorization(self):
        print("Start of authorization")
        self.__driver.get("http://www.instagram.com")
        sleep(2)
        self.__driver.find_element_by_link_text("Вход").click()
        sleep(1)
        self.__driver.find_element_by_name("username").send_keys(login)
        self.__driver.find_element_by_name("password").send_keys(password, Keys.ENTER)
        sleep(4)
        self.__isAuth = True
        self.nickname = self.__get_my_nickname()
        self.__get_my_data()
        print("Authorization is done. Hello, {}!".format(self.nickname))
 
    def __get_my_data(self):
        self.__driver.get("http://www.instagram.com/{}/?__a=1".format(self.nickname))
        user_data = json.loads(self.__driver.find_element_by_xpath("//div[@id='json']").text)["graphql"]["user"]
        self.__id = user_data["id"]
        self.followers_count = user_data["edge_followed_by"]["count"]
        self.following_count = user_data["edge_follow"]["count"]
        print("Your id: ", self.__id)
        print("Your followers count: ", self.followers_count)
        print("Your following count: ", self.following_count)
 
 
    def get_following_set(self, save_to_file=False, filename="fallowing.txt"):
        print("Start of getting following set")
        variables = {}
        variables["id"] = self.__id
        variables['first'] = 50
 
        first_shot = True
        last_shot = False
        url = "view-source:https://www.instagram.com/graphql/query/?query_hash=58712303d941c6855d4e888c5f0cd22f&variables="
 
        all_following = []
        page_info = {}
 
        while True:
            if first_shot:
                first_shot = False
            else:
                variables["after"] = page_info["end_cursor"]
            req_url = url + str(json.dumps(variables))
            self.__driver.get(req_url)
            pre = self.__driver.find_element_by_tag_name("pre").text
            data = json.loads(pre)['data']
            page_info = (data['user']['edge_follow']['page_info'])
            edges = data['user']['edge_follow']['edges']
            for user in edges:
                all_following.append(user['node']['username'])
            if not page_info["has_next_page"]:
                last_shot = True
            if last_shot:
                break
        print("Getting all fallowing set is complete")
        all_following = set(all_following)
        if save_to_file:
            print("Saving al fallowing in file")
            with open(filename, "w") as f:
                for user in all_following:
                    f.write("http://www.instagram.com/{}/\n".format(user))
            f.close()
            print("Saving is complete")
        return all_following
 
 
    def unfollow(self, count):
        print("Start of unfollow")
        all_following = list(self.get_following_set())
        for user in all_following[:count]:
            self.__driver.get("http://www.instagram.com/{}/".format(user))
            self.__driver.find_element_by_css_selector("[aria-label='Подписки']").click()
            self.__driver.find_element_by_xpath("//button[text()='Отменить подписку']").click()
            print("User {} was unfollowed".format(user))
        print("Unfollow complete")
        print("_________________________")
        self.__get_my_data()
        print("_________________________")
        self.__driver.get("http://www.instagram.com/{}/".format(self.nickname))

