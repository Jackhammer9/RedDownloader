'''
This is the main source file for RedDownloader Version 3.1.1 with it's primary
usage being downloading Reddit Posts i.e Image Posts , Videos , Gifs , Gallery
Posts.

A collection of class names:

                    *Download
                    *DownloadBySubreddit
                    *DownloadVideosBySubreddit
                    *DownloadImagesBySubreddit
                    *DownloadGalleryBySubreddit
                    *GetPostAuthor

A collection of endpoints being used:

                    *https://jackhammer.pythonanywhere.com/reddit/media/downloader
                    *https://jackhammer.pythonanywhere.com/reddit/media/gallery
                    *https://jackhammer.pythonanywhere.com//reddit/subreddit/all
                    *https://jackhammer.pythonanywhere.com/reddit/subreddit/gallery
                    *https://jackhammer.pythonanywhere.com/reddit/subreddit/images
                    *https://jackhammer.pythonanywhere.com/reddit/subreddit/videos
                    *https://jackhammer.pythonanywhere.com/reddit/media/author
'''

# Internal Imports
import urllib.request
import json
import os
import shutil

# External Imports | Required Packages
from moviepy.editor import *
import requests
from PIL import Image


class Download:
    '''This is the base class for RedDownloader all downloads are done
       through it.

       ...

       |Parameters|

            url: str
                The url of the post to be downloaded.
            quality: int
                The resolution of the video (if applicable) to be
                downloaded
                accepted values are:
                360 , 720 , 1080.
            output: str
                Output file name.
            destination: str
                The path destination where file will be downloaded.

        |Public Functions|

            GetMediaType()
                Return Type : str
                Returns the type of media that is being downloaded.
                'i' for image
                'v' for video
                'g' for gallery

    '''

    def __init__(
            self,
            url,
            quality=720,
            output="downloaded",
            destination=None):
        self.output = output
        self.destination = destination
        qualityTypes = [360, 720, 1080]
        if quality not in qualityTypes:  # if quality is not in the list
            print("Error: Unkown Quality Type" +  # Throw an error
                  f" {quality} choose either 360 , 720 , 1080")
        else:
            # Getting the absolute reddit post link
            self.postLink = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/media/downloader",
                params={
                    'url': url}).text
            if 'v.redd.it' in self.postLink:  # if the post is a video
                print("Detected Post Type: Video")
                self.mediaType = "v"
                self.InitiateVideo(quality, self.postLink)
            elif 'i.redd.it' in self.postLink:  # if the post is an image
                print("Detected Post Type: Image")
                self.mediaType = "i"
                imageData = requests.get(self.postLink).content
                file = open(f'{self.output}' + '.jpeg', 'wb')
                file.write(imageData)
                file.close()
                print("Sucessfully Downloaded Image " + f"{self.output}")
                if self.destination is not None:
                    shutil.move(f"{self.output}.jpeg", self.destination)
            elif '/gallery/' in self.postLink:  # if the post is a gallery
                print("Detected Post Type: Gallery")
                self.mediaType = 'g'
                self.directory = os.path.join(self.destination, self.output)
                try:
                    # making a directory for the gallery
                    os.mkdir(self.directory)
                except BaseException:
                    pass
                print("Fetching images from gallery")
                # Fetching urls of all media in the post
                self.GalleryPosts = requests.get(
                    "https://jackhammer.pythonanywhere.com/reddit/media/gallery",
                    params={
                        'url': self.postLink})
                posts = json.loads(self.GalleryPosts.content)
                self.GetGallery(posts)
            else:
                print("Error: Could Not Recoganize Post Type")

    def GetGallery(self, posts):  # Function to download and merge all images in a directory
        TotalPosts = len(posts)
        print("Total images to be downloaded: ", TotalPosts)
        for i in range(TotalPosts):
            print(f"Downloading image {i+1} / {TotalPosts}")
            ImageData = requests.get(posts[i]).content
            with open(os.path.join(self.directory, self.output + f'{i+1}.jpeg'), 'wb') as image:
                image.write(ImageData)
                image.close()
        print("Image Gallery Successfully Downloaded!")

    def InitiateVideo(self, quality, url):
        try:
            print('Fetching Video...')
            self.fetchVideo(quality, url)
            print('Fetching Audio...')
            self.fetchAudio(url)
        except BaseException:
            print("Sorry there was an error while fetching video/audio files")
        else:
            self.MergeVideo()

    # Getting the Audioless Video only file of a specified resolution from
    # Reddit
    def fetchVideo(self, quality, url):
        try:
            print(url, self.destination)
            if self.destination is not None:
                urllib.request.urlretrieve(
                    url + f'/DASH_{quality}.mp4',
                    self.destination + "Video.mp4")
            else:
                urllib.request.urlretrieve(
                    url + f'/DASH_{quality}.mp4', "Video.mp4")
        except BaseException:
            try:
                print(
                    f'Error Downloading Video File May be an issue with avaliable quality at {quality}')
                print(f'trying resolution:720 ')
                urllib.request.urlretrieve(
                    url + f'/DASH_720.mp4',
                    self.destination + "Video.mp4")
            except BaseException:
                try:
                    print(
                        f'Error Downloading Video File May be an issue with avaliable quality at 720&1080')
                    print(f'trying resolution:360 ')
                    urllib.request.urlretrieve(
                        url + f'/DASH_360.mp4', self.destination + "Video.mp4")
                except BaseException:
                    print("Can't fetch the video file :(")

    def fetchAudio(self, url):  # Function to get the audio of a video if any
        doc = requests.get(url + '/DASH_audio.mp4')
        if self.destination is not None:
            with open(self.destination + 'Audio.mp3', 'wb') as f:
                f.write(doc.content)
                f.close()
        else:
            with open('' + 'Audio.mp3', 'wb') as f:
                f.write(doc.content)
                f.close()

    # Function to merge the video and audio files creating a complete video
    # file
    def MergeVideo(self):
        try:
            print("Merging Files")
            if self.destination is not None:
                clip = VideoFileClip(self.destination + "Video.mp4")
            else:
                clip = VideoFileClip("Video.mp4")
            try:
                if self.destination is not None:
                    audioclip = AudioFileClip(self.destination + "Audio.mp3")
                else:
                    audioclip = AudioFileClip("Audio.mp3")
                new_audioclip = CompositeAudioClip([audioclip])
                clip.audio = new_audioclip
                try:
                    if self.destination is not None:
                        clip.write_videofile(
                            self.destination + self.output + ".mp4")
                    else:
                        clip.write_videofile(self.output + ".mp4")
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

    # Function to remove the unnecessary files as well as temporary
    # directories and files
    def CleanUp(self, videoOnly=False):
        print('cleaning')
        try:
            if self.destination is not None:
                os.remove(self.destination + "Audio.mp3")
            else:
                os.remove("Audio.mp3")
        except BaseException:
            pass
        if not videoOnly:
            if self.destination is not None:
                os.remove(self.destination + "Video.mp4")
            else:
                os.remove("Video.mp4")
        else:
            try:
                os.rename(
                    self.destination +
                    "Video.mp4",
                    self.destination +
                    self.output +
                    ".mp4")
            except Exception as e:
                print(e)

    def GetMediaType(self):  # Function to return the type of media
        if self.mediaType is not None:
            return self.mediaType
        else:
            return None


