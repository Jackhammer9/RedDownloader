'''
This is the main source file for RedDownloader Version 3.2.4 with it's primary
usage being downloading Reddit Posts i.e Image Posts , Videos , Gifs , Gallery
Posts.
'''

# Internal Imports
import urllib.request
import json
import os
import shutil

# External Imports | Required Packages
from moviepy.editor import *
import requests


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
                'gif' for gifs

            GetPostAuthor()
                Return Type : str
                Returns the author of the post.

            GetPostTitle()
                Return Type : str
                Returns the title of the post.

    '''

    def __init__(
            self,
            url,
            quality=1080,
            output="downloaded",
            destination=None):
        self.output = output
        self.MainURL = url
        self.destination = destination
        qualityTypes = [144, 240, 360, 480, 720, 1080]
        if quality not in qualityTypes:  # if quality is not in the list
            raise Exception("Error: Unkown Quality Type" +  # Throw an error
                            f" {quality} choose either 144, 240, 360, 480, 720 or 1080")
        else:
            # Getting the absolute reddit post link
            self.postLink = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/media/downloader",
                params={
                    'url': url}).text
            try:
                self.PostAuthor = GetPostAuthor(url)
            except Exception as e:
                pass

            if 'v.redd.it' in self.postLink:  # if the post is a video
                print("Detected Post Type: Video")
                self.mediaType = "v"
                self.InitiateVideo(quality, self.postLink)
            elif 'i.redd.it' in self.postLink:  # if the post is an image
                if not self.postLink.endswith('.gif') and not self.postLink.endswith('.GIF') and not self.postLink.endswith('.gifv') and not self.postLink.endswith('.GIFV'):
                    print("Detected Post Type: Image")
                    self.mediaType = "i"
                    imageData = requests.get(self.postLink).content
                    file = open(f'{self.output}' + '.jpeg', 'wb')
                    file.write(imageData)
                    file.close()
                    print("Sucessfully Downloaded Image: " + f"{self.output}")
                    if self.destination is not None:
                        shutil.move(f"{self.output}.jpeg", self.destination)
                else:
                    print("Detected Post Type: Gif")
                    self.mediaType = "gif"
                    GifData = requests.get(self.postLink).content
                    file = open(f'{self.output}' + '.gif', 'wb')
                    file.write(GifData)
                    file.close()
                    print("Sucessfully Downloaded Gif: " + f"{self.output}")
                    if self.destination is not None:
                        shutil.move(f"{self.output}.gif", self.destination)
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

        qualityTypes = [144, 240, 360, 480, 720, 1080]
        listIndex = qualityTypes.index(quality)
        wasDownloadSuccessful = False
        for quality in range(listIndex, -1, -1):
            print(f'Trying resolution: {qualityTypes[quality]}p')
            try:
                if self.destination is not None:
                    urllib.request.urlretrieve(
                        url + f'/DASH_{qualityTypes[quality]}.mp4',
                        self.destination + "Video.mp4")
                    wasDownloadSuccessful = True
                    print("Video File Downloaded Successfully")
                else:
                    urllib.request.urlretrieve(
                        url + f'/DASH_{qualityTypes[quality]}.mp4', "Video.mp4")
                    wasDownloadSuccessful = True
                    print("Video File Downloaded Successfully")
                break
            except BaseException:
                print(
                    f'Video file not avaliable at {qualityTypes[quality]}p going to next resolution')
                continue
        if not wasDownloadSuccessful:
            raise Exception("Can't fetch the video file")

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

    def GetPostAuthor(self):
        return GetPostAuthor(self.MainURL)

    def GetPostTitle(self):
        return GetPostTitle(self.MainURL)


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
        cachefile : str
            The location of the cache file. use cache files to keep
            a record of posts being downloaded so the duplicate files
            won't get downloaded

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            SortBy="hot",
            quality=1080,
            output="downloaded",
            destination=None,
            cachefile=None,
            flair=None):
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

                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, 'w') as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, 'r') as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    for link in Links:
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            Links.remove(link)

                    with open(cachefile, 'w') as f:
                        json.dump(self.cachedLinks, f)
                        f.close()

                self.ProcessedLinks = Links
                self.DownloadLinks(
                    self.ProcessedLinks, quality, output, destination)
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

    def GetPostTitles(self):
        Titles = []
        for title in self.ProcessedLinks:
            Titles.append(GetPostTitle(title).Get())
        return Titles


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
        cachefile : str
            The location of the cache file. use cache files to keep
            a record of posts being downloaded so the duplicate files
            won't get downloaded

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            SortBy="hot",
            quality=1080,
            output="downloaded",
            destination=None,
            flair=None,
            cachefile=None):
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

                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, 'w') as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, 'r') as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    for link in Links:
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            Links.remove(link)

                    with open(cachefile, 'w') as f:
                        json.dump(self.cachedLinks, f)
                        f.close()

                self.ProcessedLinks = Links
                self.DownloadLinks(
                    self.ProcessedLinks, quality, output, destination)
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

    def GetPostTitles(self):
        Titles = []
        for title in self.ProcessedLinks:
            Titles.append(GetPostTitle(title).Get())
        return Titles


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
            The sort method to use.
            accepted values are:
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
        cachefile : str
            The location of the cache file. use cache files to keep
            a record of posts being downloaded so the duplicate files
            won't get downloaded

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            SortBy="hot",
            quality=1080,
            output="downloaded",
            destination=None,
            flair=None,
            cachefile=None):
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
                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, 'w') as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, 'r') as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    for link in Links:
                        print(link, Links, len(Links))
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            Links.remove(link)

                    with open(cachefile, 'w') as f:
                        json.dump(self.cachedLinks, f)
                        f.close()
                self.ProcessedLinks = Links
                self.DownloadLinks(
                    self.ProcessedLinks, quality, output, destination)
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

    def GetPostTitles(self):
        Titles = []
        for title in self.ProcessedLinks:
            Titles.append(GetPostTitle(title).Get())
        return Titles


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
        cachefile : str
            The location of the cache file. use cache files to keep
            a record of posts being downloaded so the duplicate files
            won't get downloaded

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    '''

    def __init__(
            self,
            Subreddit,
            NumberOfPosts,
            SortBy="hot",
            quality=1080,
            output="downloaded",
            destination=None,
            flair=None,
            cachefile=None):
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
                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, 'w') as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, 'r') as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    for link in Links:
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            Links.remove(link)

                    with open(cachefile, 'w') as f:
                        json.dump(self.cachedLinks, f)
                        f.close()
                self.ProcessedLinks = Links
                self.DownloadLinks(
                    self.ProcessedLinks, quality, output, destination)
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

    def GetPostTitles(self):
        Titles = []
        for title in self.ProcessedLinks:
            Titles.append(GetPostTitle(title).Get())
        return Titles


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


