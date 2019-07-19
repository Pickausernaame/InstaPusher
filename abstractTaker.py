from abc import ABC, abstractmethod


class AbstractTaker(ABC):
    def __init__(self, path: str):
        self.path = path
        self.path_to_save_video = ""
        self.path_to_save_audio = ""

    @abstractmethod
    def take(self, options: dict):
        pass

    @abstractmethod
    def _take_audio(self, url: str):
        pass

    @abstractmethod
    def _take_video(self, url: str):
        pass