class DownloadBySubreddit:
    '''
    This class is used to download posts from a subreddit using
    the reddit api. It can be used to download all types of
    media from a subreddit of choice.

    ...

    |Parameters|

        Subreddit : str
            The subreddit to download the post(s) from.
        NumberOfPosts : int
            The number of posts to download.
        flair : str
            The target flair to download post(s) from
        SortBy : str
            The sort method to use. accepted values are:
            'hot', 'new', 'top'
        quality : int
            The resolution to download the video at. Higher resolution
            will result in a bigger file size.
            accepted values are:
            360, 720, 1080
        output : str
            The name of the output file.
        destination : str
            The destination to save the file to.
            Default is None.

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            flair=None,
            SortBy="hot",
            quality=720,
            output="downloaded",
            destination=None):
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/all",
                    params={
                        'subreddit': Subreddit,
                        'number': NumberOfPosts,
                        'flair': flair,
                        'sort': SortBy})
                Links = json.loads(self.PostLinks.content)
                self.ProcessedLinks = Links
                self.DownloadLinks(Links, quality, output, destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self, links, quality, output, destination):
        print("Downloading Posts...")
        print("Creating ", output, " directory...")
        path = ''
        try:
            if destination is not None:
                path = os.path.join(destination, output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except BaseException:
            pass
        length = len(links)
        i = 1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output +
                        str(i),
                        destination +
                        f'/{output}/')
                else:
                    Download(link, quality, output + str(i), f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)

    def GetPostAuthors(self):
        Authors = []
        for author in self.ProcessedLinks:
            Authors.append(GetPostAuthor(author).Get())
        return Authors


class DownloadImagesBySubreddit:
    '''
    This class is used to download ONLY images from a subreddit using
    the reddit api.

    ...

    |Parameters|

        Subreddit : str
            The subreddit to download the post(s) from.
        NumberOfPosts : int
            The number of posts to download.
        flair : str
            The target flair to download post(s) from
        SortBy : str
            The sort method to use. accepted values are:
            'hot', 'new', 'top'
        quality : int
            The resolution to download the gifs at. Higher resolution
            will result in a bigger file size.
            accepted values are:
            360, 720, 1080
        output : str
            The name of the output file.
        destination : str
            The destination to save the file to.
            Default is None.

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            flair=None,
            SortBy="hot",
            quality=720,
            output="downloaded",
            destination=None):
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/images",
                    params={
                        'subreddit': Subreddit,
                        'number': NumberOfPosts,
                        'flair': flair,
                        'sort': SortBy})
                Links = json.loads(self.PostLinks.content)
                self.ProcessedLinks = Links
                self.DownloadLinks(Links, quality, output, destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self, links, quality, output, destination):
        print("Downloading Posts...")
        print("Creating ", output, " directory...")
        path = ''
        try:
            if destination is not None:
                path = os.path.join(destination, output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except BaseException:
            pass
        length = len(links)
        i = 1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output +
                        str(i),
                        destination +
                        f'/{output}/')
                else:
                    Download(link, quality, output + str(i), f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)

    def GetPostAuthors(self):
        Authors = []
        for author in self.ProcessedLinks:
            Authors.append(GetPostAuthor(author).Get())
        return Authors


