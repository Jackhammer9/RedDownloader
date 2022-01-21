import urllib.request
from moviepy.editor import *
import requests
from PIL import Image
import json
import os
import shutil

class Download:

    def __init__(self , url , quality = 720 , output = "downloaded" , destination=None):
        self.output = output
        self.destination = destination
        qualityTypes = [360,720,1080]
        if quality not in qualityTypes:
            print("Error: Unkown Quality Type" + f" {quality} choose either 360 , 720 , 1080")
        else:
            self.postLink = requests.get("https://jackhammer.pythonanywhere.com/reddit/media/downloader" , params={'url':url}).text
            if 'v.redd.it' in self.postLink:
                print("Detected Post Type: Video")
                self.mediaType = "v"
                self.InitiateVideo(quality , self.postLink)
            elif 'i.redd.it' in self.postLink:
                print("Detected Post Type: Image")
                self.mediaType = "i"
                imageData = requests.get(self.postLink).content
                file = open(f'{self.output}'+'.jpeg' , 'wb')
                file.write(imageData)
                file.close()
                print("Sucessfully Downloaded Image " + f"{self.output}")
                if self.destination != None:
                    shutil.move(f"{self.output}.jpeg" , self.destination)
            elif '/gallery/' in self.postLink:
                print("Detected Post Type: Gallery")
                self.mediaType= 'g'
                self.directory = os.path.join(self.destination , self.output)
                try:
                    os.mkdir(self.directory)
                except:
                    pass
                print("Fetching images from gallery")
                self.GalleryPosts = requests.get("https://jackhammer.pythonanywhere.com/reddit/media/gallery", params={'url':self.postLink})
                posts = json.loads(self.GalleryPosts.content)
                self.GetGallery(posts)
            else:
                print("Error: Could Not Recoganize Post Type")

    def GetGallery(self , posts):
        TotalPosts = len(posts)
        print("Total images to be downloaded: " , TotalPosts)
        for i in range(TotalPosts):
            print(f"Downloading image {i+1} / {TotalPosts}")
            ImageData = requests.get(posts[i]).content
            with open(os.path.join(self.directory , self.output+f'{i+1}.jpeg') , 'wb') as image:
                image.write(ImageData)
                image.close()
        print("Image Gallery Successfully Downloaded!")

    def InitiateVideo(self , quality , url):
        try:
            print('Fetching Video...')
            self.fetchVideo(quality , url)
            print('Fetching Audio...')
            self.fetchAudio(url)
        except:
            print("Sorry there was an error while fetching video/audio files")
        else:
            self.MergeVideo()

    def fetchVideo(self , quality , url):
        try:
            print(url , self.destination)
            if self.destination != None:
                urllib.request.urlretrieve(url+f'/DASH_{quality}.mp4',self.destination+"Video.mp4")
            else:
                urllib.request.urlretrieve(url+f'/DASH_{quality}.mp4', "Video.mp4")
        except:
            try:
                print(f'Error Downloading Video File May be an issue with avaliable quality at {quality}')
                print(f'trying resolution:720 ')
                urllib.request.urlretrieve(url+f'/DASH_720.mp4',self.destination+"Video.mp4")
            except:
                try:
                    print(f'Error Downloading Video File May be an issue with avaliable quality at 720&1080')
                    print(f'trying resolution:360 ')
                    urllib.request.urlretrieve(url+f'/DASH_360.mp4',self.destination+"Video.mp4")
                except:
                    print("Can't fetch the video file :(")

    def fetchAudio(self , url):
        doc = requests.get(url+'/DASH_audio.mp4')
        if self.destination != None:
            with open(self.destination+'Audio.mp3', 'wb') as f:
                f.write(doc.content)
                f.close()
        else:
            with open(''+'Audio.mp3', 'wb') as f:
                f.write(doc.content)
                f.close()


    def MergeVideo(self):
        try:
            print("Merging Files")
            if self.destination != None:
                clip = VideoFileClip(self.destination+"Video.mp4")
            else:
                clip = VideoFileClip("Video.mp4")
            try:
                if self.destination != None:
                    audioclip = AudioFileClip(self.destination+"Audio.mp3")
                else:
                    audioclip= AudioFileClip("Audio.mp3")
                new_audioclip = CompositeAudioClip([audioclip])
                clip.audio = new_audioclip
                try:
                    if self.destination != None:
                        clip.write_videofile(self.destination+self.output+".mp4")
                    else:
                        clip.write_videofile(self.output+".mp4")
                except Exception as e:
                    pass
                self.CleanUp()
                print(self.output + " Successfully Downloaded!")
                clip.close()
            except Exception as e:
                clip.close()
                print('Video has no sound')
                self.CleanUp(True)
                print(self.output + " Successfully Downloaded!")
        except Exception as e:
            print("Merge Failed!")
            print(e)

    def CleanUp(self , videoOnly = False):
        print('cleaning')
        try:
            if self.destination != None:
                os.remove(self.destination+"Audio.mp3")
            else:
                os.remove("Audio.mp3")
        except:
            pass
        if videoOnly == False:
            if self.destination != None:
                os.remove(self.destination+"Video.mp4")
            else:
                os.remove("Video.mp4")
        else:
            try:
                os.rename(self.destination+"Video.mp4" , self.destination+self.output + ".mp4")
            except Exception as e:
                print(e)

    def GetMediaType(self):
        if self.mediaType != None:
            return self.mediaType
        else:
            return None

