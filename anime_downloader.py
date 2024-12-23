"""
This script downloads anime episodes from a given AnimeWorld URL.

It extracts the anime ID, formats the anime name, retrieves episode IDs and
URLs, and downloads each episode using the richwget tool.

Usage:
    - Run the script with the URL of the anime page as a command-line argument.
    - It will create a directory structure in the 'Downloads' folder based on
      the anime name where each episode will be downloaded.
"""

import os
import argparse
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from rich.live import Live

from helpers.download_utils import save_file_with_progress, run_in_parallel
from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.general_utils import (
    fetch_page, create_download_directory, clear_terminal
)
from helpers.anime_utils import (
    extract_anime_id, extract_anime_name, get_episode_ids,
    generate_episode_urls
)

SESSION = requests.Session()
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) "
        "Gecko/20100101 Firefox/117.0"
    ),
    "Connection": "keep-alive"
}

def process_episode_url(soup):
    """
    Processes episode URL to extract embed URLs from parsed HTML soup.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing parsed HTML.

    Returns:
        list: List of embed URLs extracted from the episode page.

    Raises:
        AttributeError: If the `soup` object is missing or invalid.
        ValueError: If no download links are found on the episode page.
    """
    try:
        item = soup.find(
            'a', {'href': True, 'id': "alternativeDownloadLink"}
        )
        if not item:
            raise ValueError("No download link found on the episode page.")

        return item.get('href')

    except AttributeError as attr_err:
        raise ValueError(
            f"Error accessing tag attributes: {attr_err}"
        ) from attr_err

def get_download_links(episode_urls):
    """
    Retrieves download links from a list of episode URLs using concurrent
    requests.

    Args:
        episodes_urls (list): List of episode URLs.

    Returns:
        list: List of download links for the specified episode URLs.

    Raises:
        requests.RequestException: If there's an issue with fetching an
                                   episode URL.
    """
    download_links = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(fetch_page, episode_url): episode_url
            for episode_url in episode_urls
        }

        for future in as_completed(futures):
            soup = future.result()
            if soup:
                download_link = process_episode_url(soup)
                download_links.append(download_link)

    return download_links

def get_episode_filename(download_link):
    """
    Extract the file name from the provided episode download link.

    Args:
        download_link (str): The download link for the episode.

    Returns:
        str: The extracted file name, or None if the link is None or empty.
    """
    if download_link:
        parsed_url = urlparse(download_link)
        return os.path.basename(parsed_url.path)

    return None

def download_episode(download_link, download_path, task_info):
    """
    Downloads an episode from the specified link and provides real-time
    progress updates.

    Args:
        download_link (str): The URL from which to download the episode.
        download_path (str): The directory path where the episode file will
                             be saved.
        task_info (tuple): A tuple containing progress tracking information:
            - job_progress: The progress bar object.
            - task: The specific task being tracked.
            - overall_task: The overall progress task being updated.

    Raises:
        requests.RequestException: If there is an error with the HTTP request,
                                   such as connectivity issues or invalid URLs.
    """
    try:
        response = SESSION.get(
            download_link, stream=True, headers=HEADERS, timeout=10
        )
        response.raise_for_status()

        file_name = get_episode_filename(download_link)
        final_path = os.path.join(download_path, file_name)
        save_file_with_progress(response, final_path, task_info)

    except requests.RequestException as req_error:
        print(f"HTTP request failed: {req_error}")

def download_anime(anime_name, download_links, download_path):
    """
    Downloads anime episodes from provided video URLs.

    Args:
        anime_name (str): The name of the anime being downloaded.
        download_links (list): List of URLs for downloading each episode.
        download_path (str): Directory path where episodes will be saved.
    """
    job_progress = create_progress_bar()
    progress_table = create_progress_table(anime_name, job_progress)

    with Live(progress_table, refresh_per_second=10):
        run_in_parallel(
            download_episode, download_links, job_progress, download_path
        )

def process_anime_download(url, start_episode=None, end_episode=None):
    """
    Processes the download of an anime from the specified URL.

    Args:
        url (str): The URL of the anime page to process.
        start_episode (int, optional): The starting episode number. Defaults to
                                       None.
        end_episode (int, optional): The ending episode number. Defaults to
                                     None.

    Raises:
        ValueError: If there is an issue with extracting data from 
                    the anime page.
    """
    soup = fetch_page(url)

    try:
        (host_page, anime_id) = extract_anime_id(url)
        anime_name = extract_anime_name(soup)
        download_path = create_download_directory(anime_name)

        episode_ids = get_episode_ids(
            soup,
            start_episode=start_episode,
            end_episode=end_episode
        )
        episode_urls = generate_episode_urls(host_page, anime_id, episode_ids)

        download_links = get_download_links(episode_urls)
        download_anime(anime_name, download_links, download_path)

    except ValueError as error_value:
        print(f"Value error: {error_value}")

def setup_parser():
    """
    Set up the argument parser for the anime download script.

    Returns:
        argparse.ArgumentParser: The configured argument parser instance.
    """
    parser = argparse.ArgumentParser(
        description="Download anime episodes from a given URL."
    )
    parser.add_argument('url', help="The URL of the Anime series to download.")
    parser.add_argument(
        '--start', type=int, default=None, help="The starting episode number."
    )
    parser.add_argument(
        '--end', type=int, default=None, help="The ending episode number."
    )
    return parser

def main():
    """
    Main function to download anime episodes from a given AnimeWorld URL.
    """
    clear_terminal()
    parser = setup_parser()
    args = parser.parse_args()
    process_anime_download(
        args.url,
        start_episode=args.start,
        end_episode=args.end
    )

if __name__ == '__main__':
    main()