class DownloadVideosBySubreddit:
    '''
    This class is used to download ONLY videos from a subreddit using
    the reddit api.

    ...

    |Parameters|

        Subreddit : str
            The subreddit to download the post(s) from.
        NumberOfPosts : int
            The number of posts to download.
        flair : str
            The target flair to download post(s) from
        SortBy : str
            The sort method to use. accepted values are:
            'hot', 'new', 'top'
        quality : int
            The resolution to download the video at. Higher resolution
            will result in a bigger file size.
            accepted values are:
            360, 720, 1080
        output : str
            The name of the output file.
        destination : str
            The destination to save the file to.
            Default is None.

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            flair=None,
            SortBy="hot",
            quality=720,
            output="downloaded",
            destination=None):
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/videos",
                    params={
                        'subreddit': Subreddit,
                        'number': NumberOfPosts,
                        'flair': flair,
                        'sort': SortBy})
                Links = json.loads(self.PostLinks.content)
                self.ProcessedLinks = Links
                self.DownloadLinks(Links, quality, output, destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self, links, quality, output, destination):
        print("Downloading Posts...")
        print("Creating ", output, " directory...")
        path = ''
        try:
            if destination is not None:
                path = os.path.join(destination, output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except BaseException:
            pass
        length = len(links)
        i = 1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output +
                        str(i),
                        destination +
                        f'/{output}/')
                else:
                    Download(link, quality, output + str(i), f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)

    def GetPostAuthors(self):
        Authors = []
        for author in self.ProcessedLinks:
            Authors.append(GetPostAuthor(author).Get())
        return Authors


class DownloadGalleriesBySubreddit:
    '''
    This class is used to download Gallery posts from a subreddit using
    the reddit api.

    ...

    |Parameters|

        Subreddit : str
            The subreddit to download the post(s) from.
        NumberOfPosts : int
            The number of posts to download.
        flair : str
            The target flair to download post(s) from
        SortBy : str
            The sort method to use. accepted values are:
            'hot', 'new', 'top'
        quality : int
            The resolution to download the video (if applicable) at.
            Higher resolution will result in a bigger file size.
            accepted values are:
            360, 720, 1080
        output : str
            The name of the output file.
        destination : str
            The destination to save the file to.
            Default is None.

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            flair=None,
            SortBy="hot",
            quality=720,
            output="downloaded",
            destination=None):
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            print("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/galleries",
                    params={
                        'subreddit': Subreddit,
                        'number': NumberOfPosts,
                        'flair': flair,
                        'sort': SortBy})
                Links = json.loads(self.PostLinks.content)
                self.ProcessedLinks = Links
                self.DownloadLinks(Links, quality, output, destination)
            except Exception as e:
                print("Unable to fetch posts")
                print(e)
        else:
            print("Bad SortBy Option Please either choose 'top' or 'new' or 'hot' ")

    def DownloadLinks(self, links, quality, output, destination):
        print("Downloading Posts...")
        print("Creating ", output, " directory...")
        path = ''
        try:
            if destination is not None:
                path = os.path.join(destination, output)
                os.mkdir(path)
            else:
                os.mkdir(output)
        except BaseException:
            pass
        length = len(links)
        i = 1
        try:
            for link in links:
                print(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output +
                        str(i),
                        destination +
                        f'/{output}/')
                else:
                    Download(link, quality, output + str(i), f'{output}/')
                i += 1
            print("All Posts Downloaded Sucessfully...")
        except Exception as e:
            print("There was an unexpected error while downloading posts...")
            print(e)

    def GetPostAuthors(self):
        Authors = []
        for author in self.ProcessedLinks:
            Authors.append(GetPostAuthor(author).Get())
        return Authors


class GetPostAuthor:
    '''
    This class is used to get the author of a post using the reddit api.

    ...

    |Parameters|

        url : str
            The url of the post to get the author of.

    |Public Functions|

        Get()
            Return Type: str
            Returns the author of the post.
    '''

    def __init__(self, url):
        try:
            self.PostAuthor = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/media/author",
                params={
                    'url': url}).text
        except Exception as e:
            print("Unable to fetch post author")
            print(e)

    def Get(self):
        return self.PostAuthor
