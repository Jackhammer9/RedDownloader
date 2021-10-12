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
            urllib.request.urlretrieve(url+f'/DASH_{quality}.mp4',self.destination+"Video.mp4")
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
        with open(self.destination+'Audio.mp3', 'wb') as f:
            f.write(doc.content)
            f.close()

    def MergeVideo(self):
        try:
            print("Merging Files")
            clip = VideoFileClip(self.destination+"Video.mp4")
            try:
                audioclip = AudioFileClip(self.destination+"Audio.mp3")
                videoclip = clip.set_audio(audioclip)
                try:
                    videoclip.ipython_display()
                except:
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
        try:
            os.remove(self.destination+"Audio.mp3")
        except:
            pass
        if videoOnly:
            os.rename(self.destination+'Video.mp4',self.output+'.mp4')
            if self.destination != None:
                shutil.move(f"{self.output}.mp4" , self.destination)
        else: 
            os.rename('__temp__.mp4',self.output+'.mp4')
            os.remove(self.destination+"Video.mp4")
            if self.destination != None:
                shutil.move(f"{self.output}.mp4" , self.destination)

    def GetMediaType(self):
        if self.mediaType != None:
            return self.mediaType
        else:
            return None