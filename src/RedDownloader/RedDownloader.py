"""
This is the main source file for RedDownloader Version 4.1.2 with it's primary
usage being downloading Reddit Posts i.e Image Posts , Videos , Gifs , Gallery
Posts with additional support for Youtube links and Imgur Links.
"""

# Internal Imports | Pre Installed Packages
import urllib.request
import json
import os
import shutil

# External Imports | Required Packages
from moviepy.editor import *
import requests
from pytube import YouTube

# Other Script Refference
from Utils import Logger


class Download:
    """This is the base class for RedDownloader all downloads are done
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
         verbose: bool
             Controls wether the logger should print progress to
             console or not
             Set It To True (Default) to print the progress
             Set It To False to not print the progress

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

    """

    def __init__(
        self, url, quality=1080, output="downloaded", destination=None, verbose=True
    ):
        self.output = output
        self.MainURL = url
        self.destination = destination
        qualityTypes = [144, 240, 360, 480, 720, 1080]
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        if quality not in qualityTypes:  # if quality is not in the list
            raise Exception(
                "Error: Unkown Quality Type"
                + f" {quality} choose either 144, 240, 360, 480, 720 or 1080"  # Throw an error
            )
        else:
            # Getting the absolute reddit post link
            self.postLink = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/media/downloader",
                params={"url": url},
            ).text
            try:
                self.PostAuthor = GetPostAuthor(url)
            except Exception as e:
                self.Logger.LogInfo(e)

            if "v.redd.it" in self.postLink:  # if the post is a video
                self.Logger.LogInfo("Detected Post Type: Video")
                self.mediaType = "v"
                self.InitiateVideo(quality, self.postLink)
            elif "i.redd.it" in self.postLink:  # if the post is an image
                if (
                    not self.postLink.endswith(".gif")
                    and not self.postLink.endswith(".GIF")
                    and not self.postLink.endswith(".gifv")
                    and not self.postLink.endswith(".GIFV")
                ):
                    self.Logger.LogInfo("Detected Post Type: Image")
                    self.mediaType = "i"
                    imageData = requests.get(self.postLink).content
                    file = open(f"{self.output}" + ".jpeg", "wb")
                    file.write(imageData)
                    file.close()
                    self.Logger.LogInfo(
                        "Sucessfully Downloaded Image: " + f"{self.output}"
                    )
                    if self.destination is not None:
                        shutil.move(f"{self.output}.jpeg", self.destination)
                else:
                    self.Logger.LogInfo("Detected Post Type: Gif")
                    self.mediaType = "gif"
                    GifData = requests.get(self.postLink).content
                    file = open(f"{self.output}" + ".gif", "wb")
                    file.write(GifData)
                    file.close()
                    self.Logger.LogInfo(
                        "Sucessfully Downloaded Gif: " + f"{self.output}"
                    )
                    if self.destination is not None:
                        shutil.move(f"{self.output}.gif", self.destination)
            elif "/gallery/" in self.postLink:  # if the post is a gallery
                self.Logger.LogInfo("Detected Post Type: Gallery")
                self.mediaType = "g"
                if self.destination == None:
                    self.directory = self.output
                else:
                    self.directory = os.path.join(self.destination, self.output)
                try:
                    # making a directory for the gallery
                    os.mkdir(self.directory)
                except BaseException:
                    pass
                self.Logger.LogInfo("Fetching images from gallery")
                # Fetching urls of all media in the post
                self.GalleryPosts = requests.get(
                    "https://jackhammer.pythonanywhere.com/reddit/media/gallery",
                    params={"url": self.postLink},
                )
                posts = json.loads(self.GalleryPosts.content)
                self.GetGallery(posts)

            elif "youtu.be" in self.postLink or "youtube.com" in self.postLink:
                self.Logger.LogInfo("Type Detected: Youtube Video")
                self.mediaType = "yt"

                try:
                    self.Logger.LogInfo("Downloading Youtube Video")
                    yt = YouTube(self.postLink)
                    stream = yt.streams.filter(
                        progressive=True, file_extension="mp4"
                    ).order_by("resolution")[-1]
                    if self.destination == None:
                        stream.download(".", filename=self.output + ".mp4")
                    else:
                        stream.download(self.destination, filename=self.output + ".mp4")

                    self.Logger.LogInfo("Downloaded Sucessfully...")

                except Exception as e:
                    self.Logger.LogInfo("Connection Error")
                    self.Logger.LogInfo(e)

            elif "i.imgur.com" in self.postLink:
                self.Logger.LogInfo("Detected Post Type: Imgur Image")
                self.mediaType = "imgur"
                imageData = requests.get(self.postLink).content
                file = open(f"{self.output}" + ".jpeg", "wb")
                file.write(imageData)
                file.close()
                self.Logger.LogInfo("Sucessfully Downloaded Image: " + f"{self.output}")
                if self.destination is not None:
                    shutil.move(f"{self.output}.jpeg", self.destination)

            elif "imgur.com" in self.postLink:
                self.Logger.LogInfo("Detected Post Type: Imgur Album")
                self.Logger.LogInfo(
                    "Support for imgur album posts has not yet been added"
                )

            else:
                self.Logger.LogInfo("Error: Could Not Recognize Post Type")

    def GetGallery(
        self, posts
    ):  # Function to download and merge all images in a directory

        TotalPosts = len(posts)
        self.Logger.LogInfo("Total images to be downloaded: " + str(TotalPosts))
        for i in range(TotalPosts):
            self.Logger.LogInfo(f"Downloading image {i+1} / {TotalPosts}")
            ImageData = requests.get(posts[i]).content
            with open(
                os.path.join(self.directory, self.output + f"{i+1}.jpeg"), "wb"
            ) as image:
                image.write(ImageData)
                image.close()
        self.Logger.LogInfo("Image Gallery Successfully Downloaded!")

    def InitiateVideo(self, quality, url):
        try:
            self.Logger.LogInfo("Fetching Video...")
            self.fetchVideo(quality, url)
            self.Logger.LogInfo("Fetching Audio...")
            self.fetchAudio(url)
        except BaseException as e:
            self.Logger.LogInfo(
                "Sorry there was an error while fetching video/audio files"
            )
            self.Logger.LogInfo("\nTraceback:\n", e)
        else:
            self.MergeVideo()

    # Getting the Audioless Video only file of a specified resolution from
    # Reddit
    def fetchVideo(self, quality, url):

        qualityTypes = [144, 240, 360, 480, 720, 1080]
        listIndex = qualityTypes.index(quality)
        wasDownloadSuccessful = False
        for quality in range(listIndex, -1, -1):
            self.Logger.LogInfo(f"Trying resolution: {qualityTypes[quality]}p")
            try:
                if self.destination is not None:
                    urllib.request.urlretrieve(
                        url + f"/DASH_{qualityTypes[quality]}.mp4",
                        self.destination + "Video.mp4",
                    )
                    wasDownloadSuccessful = True
                    self.Logger.LogInfo("Video File Downloaded Successfully")
                else:
                    urllib.request.urlretrieve(
                        url + f"/DASH_{qualityTypes[quality]}.mp4", "Video.mp4"
                    )
                    wasDownloadSuccessful = True
                    self.Logger.LogInfo("Video File Downloaded Successfully")
                break
            except BaseException as e:
                self.Logger.LogInfo(e)
                self.Logger.LogInfo(
                    f"Video file not avaliable at {qualityTypes[quality]}p going to next resolution"
                )
                continue
        if not wasDownloadSuccessful:
            raise Exception("Can't fetch the video file")

    def fetchAudio(self, url):  # Function to get the audio of a video if any
        doc = requests.get(url + "/DASH_audio.mp4")
        if self.destination is not None:
            with open(self.destination + "Audio.mp3", "wb") as f:
                f.write(doc.content)
                f.close()
        else:
            with open("" + "Audio.mp3", "wb") as f:
                f.write(doc.content)
                f.close()

    # Function to merge the video and audio files creating a complete video
    # file
    def MergeVideo(self):
        try:
            self.Logger.LogInfo("Merging Files")
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
                            self.destination + self.output + ".mp4",
                            verbose=self.verbose,
                            logger=None,
                        )
                    else:
                        clip.write_videofile(
                            self.output + ".mp4", verbose=self.verbose, logger=None
                        )
                except Exception as e:
                    pass
                self.Logger.LogInfo("Merging Done!")
                self.CleanUp()
                self.Logger.LogInfo(self.output + " Successfully Downloaded!")
                clip.close()
            except Exception as e:
                clip.close()
                self.Logger.LogInfo("Video has no sound")
                self.CleanUp(True)
                self.Logger.LogInfo(self.output + " Successfully Downloaded!")
        except Exception as e:
            self.Logger.LogInfo("Merge Failed!")
            self.Logger.LogInfo(e)

    # Function to remove the unnecessary files as well as temporary
    # directories and files
    def CleanUp(self, videoOnly=False):

        self.Logger.LogInfo("cleaning")
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
                if self.output.lower() != "video":
                    os.remove("Video.mp4")
        else:
            try:
                if self.destination is not None:
                    os.rename(
                        self.destination + "Video.mp4",
                        self.destination + self.output + ".mp4",
                    )
                else:
                    os.rename("Video.mp4", self.output + ".mp4")
            except Exception as e:
                self.Logger.LogInfo(e)

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
    """
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
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    """

    def __init__(
        self,
        Subreddit,
        NumberOfPosts,
        SortBy="hot",
        quality=1080,
        output="downloaded",
        destination=None,
        cachefile=None,
        flair=None,
        verbose=True,
    ):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            self.Logger.LogInfo("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/all",
                    params={
                        "subreddit": Subreddit,
                        "number": NumberOfPosts,
                        "flair": flair,
                        "sort": SortBy,
                    },
                )
                Links = json.loads(self.PostLinks.content)

                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, "w") as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, "r") as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    ToBeRemoved = []
                    for link in Links:

                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            ToBeRemoved.append(link)

                    for link in ToBeRemoved:
                        Links.remove(link)

                    with open(cachefile, "w") as f:
                        json.dump(self.cachedLinks, f)
                        f.close()

                self.ProcessedLinks = Links
                self.DownloadLinks(self.ProcessedLinks, quality, output, destination)
            except Exception as e:
                self.Logger.LogInfo("Unable to fetch posts")
                self.Logger.LogInfo(e)
        else:
            self.Logger.LogInfo(
                "Bad SortBy Option Please either choose 'top' or 'new' or 'hot' "
            )

    def DownloadLinks(self, links, quality, output, destination):
        self.Logger.LogInfo("Downloading Posts...")
        self.Logger.LogInfo("Creating " + str(output) + " directory...")
        path = ""
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
                self.Logger.LogInfo(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        destination + f"/{output}/",
                        verbose=self.verbose,
                    )
                else:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        f"{output}/",
                        verbose=self.verbose,
                    )
                i += 1
            self.Logger.LogInfo("All Posts Downloaded Sucessfully...")
        except Exception as e:
            self.Logger.LogInfo(
                "There was an unexpected error while downloading posts..."
            )
            self.Logger.LogInfo(e)

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
    """
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
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    """

    def __init__(
        self,
        Subreddit,
        NumberOfPosts,
        SortBy="hot",
        quality=1080,
        output="downloaded",
        destination=None,
        flair=None,
        cachefile=None,
        verbose=True,
    ):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            self.Logger.LogInfo("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/images",
                    params={
                        "subreddit": Subreddit,
                        "number": NumberOfPosts,
                        "flair": flair,
                        "sort": SortBy,
                    },
                )
                Links = json.loads(self.PostLinks.content)

                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, "w") as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, "r") as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    ToBeRemoved = []
                    for link in Links:
                        self.Logger.LogInfo(link)
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            ToBeRemoved.append(link)

                    for link in ToBeRemoved:
                        Links.remove(link)

                    with open(cachefile, "w") as f:
                        json.dump(self.cachedLinks, f)
                        f.close()

                self.ProcessedLinks = Links
                self.DownloadLinks(self.ProcessedLinks, quality, output, destination)
            except Exception as e:
                self.Logger.LogInfo("Unable to fetch posts")
                self.Logger.LogInfo(e)
        else:
            self.Logger.LogInfo(
                "Bad SortBy Option Please either choose 'top' or 'new' or 'hot' "
            )

    def DownloadLinks(self, links, quality, output, destination):
        self.Logger.LogInfo("Downloading Posts...")
        self.Logger.LogInfo("Creating " + str(output) + " directory...")
        path = ""
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
                self.Logger.LogInfo(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        destination + f"/{output}/",
                        verbose=self.verbose,
                    )
                else:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        f"{output}/",
                        verbose=self.verbose,
                    )
                i += 1
            self.Logger.LogInfo("All Posts Downloaded Sucessfully...")
        except Exception as e:
            self.Logger.LogInfo(
                "There was an unexpected error while downloading posts..."
            )
            self.Logger.LogInfo(e)

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
    """
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
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    """

    def __init__(
        self,
        Subreddit,
        NumberOfPosts,
        SortBy="hot",
        quality=1080,
        output="downloaded",
        destination=None,
        flair=None,
        cachefile=None,
        verbose=True,
    ):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            self.Logger.LogInfo("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/videos",
                    params={
                        "subreddit": Subreddit,
                        "number": NumberOfPosts,
                        "flair": flair,
                        "sort": SortBy,
                    },
                )
                Links = json.loads(self.PostLinks.content)

                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, "w") as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, "r") as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    ToBeRemoved = []
                    for link in Links:
                        self.Logger.LogInfo(link)
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            ToBeRemoved.append(link)

                    for link in ToBeRemoved:
                        Links.remove(link)

                    with open(cachefile, "w") as f:
                        json.dump(self.cachedLinks, f)
                        f.close()

                self.ProcessedLinks = Links
                self.DownloadLinks(self.ProcessedLinks, quality, output, destination)
            except Exception as e:
                self.Logger.LogInfo("Unable to fetch posts")
                self.Logger.LogInfo(e)
        else:
            self.Logger.LogInfo(
                "Bad SortBy Option Please either choose 'top' or 'new' or 'hot' "
            )

    def DownloadLinks(self, links, quality, output, destination):
        self.Logger.LogInfo("Downloading Posts...")
        self.Logger.LogInfo("Creating " + str(output) + " directory...")
        path = ""
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
                self.Logger.LogInfo(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        destination + f"/{output}/",
                        verbose=self.verbose,
                    )
                else:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        f"{output}/",
                        verbose=self.verbose,
                    )
                i += 1
            self.Logger.LogInfo("All Posts Downloaded Sucessfully...")
        except Exception as e:
            self.Logger.LogInfo(
                "There was an unexpected error while downloading posts..."
            )
            self.Logger.LogInfo(e)

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
    """
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
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

    |Public Functions|

        GetPostAuthors()
            Return Type: List
            Returns a list of the authors of the posts.

        GetPostTitles()
            Return Type: List
            Returns a list of the titles of the posts.

    """

    def __init__(
        self,
        Subreddit,
        NumberOfPosts,
        SortBy="hot",
        quality=1080,
        output="downloaded",
        destination=None,
        flair=None,
        cachefile=None,
        verbose=True,
    ):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        if SortBy == "hot" or SortBy == "new" or SortBy == "top":
            self.Logger.LogInfo("Fetching Posts...")
            try:
                self.PostLinks = requests.get(
                    "https://jackhammer.pythonanywhere.com//reddit/subreddit/galleries",
                    params={
                        "subreddit": Subreddit,
                        "number": NumberOfPosts,
                        "flair": flair,
                        "sort": SortBy,
                    },
                )
                Links = json.loads(self.PostLinks.content)

                if cachefile is not None:
                    if os.stat(cachefile).st_size == 0:
                        with open(cachefile, "w") as f:
                            f.write(json.dumps([]))
                            f.close()

                    with open(cachefile, "r") as f:
                        self.cachedLinks = json.load(f)
                        f.close()

                    ToBeRemoved = []
                    for link in Links:
                        self.Logger.LogInfo(link)
                        if link not in self.cachedLinks:
                            self.cachedLinks.append(link)
                        else:
                            ToBeRemoved.append(link)

                    for link in ToBeRemoved:
                        Links.remove(link)

                    with open(cachefile, "w") as f:
                        json.dump(self.cachedLinks, f)
                        f.close()

                self.ProcessedLinks = Links
                self.DownloadLinks(self.ProcessedLinks, quality, output, destination)
            except Exception as e:
                self.Logger.LogInfo("Unable to fetch posts")
                self.Logger.LogInfo(e)
        else:
            self.Logger.LogInfo(
                "Bad SortBy Option Please either choose 'top' or 'new' or 'hot' "
            )

    def DownloadLinks(self, links, quality, output, destination):
        self.Logger.LogInfo("Downloading Posts...")
        self.Logger.LogInfo("Creating " + str(output) + " directory...")
        path = ""
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
                self.Logger.LogInfo(f"Downloading Post {i} of {length}")
                if destination is not None:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        destination + f"/{output}/",
                        verbose=self.verbose,
                    )
                else:
                    Download(
                        link,
                        quality,
                        output + str(i),
                        f"{output}/",
                        verbose=self.verbose,
                    )
                i += 1
            self.Logger.LogInfo("All Posts Downloaded Sucessfully...")
        except Exception as e:
            self.Logger.LogInfo(
                "There was an unexpected error while downloading posts..."
            )
            self.Logger.LogInfo(e)

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
    """
    This class is used to get the author of a post using the reddit api.

    ...

    |Parameters|

        url : str
            The url of the post to get the author of.
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

    |Public Functions|

        Get()
            Return Type: str
            Returns the author of the post.
    """

    def __init__(self, url, verbose=True):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        try:
            self.PostAuthor = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/media/author",
                params={"url": url},
            ).text
        except Exception as e:
            self.Logger.LogInfo("Unable to fetch post author")
            self.Logger.LogInfo(e)

    def Get(self):
        return self.PostAuthor


