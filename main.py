"""
This module provides functionality to read URLs from a specified file,
validate them, and download the associated content. It manages the entire
download process by leveraging asynchronous operations, allowing for
efficient handling of multiple URLs.

Usage:
    To run the module, execute the script directly. It will process URLs
    listed in 'URLs.txt' and log the session activities in 'session_log.txt'.
"""

from helpers.file_utils import read_file, write_file
from helpers.general_utils import clear_terminal
from anime_downloader import process_anime_download

FILE = 'URLs.txt'

def process_urls(urls):
    """
    Validates and downloads items for a list of URLs.

    Args:
        urls (list): A list of URLs to process.
    """
    for url in urls:
        process_anime_download(url)

def main():
    """
    Main function to execute the script.

    Clears the session log, reads URLs from a file, processes them,
    and clears the URLs file at the end.
    """
    clear_terminal()
    urls = read_file(FILE)
    process_urls(urls)
    write_file(FILE)

if __name__ == '__main__':
    main()
