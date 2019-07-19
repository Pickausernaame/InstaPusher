import os
import json
import requests
from vkTaker import VkTaker
from coubTaker import CoubTaker
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as Firefox_Options
from youtubeTaker import YoutubeTaker



class Butler:

    def __init__(self, path=os.getcwd()):
        self.__options = Firefox_Options()
        self.__options.add_argument('-headless')
        self.__driver = webdriver.Firefox(firefox_options=self.__options)
        self.path = path
        self.coub_path = path + "/coub"
        self.coub_taker = CoubTaker(self.coub_path)
        try:
            os.mkdir(self.coub_path)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise
            pass
        self.youtube_path = path + "/youtube"
        self.youtube_taker = YoutubeTaker(self.youtube_path)
        try:
            os.mkdir(self.youtube_path)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise
            pass
        self.insta_path = path + "/insta"
        self.insta_taker = VkTaker(self.path)
        try:
            os.mkdir(self.insta_path)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise
            pass
        self.vk_path = path + "/vk"
        self.vk_taker = VkTaker(self.vk_path)
        try:
            os.mkdir(self.vk_path)
        except OSError as e:
            if e.errno != os.errno.EEXIST:
                raise
            pass

    def get_content(self, url: str):
        self.__taking_url(url)

    def __taking_url(self, url):
        parts = url.split("/")
        for i, part in enumerate(parts):
            if part == "vk.com" or part == "m.vk.com":
                parts[i] = "m.vk.com"
                # todo checking link in database
                options = self.__prepare_vk_options(parts)
                if options["video_url"] != "None" or options["audio_url"] != "None":
                    self.vk_taker.take(options)
                return
            if part == "coub.com":
                # todo checking link in database
                options = self.__prepare_coub_options(url)
                if options["video_url"] != "None" or options["audio_url"] != "None":
                    self.coub_taker.take(options)
                return
            # if part == "www.instagram.com" or part == "instagram.com":
            #     options = self.__prepare_insta_options(url)
            #     if options ["video_url"] != "None" or options["audio_url"] != "None":
            #         self.insta_taker.take(options)
            #     return
            if part ==  "www.youtube.com" or part == "m.youtube.com":
                print(url)
                options = {"video_url": url, "audio_url": "None", "with_video": True, "with_audio": True}
                self.youtube_taker.take(options)



    @staticmethod
    def __prepare_vk_options(parts, resolution="1080", with_video=True, with_audio=True):
        resolutions = ["720", "480", "360", "240"]
        url = "/".join(parts)
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
        try:
            page = requests.get(url, headers=headers)
        except Exception as e:
            print("Bad url\n", e)
            raise ArithmeticError
        data = page.text
        att = "url" + str(resolution)
        for res in resolutions:
            try:
                start_ind = data.index(att)
            except ValueError:
                print("Wrong resolution {}".format(att[3:]))
                att = "url" + res
            else:
                print("Current resolution {}".format(att[3:]))
                try:
                    end_ind = data.index("?", start_ind)
                    url = data[(start_ind + len(att) + 1):end_ind]
                    url = url[2:]
                    url = url.replace("\/", "/")
                except Exception as e:
                    print("Bad url\n", e)
                    raise ArithmeticError
                else:
                    options = {"video_url": url, "audio_url": "None", "with_video": with_video, "with_audio": with_audio}
                    return options


    @staticmethod
    def __prepare_coub_options(url, resolution="high", with_video=True, with_audio=True):
        if resolution not in ["high", "med"]:
            resolution = "high"
        try:
            data_url = url.replace("https://coub.com/view/", "http://coub.com/api/v2/coubs/")
        except Exception as e:
            print("Bad url\n", e)
            raise ArithmeticError
        else:
            try:
                video_url = requests.get(data_url).json()["file_versions"]["html5"]["video"][resolution]["url"]
                audio_url = requests.get(data_url).json()["file_versions"]["html5"]["audio"][resolution]["url"]
            except KeyError as e:
                resolution = "med"
                video_url = requests.get(data_url).json()["file_versions"]["html5"]["video"][resolution]["url"]
                audio_url = requests.get(data_url).json()["file_versions"]["html5"]["audio"][resolution]["url"]
            except Exception as e:
                raise ArithmeticError
            options = {"video_url": video_url, "audio_url": audio_url, "with_video": with_video, "with_audio": with_audio}
            return options

    def __prepare_insta_options(self, url, with_video=True, with_audio=True):
        try:
            url = url + "?__a=1"
            self.__driver.get(url)

            data = json.loads(self.__driver.find_element_by_xpath("//div[@id='json']").text)["graphql"]["shortcode_media"]
            if data["__typename"] != "GraphVideo":
                print("Bad url")
                raise Exception
            video_url = data["video_url"]
        except Exception as e:
            print("Bad url\n", e)
            raise ArithmeticError
        else:
            options = {"video_url": video_url, "with_video": with_video, "with_audio": with_audio}
            return options