class GetUser:
    """
    This class is used to get the user information of a user using the reddit api.

    ...

    |Parameters|
        username : str
            The username of the user to get the information of.
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

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
    """

    def __init__(self, username, verbose=True):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        try:
            self.UserInfo = requests.get(
                "https://jackhammer.pythonanywhere.com/reddit/user/info",
                params={"username": username},
            ).text
            self.info = json.loads(self.UserInfo)
        except Exception as e:
            self.Logger.LogInfo("Unable to fetch user info")
            self.Logger.LogInfo(e)

    def Get(self):
        return self.info


class GetPostTitle:
    """
    This class is used to get the title of a post using the reddit api.

    ...

    |Parameters|

        url : str
            The url of the post to get the title of.
        verbose: bool
            Controls wether the logger should print progress to
            console or not
            Set It To True (Default) to print the progress
            Set It To False to not print the progress

    |Public Functions|

        Get()
            Return Type: str
            Returns the title of the post.
    """

    def __init__(self, url, verbose=True):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        try:
            self.PostTitle = requests.get(
                "http://jackhammer.pythonanywhere.com/reddit/media/title",
                params={"url": url},
            ).text
        except Exception as e:
            self.Logger.LogInfo("Unable to fetch post title")
            self.Logger.LogInfo(e)

    def Get(self):
        return self.PostTitle


