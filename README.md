# Spotify Track Downloader

A Python script to download audio (M4A format) from YouTube for a given Spotify track URL, complete with metadata.

## Features
- Validate Spotify track URLs.
- Search YouTube for the corresponding track.
- Download audio-only YouTube streams.
- Add track metadata (title, artist, album, release date, cover art).

## Prerequisites
- Python 3.x
- Required libraries: `pytubefix`, `beautifulsoup4`, `mutagen`, `youtube-search-python`, `requests`

## Usage
- Install the required dependencies using the following command:  
  `pip install -r requirements.txt`
- Run the script:  
  `python downloader.py`
