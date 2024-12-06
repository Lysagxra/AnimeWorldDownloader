# AnimeWorld Downloader

> A Python-based tool for downloading anime series from AnimeWorld, featuring progress tracking for each episode. It efficiently extracts video URLs and manages downloads.

![Screenshot](https://github.com/Lysagxra/AnimeWorldDownloader/blob/48ebac6e425e3ca7bf89929b40a79d6f362f02c0/misc/Screenshot.png)

## Features

- Downloads multiple episodes concurrently.
- Supports batch downloading via a list of URLs.
- Supports downloading a specified range of episodes.
- Tracks download progress with a progress bar.
- Automatically creates a directory structure for organized storage.

## Directory Structure

```
project-root/
├── helpers/
│ ├── anime_utils.py     # Utilities for extracting information from AnimeWorld.
│ ├── download_utils.py  # Utilities for managing the download process
│ ├── file_utils.py      # Utilities for managing file operations
│ ├── general_utils.py   # Miscellaneous utility functions
│ └── progress_utils.py  # Tools for progress tracking and reporting
├── anime_downloader.py  # Module for downloading anime episodes
├── main.py              # Main script to run the downloader
└── URLs.txt             # Text file containing anime URLs
```

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `BeautifulSoup` (bs4) - for HTML parsing
- `rich` - for progress display in terminal

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Lysagxra/AnimeWorldDownloader.git
```

2. Navigate to the project directory:

```bash
cd AnimeWorldDownloader
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Single Anime Download

To download a single anime, you can use the `anime_downloader.py` script.

### Usage

Run the script followed by the anime URL you want to download:

```bash
python3 anime_downloader.py <anime_url> [--start <start_episode>] [--end <end_episode>]
```

- `<anime_url>`: The URL of the anime series.
- `--start <start_episode>`: The starting episode number (optional).
- `--end <end_episode>`: The ending episode number (optional).

### Examples

To download all episodes:
```bash
python3 anime_downloader.py https://www.animeworld.so/play/made-in-abyss.pIzmnA/TNBNCF
```

To download a specific range of episodes (e.g., episodes 5 to 10):
```bash
python3 anime_downloader.py https://www.animeworld.so/play/made-in-abyss.pIzmnA/TNBNCF --start 5 --end 10
```

To download episodes starting from a specific episode:
```bash
python3 anime_downloader.py https://www.animeworld.so/play/made-in-abyss.pIzmnA/TNBNCF --start 5
```
In this case, the script will download all episodes starting from the `--start` episode to the last episode.

## Batch Download

### Usage

1. Create a `URLs.txt` file in the project root and list the anime URLs you want to download.

2. Run the main script via the command line:

```bash
python3 main.py
```

The downloaded files will be saved in the `Downloads` directory.