class GetPostAudio:
    """
    This class is used to get the audio of a post using the reddit api.

    ...

    |Parameters|

        url : str
            The url of the post to get the audio of.

        destination : str
            The destination to save the audio to.

        output : str
            The name of the file to be saved as audio.

            verbose: bool
                Controls wether the logger should print progress to
                console or not
                Set It To True (Default) to print the progress
                Set It To False to not print the progress

    """

    def __init__(self, url, destination=None, output=None, verbose=True):
        self.verbose = verbose
        self.Logger = Logger(self.verbose)
        self.url = url
        self.postLink = requests.get(
            "https://jackhammer.pythonanywhere.com/reddit/media/downloader",
            params={"url": self.url},
        ).text
        self.destination = destination

        doc = requests.get(self.postLink + "/DASH_audio.mp4")

        if doc.status_code == 200:
            self.Logger.LogInfo("Downloading Audio...")
            if self.destination is not None:
                if not output:
                    with open(os.path.join(self.destination, "Audio.mp3"), "wb") as f:
                        f.write(doc.content)
                        f.close()
                else:
                    with open(
                        os.path.join(self.destination, f"{output}.mp3"), "wb"
                    ) as f:
                        f.write(doc.content)
                        f.close()
            else:
                if not output:
                    with open("Audio.mp3", "wb") as f:
                        f.write(doc.content)
                        f.close()
                else:
                    with open(output + ".mp3", "wb") as f:
                        f.write(doc.content)
                        f.close()
            self.Logger.LogInfo("Audio Downloaded Sucessfully...")

        else:
            raise Exception("Unable to download audio, audio not found...")