class GetUser:
    '''
    This class is used to get the user information of a user using the reddit api.

    ...

    |Parameters|
        username : str
            The username of the user to get the information of.

    |Public Functions|
        Get()
            Return Type: dict
                Keys:
                    'AccountName' : str
                        the username of the user
                    'ID' : str
                        the id of the user
                    'CreationDate' : float
                        the date the user was created (in unix time)
                    'CommentKarma' : int
                        the amount of comment karma the user has
                    'LinkKarma' : int
                        the amount of link karma the user has
                    'PremiumUser' : bool
                        whether the user has a premium account or not
                    'Moderator' : bool
                        whether the user is a moderator or not
                    'Verified' : bool
                        whether the user is verified or not


            Returns the user information of the user.
    '''

    def __init__(self, username):
        try:
            self.UserInfo = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/user/info",
                params={
                    'username': username}).text
            self.info = json.loads(self.UserInfo)
        except Exception as e:
            print("Unable to fetch user info")
            print(e)

    def Get(self):
        return self.info


class GetPostTitle:
    '''
    This class is used to get the title of a post using the reddit api.

    ...

    |Parameters|

        url : str
            The url of the post to get the title of.

    |Public Functions|

        Get()
            Return Type: str
            Returns the title of the post.
    '''

    def __init__(self, url):
        try:
            self.PostTitle = requests.get(
                "http://jackhammer.pythonanywhere.com/reddit/media/title",
                params={
                    'url': url}).text
        except Exception as e:
            print("Unable to fetch post title")
            print(e)

    def Get(self):
        return self.PostTitle


class GetPostAudio:
    '''
    This class is used to get the audio of a post using the reddit api.

    ...

    |Parameters|

        url : str
            The url of the post to get the audio of.

        destination : str
            The destination to save the audio to.

        output : str
            The name of the file to be saved as audio.

    '''

    def __init__(self, url, destination=None, output=None):
        self.url = url
        self.postLink = requests.get(
            "https://jackhammer.pythonanywhere.com/reddit/media/downloader",
            params={
                'url': self.url}).text
        self.destination = destination

        doc = requests.get(self.postLink + '/DASH_audio.mp4')

        if doc.status_code == 200:
            print('Downloading Audio...')
            if self.destination is not None:
                if not output:
                    with open(os.path.join(self.destination, 'Audio.mp3'), 'wb') as f:
                        f.write(doc.content)
                        f.close()
                else:
                    with open(os.path.join(self.destination, f'{output}.mp3'), 'wb') as f:
                        f.write(doc.content)
                        f.close()
            else:
                if not output:
                    with open('Audio.mp3', 'wb') as f:
                        f.write(doc.content)
                        f.close()
                else:
                    with open(output + '.mp3', 'wb') as f:
                        f.write(doc.content)
                        f.close()
            print('Audio Downloaded Sucessfully...')

        else:
            raise Exception("Unable to download audio, audio not found...")