class DownloadBySubreddit:

    def __init__(self , Subreddit , NumberOfPosts , flair = None , SortBy = "hot" , quality = 720 , output = "downloaded" , destination=None):
        if SortBy == "hot" or SortBy =="new" or SortBy=="top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get("https://jackhammer.pythonanywhere.com//reddit/subreddit/all", params={'subreddit':Subreddit , 'number':NumberOfPosts , 'flair':flair , 'sort':SortBy})
                Links = json.loads(self.PostLinks.content)
                self.DownloadLinks(Links , quality , output ,destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self , links , quality , output , destination):
        print("Downloading Posts...")
        print("Creating " , output , " directory...")
        path = ''
        try:
            if destination != None:
                path = os.path.join(destination , output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except:
            pass
        length = len(links)
        i=1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination != None:
                    Download(link , quality , output+str(i) , destination+f'/{output}/')
                else:
                    Download(link , quality , output+str(i) , f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)

class DownloadImagesBySubreddit:

    def __init__(self , Subreddit , NumberOfPosts , flair = None , SortBy = "hot" , quality = 720 , output = "downloaded" , destination=None):
        if SortBy == "hot" or SortBy =="new" or SortBy=="top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get("https://jackhammer.pythonanywhere.com//reddit/subreddit/images", params={'subreddit':Subreddit , 'number':NumberOfPosts , 'flair':flair , 'sort':SortBy})
                Links = json.loads(self.PostLinks.content)
                self.DownloadLinks(Links , quality , output ,destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self , links , quality , output , destination):
        print("Downloading Posts...")
        print("Creating " , output , " directory...")
        path = ''
        try:
            if destination != None:
                path = os.path.join(destination , output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except:
            pass
        length = len(links)
        i=1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination != None:
                    Download(link , quality , output+str(i) , destination+f'/{output}/')
                else:
                    Download(link , quality , output+str(i) , f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)


class DownloadVideosBySubreddit:

    def __init__(self , Subreddit , NumberOfPosts , flair = None , SortBy = "hot" , quality = 720 , output = "downloaded" , destination=None):
        if SortBy == "hot" or SortBy =="new" or SortBy=="top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get("https://jackhammer.pythonanywhere.com//reddit/subreddit/videos", params={'subreddit':Subreddit , 'number':NumberOfPosts , 'flair':flair , 'sort':SortBy})
                Links = json.loads(self.PostLinks.content)
                self.DownloadLinks(Links , quality , output ,destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self , links , quality , output , destination):
        print("Downloading Posts...")
        print("Creating " , output , " directory...")
        path = ''
        try:
            if destination != None:
                path = os.path.join(destination , output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except:
            pass
        length = len(links)
        i=1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination != None:
                    Download(link , quality , output+str(i) , destination+f'/{output}/')
                else:
                    Download(link , quality , output+str(i) , f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)

class DownloadGalleriesBySubreddit:

    def __init__(self , Subreddit , NumberOfPosts , flair = None , SortBy = "hot" , quality = 720 , output = "downloaded" , destination=None):
        if SortBy == "hot" or SortBy =="new" or SortBy=="top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get("https://jackhammer.pythonanywhere.com//reddit/subreddit/galleries", params={'subreddit':Subreddit , 'number':NumberOfPosts , 'flair':flair , 'sort':SortBy})
                Links = json.loads(self.PostLinks.content)
                self.DownloadLinks(Links , quality , output ,destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self , links , quality , output , destination):
        print("Downloading Posts...")
        print("Creating " , output , " directory...")
        path = ''
        try:
            if destination != None:
                path = os.path.join(destination , output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except:
            pass
        length = len(links)
        i=1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination != None:
                    Download(link , quality , output+str(i) , destination+f'/{output}/')
                else:
                    Download(link , quality , output+str(i) , f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)