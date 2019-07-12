from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as Firefox_Options
from time import sleep
import json
from Printer import Printer
import progressbar

user_agent = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 3_0 like Mac OS X; en-us) AppleWebKit/528.18 (KHTML, like Gecko) Version/4.0 Mobile/7A341 Safari/528.16"


class InstaPusher:

    def __init__(self, login, password, user_agent=user_agent):

        self.__login = login
        self.__password = password
        self.__isAuth = False
        self.__id = 0

        self.nickname = ""
        self.following_count = 0
        self.followers_count = 0

        self.__profile = webdriver.FirefoxProfile()
        self.__options = Firefox_Options()
        #self.__options.add_argument('-headless')
        self.__profile.set_preference('intl.accept_languages', 'ru')
        self.__profile.set_preference("general.useragent.override", user_agent)
        self.__profile.set_preference('permissions.default.image', 2)

        self.__driver = webdriver.Firefox(firefox_profile=self.__profile, firefox_options=self.__options)
        self.__driver.set_window_size(360, 640)

        self.__authorization()

    def __go_to_profile(self):
        self.__driver.find_element_by_css_selector("[aria-label='Профиль']").click()
        sleep(1)

    def __get_my_nickname(self):
        self.__go_to_profile()
        current_url = str(self.__driver.current_url)
        return str(current_url).split("/")[-2]

    def __authorization(self):
        Printer.START("Start of authorization \n")
        self.__driver.get("http://www.instagram.com")
        sleep(2)
        self.__driver.find_element_by_link_text("Вход").click()
        sleep(1)
        self.__driver.find_element_by_name("username").send_keys(self.__login)
        self.__driver.find_element_by_name("password").send_keys(self.__password, Keys.ENTER)
        sleep(4)
        self.__isAuth = True
        self.nickname = self.__get_my_nickname()
        self.update_my_data()
        Printer.OK("Authorization is done. Hello, {}!\n".format(self.nickname))


    def __get_account_data(self, nickname):
        self.__driver.get("http://www.instagram.com/{}/?__a=1".format(nickname))
        account_data = json.loads(self.__driver.find_element_by_xpath("//div[@id='json']").text)
        return account_data["graphql"]["user"]

    def update_my_data(self):
        user_data = self.__get_account_data(self.nickname)
        self.__id = user_data["id"]
        self.followers_count = user_data["edge_followed_by"]["count"]
        self.following_count = user_data["edge_follow"]["count"]

        print("Your id: {}".format(self.__id))
        print("Your followers count: {}".format(self.followers_count))
        print("Your following count: {}\n".format(self.following_count))

    def get_user_data(self, nickname):
        Printer.START("Start of getting {}'s data\n".format(nickname))
        user_data = self.__get_account_data(nickname)

        print("{}'s id: {}".format(nickname, user_data["id"]))
        print("{}'s followers count: {}".format(nickname, user_data["edge_followed_by"]["count"]))
        print("{}'s following count: {}\n".format(nickname, user_data["edge_follow"]["count"]))
        return user_data

    def __get_account_following_set(self, id):
        Printer.START("Start of getting following set")

        variables = {}
        variables["id"] = id
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
        Printer.OK("Getting all fallowing set is complete")
        all_following = set(all_following)
        return all_following

    def get_user_following_set(self, nickname):
        user_data = self.get_user_data(nickname)
        all_following = self.__get_account_following_set(user_data["id"])
        return all_following

    def get_my_following_set(self, save_to_file=False, filename="fallowing.txt"):
        all_following = self.__get_account_following_set(self.__id)
        if save_to_file:
            InstaPusher.__save_to_file(all_following, filename)
        return all_following


    def __unfollow(self, following_list):
       Printer.START("Start of unfollow\n")
       bar = progressbar.ProgressBar(max_value=len(following_list))
       for user, i in enumerate(following_list):
           bar.update(i)
           self.__driver.get("http://www.instagram.com/{}/".format(user))
           self.__driver.find_element_by_css_selector("[aria-label='Подписки']").click()
           self.__driver.find_element_by_xpath("//button[text()='Отменить подписку']").click()
           print("User {} was unfollowed".format(user))
       Printer.OK("Unfollow complete")
       print("_________________________")
       self.update_my_data()
       print("_________________________")
       self.__driver.get("http://www.instagram.com/{}/".format(self.nickname))

    def unfollow_by_list(self, following_list):
        self.__unfollow(following_list)

    def auto_unfollow(self, count=-1):
        if count == -1:
            count = self.following_count
        all_following = list(self.get_my_following_set())
        self.__unfollow(all_following[:count])

    def __get_account_followers_set(self, id):
        Printer.START("Start of getting followers")

        variables = {}
        variables["id"] = id
        variables['first'] = 50

        first_shot = True
        last_shot = False

        url = "view-source:https://www.instagram.com/graphql/query/?query_hash=37479f2b8209594dde7facb0d904896a&variables="

        unfollowing_followers = []
        following_followers = []
        all_followers = []

        page_info = {}

        while True:
            if first_shot:
                first_shot = False
            else:
                variables["after"] = page_info["end_cursor"]

            req_url = url + str(json.dumps(variables))
            print(req_url)
            self.__driver.get(req_url)
            pre = self.__driver.find_element_by_tag_name("pre").text
            data = json.loads(pre)['data']
            page_info = (data['user']['edge_followed_by']['page_info'])
            edges = data['user']['edge_followed_by']['edges']
            for user in edges:
                all_followers.append(user['node']['username'])
                if user['node']['followed_by_viewer'] == True:
                    following_followers.append(user['node']['username'])
                else:
                    unfollowing_followers.append(user['node']['username'])
            if not page_info["has_next_page"]:
                last_shot = True
            if last_shot:
                break
        Printer.OK("Getting all fallowing set is complete")
        all_followers = set(all_followers)
        return all_followers, following_followers, unfollowing_followers



    def get_user_followers_set(self, nickname):
        user_data = self.get_user_data(nickname)
        all_followers = self.__get_account_followers_set(user_data["id"])
        return all_followers

    def get_my_followers_set(self, save_to_file=False, filename="followers.txt"):
        all_followers = self.__get_account_followers_set(self.__id)
        if save_to_file:
            InstaPusher.__save_to_file(all_followers, filename)
        return all_followers

    @staticmethod
    def __save_to_file(data, filename):
        Printer.START("Saving all fallowing in file")
        with open(filename, "w") as f:
            for unit in data:
                f.write("http://www.instagram.com/{}/\n".format(unit))
        f.close()
        Printer.OK("Saving is complete")

    def __get_all_account_posts(self, id):
        Printer.START("Start of getting posts")

        variables = {}
        variables["id"] = id
        variables['first'] = 50

        first_shot = True
        last_shot = False
        query_hash = "f2405b236d85e8296cf30347c9f08c2a"
        url = "view-source:https://www.instagram.com/graphql/query/?query_hash={}&variables=".format(query_hash)

        all_posts = []
        liked_posts = []
        not_liked_posts = []
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
            page_info = (data['user']['edge_owner_to_timeline_media']['page_info'])
            edges = data['user']['edge_owner_to_timeline_media']['edges']
            for post in edges:
                all_posts.append("p/" + post['node']['shortcode'])
                if post['node']['viewer_has_liked']:
                    liked_posts.append("p/" + post['node']['shortcode'])
                else:
                    not_liked_posts.append("p/" + post['node']['shortcode'])
            if not page_info["has_next_page"]:
                last_shot = True
            if last_shot:
                break
        Printer.OK("Getting all posts set is complete")
        all_posts = set(all_posts)
        return all_posts, liked_posts, not_liked_posts

    def get_my_all_posts(self):
        all_posts = self.__get_all_account_posts(self.__id)
        return all_posts

    def get_user_all_posts(self, nickname):
        user_data = self.get_user_data(nickname)
        all_posts = self.__get_all_account_posts(user_data["id"])
        return all_posts

    def __like(self, post_list):
        bar = progressbar.ProgressBar(max_value=len(post_list))
        for i, post in enumerate(post_list):
            print(type(i), "  ", i)
            bar.update(i)
            self.__driver.get("http://www.instagram.com/{}/".format(post))
            sleep(1)
            try:
                self.__driver.find_element_by_css_selector("[aria-label='Нравится']").click()
            except:
                continue

    def auto_like(self, nickname, count):
        Printer.START("Starting of LIKEMACHINE. Target - {}".format(nickname))
        all_posts = self.get_user_all_posts(nickname)
        if count < 0 or count > len(all_posts):
            count = len(all_posts)
        self.__like(all_posts[:count])

    def like_by_list(self, post_list):
        self.__like(post_list)

    def auto_unlike(self, nickname, count):
        Printer.START("Starting of UNLIKEMACHINE. Target - {}\n".format(nickname))
        all_posts = self.get_user_all_posts(nickname)
        bar = progressbar.ProgressBar(max_value=len(all_posts))
        for post, i in enumerate(all_posts[:count]):
            bar.update(i)
            self.__driver.get("http://www.instagram.com/{}/".format(post))
            sleep(1)
            try:
                self.__driver.find_element_by_css_selector("[aria-label='Не нравится']").click()
            except:
                continue
        Printer.OK("Unlike is done\n")


    def __follow(self, follow_list):
        bar = progressbar.ProgressBar(max_value=len(follow_list))
        for user, i in enumerate(follow_list):
            bar.update(i)
            self.__driver.get("http://www.instagram.com/{}/".format(user))
            sleep(1)
            try:
                self.__driver.find_element_by_xpath("//button[text()='Подписаться']").click()
            except:
                continue

    def follow_by_list(self, follow_list):
        self.__follow(follow_list)

    def auto_follow(self, nickname, count=-1):
        Printer.START("Starting of auto following. Target followers from user - {}\n".format(nickname))
        user_data = self.get_user_data(nickname)
        if count < 0:
            count = user_data["edge_owner_to_timeline_media"]
        all_followers = self.__get_account_followers_set(user_data["id"])
        self.__follow(all_followers[:count])
        Printer.OK("Auto following is done\n")
