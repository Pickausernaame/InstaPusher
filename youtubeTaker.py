from abstractTaker import AbstractTaker
from pytube import YouTube
import requests
import datetime
from moviepy.editor import VideoFileClip


class YoutubeTaker(AbstractTaker):

    def __init__(self, path):
        super(YoutubeTaker, self).__init__(path)
        self.streams = None


    def take(self, options):
        self.streams = YouTube(options["video_url"])
        print(self.streams)

        # if not options["with_audio"]:
        #     self._remove_audio()
        # elif not options["with_video"]:
        #     self._take_audio()
        #     self._remove_file(self.path_to_save_video)

    def _take_video(self, url):
        try:
            video = requests.get(url)
        except Exception as e:
            print("Bad url\n", e)
            return
        filename = str(datetime.datetime.now()) + ".mp4"
        self.path_to_save_video = self.path + "/" + filename
        with open(self.path_to_save_video, "wb") as f:
            try:
                f.write(b'\x00\x00' + video.content[2:])
            except Exception as e:
                print("Error of writing in file.\n", e)
                return
        print("Video {0} was saved in {1}".format(filename, self.path_to_save_video))

    def _remove_audio(self):
        video = VideoFileClip(self.path_to_save_video)
        video = video.without_audio()
        os.remove(self.path_to_save_video)
        video.write_videofile(self.path_to_save_video)

    def _take_audio(self, url):
        video = VideoFileClip(self.path_to_save_video)
        self.path_to_save_audio = self.path_to_save_video[:-1] + "3"
        audio = video.audio
        audio.write_audiofile(self.path_to_save_audio)



    def _remove_file(self, path_to_file):
        try:
            os.remove(path_to_file)
        except Exception as e:
            print(e)
