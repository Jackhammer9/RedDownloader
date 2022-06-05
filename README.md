A very easy to use library to download videos from reddit with sound without installing external installation of ffmpeg. The library can also be used to download pictures and even picture galleries all just with a reddit post link. With RedDownloader 3 you can access Reddit API methods without having your own bot with classes such as ```DownloadBySubreddit``` more on that below.
note that this package does only download media from posts with images/video directly uploaded to reddit and not from sources like imgur or youtube / vimeo.

Usage:
To Install the package:

```
pip install RedDownloader
```

To Import package just do:

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

for images it returns a ```i```  for videos it returns a ```v``` and for a gallery post it returns a ```g```

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

Classes such as ```DownloadBySubreddit``` , ```DownloadImagesBySubreddit``` , ```DownloadVideosBySubreddit``` and ```DownloadGalleriesBySubreddit``` now have a method ```GetPostAuthors``` which returns a list of authors of the posts you just downloaded. Example:

```python
posts = RedDownloader.DownloadBySubreddit("python" , 5)
authors = posts.GetPostAuthors()
print(authors)
```