"""
Below are some test lines to make sure all RedDownloader Features are working well. Uncomment them and run them if you want to test
out specific files or are facing issues with RedDownloader.
"""
## Test For Image Downloading
# Download("https://www.reddit.com/r/memes/comments/xfhe9j/my_brain_haha_fuck_you_losah/", output="Image")

## Test For Video Downloading
# Download("https://www.reddit.com/r/Unity2D/comments/xfadpb/trying_to_make_new_over_the_top_spells_for_our/", output="VideoTest")

## Test For Gallery Posts
# Download("https://www.reddit.com/r/pics/comments/xevl7p/a_magnetic_knife_strip_felt_too_small_in_the/", output="Gallery")

## Test for Gif Files
# Download("https://www.reddit.com/r/dankmemes/comments/xfmqqn/thats_what_facebook_said/", output="Gif")

## Test For Using Reddit API Features
# DownloadBySubreddit("memes", 5, output="Subreddit API")

## Test For Youtube Links
# Download("https://www.reddit.com/r/videos/comments/xi89wf/this_guy_made_a_1hz_cpu_in_minecraft_to_run/", output="Youtube Video")

## Test For Imgur Posts
# Download("https://www.reddit.com/r/pics/comments/xbzjbv/my_grandparents_100_yearolddresser_prerestoration/",output="Imgur Image")
