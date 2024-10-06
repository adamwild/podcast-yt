class TaskManager:
    def __init__(self) -> None:
        from config import ROOT_PODCASTS
        self.root_podcasts = ROOT_PODCASTS

    def scan_podcast_folder(self):
        # Gets recursively all the files
        import os

        file_paths = []
        for root, directories, files in os.walk(self.root_podcasts):
            for filename in files:
                # Join the two strings to form the full file path.
                file_path = os.path.join(root, filename)
                file_paths.append(file_path)
        return file_paths
    
    def get_available_videos(self):
        # Get all the videos previously downloaded
        import pandas as pd

        def get_id_from_video_name(s):
            # Find the position of the last closing bracket
            end_index = s.rfind(']')
            if end_index == -1:
                return None  # No closing bracket found
            
            # Find the position of the last opening bracket before the last closing bracket
            start_index = s.rfind('[', 0, end_index)
            if start_index == -1:
                return None  # No opening bracket found before the last closing bracket
            
            # Extract and return the content between the brackets
            return s[start_index + 1:end_index]

        file_paths = self.scan_podcast_folder()
        columns = ['videoId', 'path_video']

        df_dic = {col:[] for col in columns}

        for file_path in file_paths:
            df_dic['videoId'].append(get_id_from_video_name(file_path))
            df_dic['path_video'].append(file_path)

        return pd.DataFrame(df_dic)

    def get_task_table(self):
        # Creates the task table, 
        self.task_table = None
        
        return self.task_table
    
    def manage_tasks(self):
        task_table = self.get_task_table()

        #TODO

if __name__ == '__main__':
    TM = TaskManager()
    print(TM.get_available_videos())