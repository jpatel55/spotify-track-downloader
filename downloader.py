import re
import requests
from pytubefix import YouTube
from pytubefix.cli import on_progress
from bs4 import BeautifulSoup
from mutagen.mp4 import MP4, MP4Cover
from youtubesearchpython import VideosSearch


def is_url_valid(url):
    """Validate the Spotify track URL."""
    return re.match(r"^https:\/\/open\.spotify\.com\/track\/[a-zA-Z0-9]{22}$", url) is not None


def get_search_query(soup):
    """Extract artist and title from the Spotify track page to form a YouTube search query."""
    artist = soup.find("meta", attrs={"name": "music:musician_description"})["content"]
    title = soup.find("meta", attrs={"name": "twitter:title"})["content"]
    return f"{artist} - {title}"


def get_youtube_link(query):
    """Search YouTube for the given query and return the first video link."""
    videos_search = VideosSearch(query, limit=1)
    results = videos_search.result()

    if results["result"]:
        return results["result"][0]["link"]
    return None


def download_track(youtube_link, soup):
    """Download the audio from the YouTube video."""
    yt = YouTube(youtube_link, on_progress_callback=on_progress)
    ys = yt.streams.get_audio_only()
    new_title = soup.find("meta", attrs={"name": "twitter:title"})["content"]
    ys.download(filename=f"{new_title}.m4a")
    print(f"{new_title}.m4a has been successfully downloaded.")


def add_metadata(soup):
    """Add metadata to the downloaded audio file."""
    title = soup.find("meta", attrs={"name": "twitter:title"})["content"]
    artist = soup.find("meta", attrs={"name": "music:musician_description"})["content"]
    album_url = soup.find("meta", attrs={"name": "music:album"})["content"]
    album_art_url = soup.find("meta", attrs={"name": "twitter:image"})["content"]
    release_date = soup.find("meta", attrs={"name": "music:release_date"})["content"]

    album_response = requests.get(album_url)
    album_soup = BeautifulSoup(album_response.text, "html.parser")
    album = album_soup.find("meta", attrs={"name": "twitter:title"})["content"]

    album_art_response = requests.get(album_art_url)

    audio = MP4(f"{title}.m4a")
    audio["\xa9nam"] = title
    audio["\xa9ART"] = artist
    audio["\xa9alb"] = album
    audio["\xa9day"] = release_date
    audio["covr"] = [MP4Cover(album_art_response.content, imageformat=MP4Cover.FORMAT_JPEG)]

    audio.save()
    print(f"Metadata added to {title}.m4a.")


def main():
    """Main function to handle the workflow."""
    track_url = input("Enter Spotify track URL: ")

    if is_url_valid(track_url):
        response = requests.get(track_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            query = get_search_query(soup)
            youtube_link = get_youtube_link(query)

            if youtube_link:
                download_track(youtube_link, soup)
                add_metadata(soup)
            else:
                print("Sorry, unable to find the track on YouTube.")
        else:
            print("Error loading the Spotify URL.")
    else:
        print("Invalid Spotify track URL.")


if __name__ == "__main__":
    main()
