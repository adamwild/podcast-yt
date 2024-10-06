
class YouTube_API():
    def __init__(self):

        # Set up the API client
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
        self.CLIENT_SECRET_FILE = 'client_secret.json'  # Path to your client secret JSON file
        self.API_SERVICE_NAME = 'youtube'
        self.API_VERSION = 'v3'

        self.youtube = self.get_authenticated_service()

        self.playlists = None

    def get_authenticated_service(self):
        import os
        import json
        import google.auth.transport.requests
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        token_path = 'token.json'

        # Load credentials from file if they exist
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        # If there are no (valid) credentials available, prompt the user to log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(google.auth.transport.requests.Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build(self.API_SERVICE_NAME, self.API_VERSION, credentials=creds)

    def get_playlists(self):
        import pandas as pd

        playlists = []
        request = self.youtube.playlists().list(
            part="snippet,contentDetails",
            mine=True,
            maxResults=50
        )
        
        while request:
            response = request.execute()
            playlists.extend(response.get('items', []))
            request = self.youtube.playlists().list_next(request, response)

        # Turn playlists list into concise DataFrame
        df_columns = ['title', 'id', 'publishedAt', 'channelId', 'channelTitle', 'itemCount']
        df_dict = {key:[] for key in df_columns}

        for playlist in playlists:
            df_dict['title'].append(playlist['snippet']['title'])
            df_dict['id'].append(playlist['id'])
            df_dict['publishedAt'].append(playlist['snippet']['publishedAt'])
            df_dict['channelId'].append(playlist['snippet']['channelId'])
            df_dict['channelTitle'].append(playlist['snippet']['channelTitle'])
            df_dict['itemCount'].append(playlist['contentDetails']['itemCount'])

        self.playlists = pd.DataFrame(df_dict)

        return self.playlists
    
    def get_playlist_id(self, name_playlist):
        if self.playlists is None:
            self.get_playlists()

        return self.playlists.loc[self.playlists['title']==name_playlist, 'id'].values[0]
    
    def list_videos_playlist_from_name(self, name_playlist):
        # Lists all videos of a playlist, given the playlist's name

        if self.playlists is None:
            self.get_playlists()
        
        playlist_id = self.playlists.loc[self.playlists['title']==name_playlist, 'id'].values[0]

        return self.list_videos_playlist_from_id(playlist_id)

    def list_videos_playlist_from_id(self, playlist_id, max_num_pages=1):

        def get_videos_in_playlist(playlist_id):
            videos = []
            request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50
            )
            
            num_page = 0
            while request and num_page < max_num_pages:
                response = request.execute()
                videos.extend(response.get('items', []))
                print(len(videos))
                request = self.youtube.playlistItems().list_next(request, response)

                num_page += 1

            return videos
        
        videos = get_videos_in_playlist(playlist_id)

        # Turn video list into concise DataFrame
        df_columns = ['title', 'videoId', 'publishedAt', 'videoPublishedAt', 'videoOwnerChannelTitle', 'videoOwnerChannelId', 'position']
        df_dict = {key:[] for key in df_columns}

        for video in videos:
            title = video['snippet']['title']

            df_dict['title'].append(title)
            df_dict['videoId'].append(video['snippet']['resourceId']['videoId'])

            df_dict['publishedAt'].append(video['snippet']['publishedAt'])

            if title != 'Private video' and title!= 'Deleted video':
                df_dict['videoPublishedAt'].append(video['contentDetails']['videoPublishedAt'])
                df_dict['videoOwnerChannelTitle'].append(video['snippet']['videoOwnerChannelTitle'])
                df_dict['videoOwnerChannelId'].append(video['snippet']['videoOwnerChannelId'])
            else:
                df_dict['videoPublishedAt'].append('')
                df_dict['videoOwnerChannelTitle'].append('')
                df_dict['videoOwnerChannelId'].append('')

            df_dict['position'].append(video['snippet']['position'])

        import pandas as pd

        df_videos = pd.DataFrame(df_dict)

        return df_videos

    def get_channel_id_by_name(self, channel_name):
        request = self.youtube.search().list(
            part="snippet",
            q=channel_name,
            type="channel",
            maxResults=1
        )
        response = request.execute()
        
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]['snippet']['channelId']
        else:
            return None
        
    def list_videos_channel(self, channel_name, max_num_pages=1):
        channel_id = self.get_channel_id_by_name(channel_name)

        videos = []
        request = self.youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,
            order="date",
            type="video"
        )
        
        num_page = 0
        while request and num_page < max_num_pages:
            response = request.execute()
            videos.extend(response.get('items', []))
            request = self.youtube.search().list_next(request, response)
            num_page += 1

        # Turn video list into concise DataFrame
        df_columns = ['title', 'videoId', 'publishedAt']
        df_dict = {key:[] for key in df_columns}

        for video in videos:
            title = video['snippet']['title']

            df_dict['title'].append(title)
            df_dict['videoId'].append(video['id']['videoId'])

            df_dict['publishedAt'].append(video['snippet']['publishedAt'])

        import pandas as pd

        df_videos = pd.DataFrame(df_dict)

        return df_videos
    
    def grab_videos_from_source(self, source_type, source_value, stop_condition, stop_condition_value):
        """Get video ids from a youtube source until a stop condition is met

        Args:
        source_type (str): 'channel_name', 'playlist_id', 'personnal_playlist_name'
        source_value (str): The value linked to the source_type
        stop_condition (str):
            'last_n_videos':    Grab the last n videos published on the channel/playlist
            'last_n_days':      Grab the videos published today and the last n days from source
            'vid_ids_to_reach': Grab videos until one of the video ids grabbed is in this list
        stop_condition_value (int or list[str]): int if stop_condition = 'last_n_videos' OR 'last_n_days'
                                                 list[str] if stop_condition = 'vid_ids_to_reach'
        """

        def get_videoId_from_video(video, source_type):
            if source_type == 'channel_name':
                return video['id']['videoId']

            elif source_type == 'playlist_id' or source_type == 'personnal_playlist_name':
                return video['snippet']['resourceId']['videoId']

        # Building the request object
        def get_request(source_type, source_value):

            # We have the name of a channel
            if source_type == 'channel_name':
                channel_id = self.get_channel_id_by_name(source_value)

                request = self.youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    maxResults=50,
                    order="date",
                    type="video"
                )

            # We have a playlist, either refered by id or by name (and in this case, created by the user)
            elif source_type == 'playlist_id' or source_type == 'personnal_playlist_name':
                if source_type == 'playlist_id':
                    playlist_id = source_value
                elif source_type == 'personnal_playlist_name':
                    playlist_id = self.get_playlist_id(source_value)

                request = self.youtube.playlistItems().list(
                part="snippet,contentDetails",
                playlistId=playlist_id,
                maxResults=50
            )
                
            return request
                
        request = get_request(source_type, source_value)
        

        # Getting videos until we get all videos or the stop condition is met
        videos = []
        latest_videos = ''

        def check_stop_condition(videos, latest_videos, source_type, stop_condition, stop_condition_value):
            # Tests if stop condition is met.
            # Returns True if loop is allowed to continue, False if not

            # Before first loop
            if latest_videos == '':
                return True

            if stop_condition == 'last_n_videos':
                if len(videos) >= stop_condition_value:
                    return False
                
            if stop_condition == 'last_n_days':
                #TODO later, it's complicated...
                print("TODO last_n_days")
                return

            if stop_condition == 'vid_ids_to_reach':

                for video in latest_videos:
                    if get_videoId_from_video(video) in stop_condition_value:
                        return False

            # No stop condition was met, the loop getting videos can continue 
            return True
                
        while request and check_stop_condition(videos, latest_videos, source_type, stop_condition, stop_condition_value):
            response = request.execute()
            latest_videos = response.get('items', [])
            videos.extend(latest_videos)
            request = self.youtube.search().list_next(request, response)

        
        # The 'videos' list is constructed, we will now build a Pandas DataFrame with relevant info
        columns = ['title', 'videoID', 'publishedAt', 'channelName']
        df_dict = {key:[] for key in columns}

        # 'publishedAt' is when the video has been made available from the source
        # i.e. when it was published by a channel or a added to a playlist

        for video in videos:

            if source_type == 'channel_name':
                df_dict['title'].append(video['snippet']['title'])
                df_dict['videoId'].append(video['id']['videoId'])
                df_dict['publishedAt'].append(video['snippet']['publishedAt'])

            elif source_type == 'playlist_id' or source_type == 'personnal_playlist_name':
                title = video['snippet']['title']
                if title != 'Private video' and title!= 'Deleted video':
                    df_dict['title'].append(title)
                    df_dict['videoId'].append(video['snippet']['resourceId']['videoId'])
                    df_dict['publishedAt'].append(video['snippet']['publishedAt'])

                
                    df_dict['videoPublishedAt'].append(video['contentDetails']['videoPublishedAt'])
                    df_dict['videoOwnerChannelTitle'].append(video['snippet']['videoOwnerChannelTitle'])
                    df_dict['videoOwnerChannelId'].append(video['snippet']['videoOwnerChannelId'])
                else:
                    df_dict['videoPublishedAt'].append('')
                    df_dict['videoOwnerChannelTitle'].append('')
                    df_dict['videoOwnerChannelId'].append('')



if __name__ == '__main__':
    pass


    


