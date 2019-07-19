import requests
import datetime

from moviepy.editor import VideoFileClip, AudioFileClip
import os
from abstractTaker import AbstractTaker


class CoubTaker(AbstractTaker):

    def __init__(self, path: str):
        super(CoubTaker, self).__init__(path)

    def _take_video(self, url):
        try:
            video = requests.get(url)
        except Exception as e:
            print("Bad url\n", e)
            return
        filename = str(datetime.datetime.now()) + ".mp4"
        self.__path_to_save_video = self.path + "/" + filename
        with open(self.__path_to_save_video, "wb") as f:
            try:
                f.write(b'\x00\x00' + video.content[2:])
            except Exception as e:
                print("Error of writing in file.\n", e)
                return
        print("Video {0} was saved in {1}".format(filename, self.__path_to_save_video))

    def _take_audio(self, url: str):
        try:
            audio = requests.get(url)
        except Exception as e:
            print("Bad url\n", e)
            return
        filename = str(datetime.datetime.now()) + ".mp3"
        self.__path_to_save_audio = self.path + "/" + filename
        with open(self.__path_to_save_audio, "wb") as f:
            try:
                f.write(b'\x00\x00' + audio.content[2:])
            except Exception as e:
                print("Error of writing in file.\n", e)
                return
        print("Audio {0} was saved in {1}".format(filename, self.__path_to_save_audio))

    def take(self, options: dict):
        if options["with_video"]:
            self._take_video(options["video_url"])
        if options["with_audio"]:
            self._take_audio(options["audio_url"])
            if options["with_video"]:
                video = VideoFileClip(self.__path_to_save_video)
                audio = AudioFileClip(self.__path_to_save_audio)
                video.audio = audio.set_duration(video.duration)
                os.remove(self.__path_to_save_video)
                os.remove(self.__path_to_save_audio)
                video.write_videofile(self.__path_to_save_video)
