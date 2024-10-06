from src.yt_podcast.TaskManager import TaskManager

class PlaylistManager(TaskManager):
    def __init__(self) -> None:
        super().__init__()
        from config import PLAYLISTS_TO_DOWNLOAD
        from src.yt_podcast.yt_api import YouTube_API

        self.playlists = PLAYLISTS_TO_DOWNLOAD
        self.yt_api = YouTube_API()

    