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
import sys
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from rich.live import Live

from helpers.download_utils import save_file_with_progress, run_in_parallel
from helpers.progress_utils import create_progress_bar, create_progress_table
from helpers.anime_utils import (
    extract_anime_id, extract_anime_name, get_episode_ids,
    generate_episodes_urls
)

SCRIPT_NAME = os.path.basename(__file__)
DOWNLOAD_FOLDER = "Downloads"
TIMEOUT = 10

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

def get_download_links(episodes_urls):
    """
    Retrieves embed URLs from a list of episode URLs.

    Args:
        episodes_urls (list): List of episode URLs.

    Returns:
        list: List of the download links for the specified episode URLs.

    Raises:
        requests.RequestException: If there's an issue with fetching an
                                   episode URL.
        RuntimeError: If no valid embed URLs are found.
    """
    embed_urls = []

    for episode_url in episodes_urls:
        soup = fetch_page(episode_url)
        url = process_episode_url(soup)
        embed_urls.append(url)

    if not embed_urls:
        raise RuntimeError("No valid embed URLs were found.")

    return embed_urls

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
        response = requests.get(download_link, stream=True, timeout=TIMEOUT)
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

def create_download_directory(anime_name):
    """
    Creates a directory for downloads if it doesn't exist.

    Args:
        anime_name (str): The name of the anime used to create the download 
                          directory.

    Returns:
        str: The path to the created download directory.

    Raises:
        OSError: If there is an error creating the directory.
    """
    download_path = os.path.join(DOWNLOAD_FOLDER, anime_name)

    try:
        os.makedirs(download_path, exist_ok=True)
        return download_path

    except OSError as os_err:
        print(f"Error creating directory: {os_err}")
        sys.exit(1)

def fetch_page(url):
    """
    Fetches the anime page and returns its BeautifulSoup object.

    Args:
        url (str): The URL of the anime page.

    Returns:
        BeautifulSoup: The BeautifulSoup object containing the HTML.

    Raises:
        requests.RequestException: If there is an error with the HTTP request.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    except requests.RequestException as req_err:
        print(f"Error fetching the anime page: {req_err}")
        sys.exit(1)

def process_anime_download(url):
    """
    Processes the download of an anime from the specified URL.

    Args:
        url (str): The URL of the anime page to process.

    Raises:
        ValueError: If there is an issue with extracting data from 
                    the anime page.
    """
    soup = fetch_page(url)

    try:
        (host_page, anime_id) = extract_anime_id(url)
        anime_name = extract_anime_name(soup)

        download_path = create_download_directory(anime_name)

        episode_ids = get_episode_ids(soup)
        episodes_urls = generate_episodes_urls(host_page, anime_id, episode_ids)

        download_links = get_download_links(episodes_urls)
        download_anime(anime_name, download_links, download_path)

    except ValueError as error_value:
        print(f"Value error: {error_value}")

def clear_terminal():
    """
    Clears the terminal screen based on the operating system.
    """
    commands = {
        'nt': 'cls',      # Windows
        'posix': 'clear'  # macOS and Linux
    }

    command = commands.get(os.name)
    if command:
        os.system(command)

def main():
    """
    Main function to download anime episodes from a given AnimeWorld URL.
    """
    if len(sys.argv) != 2:
        print(f"Usage: python3 {SCRIPT_NAME} <anime_url>")
        sys.exit(1)

    clear_terminal()
    url = sys.argv[1]
    process_anime_download(url)

if __name__ == '__main__':
    main()
