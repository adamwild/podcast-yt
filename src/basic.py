class Basic:
    def __init__(self):
        from pathlib import Path
        from dotenv import load_dotenv
        
        main_folder = Path(__file__).parent.parent
        path_environment = str(main_folder / 'environment.env')
        load_dotenv(dotenv_path=path_environment, override=True)
        
        self.root_dl = self.get_root_dl()
        
    def get_root_dl(self):
        import os
        
        roots_dl = os.getenv('ROOT_DL')
        
        for root in roots_dl.split(','):
            root = root.strip()
            if os.path.exists(root):
                print("Root for downloads set at {0}".format(root))
                return root
            
        print("No root found !")
        
    def download(self, weblink, subtitles=False):
        import os
        cwd = os.getcwd()
        
        os.chdir(self.root_dl)
        
        if "www.youtube.com" in weblink:
            if not subtitles:
                os.system('yt-dlp -S "res:1080,fps" {0}'.format(weblink))
            else:
                os.system('yt-dlp -S "res:1080,fps" --write-subs --sub-langs "en.*,fr" {0}'.format(weblink))
                
        elif "www.arte.tv" in weblink:
            os.system('yt-dlp --audio-multistreams -f bestvideo+VOF-audio_0-Français {0}'.format(weblink))
                
        else:
            os.system('yt-dlp {0}'.format(weblink))
            
        os.chdir(cwd)
                
        
if __name__ == "__main__":
    bsc = Basic()
        