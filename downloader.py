import re
import requests
from bs4 import BeautifulSoup
from youtubesearchpython import VideosSearch
from pytube import YouTube
import os

from pytube import YouTube
from moviepy.editor import VideoFileClip

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError, TIT2, TPE2, TALB, TYER, APIC

from urllib.request import urlopen


def is_url_valid(url):
    if re.match(r'^https:\/\/open\.spotify\.com\/track\/[a-zA-Z0-9]{22}$', url):
        return True
    else:
        return False


def get_search_query(soup):
    artist = soup.find('meta', attrs={'name': 'music:musician_description'})['content']
    title = soup.find('meta', attrs={'name': 'twitter:title'})['content']
    return artist + ' - ' + title


def get_youtube_link(query):
    videos_search = VideosSearch(query, limit = 1)
    results = videos_search.result()

    if results['result']:
        return results['result'][0]['link']
    else:
        return None


def download_track(youtube_link, title):
    yt = YouTube(youtube_link)
    stream = yt.streams.get_highest_resolution()
    stream.download(filename=f'{title}.mp4')

    video = VideoFileClip(f'{title}.mp4')
    audio = video.audio
    audio.write_audiofile(f'{title}.mp3', logger=None)
    video.close()

    os.remove(f'{title}.mp4')
    print(f'{title}.mp3 has been successfully downloaded')


def add_metadata(soup):
    title = soup.find('meta', attrs={'name': 'twitter:title'})['content']
    artist = soup.find('meta', attrs={'name': 'music:musician_description'})['content']

    album_url = soup.find('meta', attrs={'name': 'music:album'})['content']
    album_response = requests.get(album_url)
    album_soup = BeautifulSoup(album_response.text, 'html.parser')
    album = album_soup.find('meta', attrs={'name': 'twitter:title'})['content']

    release_date = soup.find('meta', attrs={'name': 'music:release_date'})['content']
    image_url = soup.find('meta', attrs={'name': 'twitter:image'})['content']

    try:
        mp3_file = MP3(f'{title}.mp3')
    except ID3NoHeaderError:
        mp3_file = mutagen.File(f'{title}.mp3', easy=True)
        mp3_file.add_tags()

    mp3_file['TIT2'] = TIT2(encoding=3, text=title)
    mp3_file['TPE2'] = TPE2(encoding=3, text=artist)
    mp3_file['TALB'] = TALB(encoding=3, text=album)
    mp3_file['TYER'] = TYER(encoding=3, text=release_date)

    album_art = urlopen(image_url)

    mp3_file['APIC'] = APIC(
        encoding=3,
        mime='image/jpeg',
        type=3, desc=u'Cover',
        data=album_art.read()
    )

    album_art.close()
    mp3_file.save(v2_version=3)


track_url = input('Enter spotify track url: ')

if is_url_valid(track_url):
    response = requests.get(track_url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        query = get_search_query(soup)
        youtube_link = get_youtube_link(query)
        title = soup.find('meta', attrs={'name': 'twitter:title'})['content']

        if youtube_link is not None:
            download_track(youtube_link, title)
            add_metadata(soup)
        else:
            print('Sorry, unable to find track')

    else:
        print('Error loading url')

else:
    print('Invalid spotify track url')
