<div align="center">
    
<img src= "https://raw.githubusercontent.com/JackhammerYT/RedDownloader/main/.github/logo.png" height=250px width=250px>
    
</div>
<br><br>

<div align = "center">


<img src="https://img.shields.io/badge/License-GPLv3-blueviolet">


</div>

<div align = "center">
    

![GitHub forks](https://img.shields.io/github/forks/JackhammerYT/RedDownloader?color=red&logo=Github&style=flat-square) ![GitHub watchers](https://img.shields.io/github/watchers/JackhammerYT/RedDownloader?logo=Github) ![GitHub Repo stars](https://img.shields.io/github/stars/JackhammerYT/RedDownloader?logo=Github) ![GitHub followers](https://img.shields.io/github/followers/JackhammerYT?logo=Github) 

    
</div>

<div align = "center">
    
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/JackhammerYT/RedDownloader?logo=Github)  ![GitHub closed issues](https://img.shields.io/github/issues-closed/JackhammerYT/RedDownloader?color=255%2C255%2C0&logo=Github)![GitHub repo size](https://img.shields.io/github/repo-size/JackhammerYT/RedDownloader?logo=Github)![GitHub release (latest by date)](https://img.shields.io/github/v/release/JackhammerYT/RedDownloader?display_name=tag&logo=Github)
    
</div>

<div align = "center">
    
![PyPI - Downloads](https://img.shields.io/pypi/dm/RedDownloader?label=Pypi%20Downloads&logo=Pypi) ![PyPI](https://img.shields.io/pypi/v/RedDownloader?logo=pypi)
    
</div>

<div align="center">
    
<img src="https://img.shields.io/badge/dynamic/json?style=flat&logo=reddit&logoColor=white&color=orange&label=Requests%20Handled&query=requests&url=https%3A%2F%2Fjackhammer.pythonanywhere.com%2FRedDownloader%2FRequests%2F">
    
</div>

<h1> Introduction </h1>

A very easy to use Reddit Media Downloader. The library can also be used to download pictures and even picture galleries all just with a reddit post link. You can access Reddit API methods without having your own bot with classes such as ```DownloadBySubreddit``` more on that below.

<b>NOTE: </b> this package only downloads media from posts with images/video directly uploaded to reddit and not from sources like imgur or youtube / vimeo which are posted to Reddit.

<h1> Installation </h1>
To Install the package:

```
pip install RedDownloader
```


<h1> Usage </h1>

```python
from RedDownloader import RedDownloader
```

RedDownloader is auth less you don't need to have a praw bot to use this package.

After importing, Downloading is just a single line of code

```python
RedDownloader.Download(url)
```

This will automatically download media from the passed url it would automatically detect if it's a picture/video/gallery with default options. to pass in an output filename just pass in the output parameter as:

```python
RedDownloader.Download(url , output="MyAwesomeRedditMedia")
```

In case if a post is of type gallery it will make a folder in the ```destination``` path with the output parameter passed. That folder would contain all your pictures. In Case if a folder with that name already exists files would be downloaded in that folder.

To set a custom path for downloaded file use ```destination``` as an argument like

```python
RedDownloader.Download(url , output="MyAwesomeRedditMedia" , destination="D:/Pictures/")
```

default file name is "downloaded".
you don't have to pass in extensions to the output parameter.

default download location for file is current working directory.

Another argument is the ```quality``` argument which defines the resolution to download if the filetype is a video the avaliable options to choose from are 144, 240, 360, 480, 720, 1080 please note that higher resolution would result in bigger file size. If a video file in specified resolution is not found it will try for a lower resolution.
Default: 1080p

An example:

```python
RedDownloader.Download(url , output="MyAwesomeRedditMedia" , quality = 1080)
```
You at times might need to know the media type of the file being downloaded for that you can use the ```GetMediaType()``` method

```python
file = RedDownloader.Download(url)
print(file.GetMediaType())
```

for images it returns a ```i```  for videos it returns a ```v``` and for a gallery post it returns a ```g``` and a ```gif``` for a gif.

The package has been tested for videos with no sound as well.

Galleries were first supported in RedDownloader 2.2.0 any older version used to download a gallery post would return a ```Post Not Recoganized``` error

<h1>Using Reddit API Methods</h1>

To download some number of media from a specific subreddit you can use the ```DownloadBySubreddit```:

```python
RedDownloader.DownloadBySubreddit(subreddit , NumberOfPosts , flair = None , SortBy = "hot" , quality = 720 , output = "downloaded" , destination=None)
```

subreddit: the subreddit you want to download the posts from.
NumberOfPosts: the number of posts to download from the subreddit
flair: to download posts from a specfic flair from the subreddit of your choice by defaut flair is set to ```None``` and downloads posts from any flair
SortBy: it sorts the posts from the subreddit you can set it to either ```hot```, ```new``` or ```top``` by default it is set to ```hot```
output: it is the folder name under which all the posts get downloaded
destination: path where the download folder and all the posts are downloaded by default it downloads the posts in current working directory.

essentialy you can just do:
```python
RedDownloader.DownloadBySubreddit("memes" , 15)
```

this would download the hottest 15 posts from r/memes in a folder called downloaded in your current working directory

alternativley you have:

```python
RedDownloader.DownloadImagesBySubreddit("python" , 5)
```

This would only download Images from a subreddit it is derived from ```DownloadBySubreddit``` hence shares the same argumets as listed above

```python
RedDownloader.DownloadVideosBySubreddit("python" , 5)
```

This would only download Videos from a subreddit it is derived from ```DownloadBySubreddit``` hence shares the same argumets as listed above

```python
RedDownloader.DownloadGalleriesBySubreddit("python" , 5)
```

This would only download Gallery type posts from a subreddit it is derived from ```DownloadBySubreddit``` hence shares the same argumets as listed above

<h1>New Features in RedDownloader 3.1.1:</h1>

You can now use the ```GetPostAuthor``` class to get a post author/poster from a given url the syntax followed is

```python
author = RedDownloader.GetPostAuthor(url).Get()
print(author)
```

Classes such as ```DownloadBySubreddit``` , ```DownloadImagesBySubreddit``` , ```DownloadVideosBySubreddit``` and ```DownloadGalleriesBySubreddit``` now have a method ```GetPostAuthors``` which returns a list of authors of the posts you just downloaded.

For regular ```Download``` class you can now use the ```GetPostAuthor``` class to get a post author.

Example:

```python
posts = RedDownloader.DownloadBySubreddit("python" , 5)
authors = posts.GetPostAuthors()
print(authors)
```


<h1>New Features in RedDownloader 3.2.0:</h1>

<h2> The GetUser Class </h2>

You can now use the ```GetUser``` class to get information about a user with the following syntax

```Python
User = RedDownloader.GetUser("Jackhammer_YOUTUBE")
print(User.Get())
```

This returns a dictionary with a couple of information:
```
Key : ReturnType
    usage

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
```

for suspended accounts only ```AccountName``` and ```Suspended``` as keys are avaliable


<h2> Cache FIles </h2>

A new argument called ```cachefile``` can now be used with following classes ```DownloadBySubreddit``` , ```DownloadImagesBySubreddit``` , ```DownloadVideosBySubreddit``` and ```DownloadGalleriesBySubreddit```.

```cachefile``` is useful when you don't want to download an already download file with RedDownloader. Everytime you download posts with ```cachefile``` all the urls of downloaded posts are stored in the file, RedDownloader checks the url of post to be downloaded next time making sure duplicates are avoided. By default it is set to ```None``` meaning it won't be checking for duplicate downloads

To use ```cachefile``` your virtual environment or work folder should already have a file, RedDownloader won't manually create cachefiles!!!

If you have an empty file called ```Downloaded.txt``` to use cachefile you can simply do

```python
RedDownloader.DownloadBySubreddit('memes' , 5 , cachefile='Downloaded.txt')
```

This is especially beneficial if you would like to store different types of posts in different cache files. 


<h1>New Features in RedDownloader 3.2.1:</h1>

<h2> The GetPostTitles && GetPostTitle Class </h2>

You can now use the ```GetPostTitle``` class to get a post title from a given url the syntax followed is
 
```python
title = RedDownloader.GetPostTitle(url).Get()
print(title)
```

For classes like ```DownloadBySubreddit``` , ```DownloadImagesBySubreddit``` , ```DownloadVideosBySubreddit``` and ```DownloadGalleriesBySubreddit``` there is a method ```GetPostTitles``` which returns a list of titles of the posts you just downloaded.

And for regular ```Download``` class you can now use the ```GetPostTitle``` method to get a post title.

<h2> The GetPostAudio Class </h2>

You can now use the ```GetPostAudio``` class to get a post audio from a given url the syntax followed is
     
```python           
audio = RedDownloader.GetPostAudio(url)
```

To change the file download destination you can set the ```destination``` argument to the path you want to download the file to. By default it downloads the file in the current working directory. To change to output file name you can set the ```output``` argument to the name of the file you want to download the audio to. By default it downloads the file with the name ```Audio.mp3```.


## Star History

<div align = "center">

[![Star History Chart](https://api.star-history.com/svg?repos=JackhammerYT/RedDownloader&type=Date)](https://star-history.com/#JackhammerYT/RedDownloader&Date)

</div>
