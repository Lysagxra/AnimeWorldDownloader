"""
This module provides functions for extracting information from anime web pages
and constructing episode URLs for downloading. It utilizes BeautifulSoup for 
parsing HTML content and includes error handling for common extraction issues.
"""

from urllib.parse import urlparse

def extract_anime_id(url):
    """
    Extracts the host page and anime ID from a given URL.

    Args:
        url (str): The URL from which anime ID is to be extracted.

    Returns:
        tuple: A tuple containing:
            - anime_id (str): The extracted anime ID.
            - host_page (str): The extracted host page.

    Raises:
        ValueError: If the URL format is invalid.
    """
    try:
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip('/').split('/')

        if len(path_segments) < 3:
            raise ValueError("URL does not contain enough path segments.")

        play_tag = path_segments[0]
        anime_id = path_segments[1]
        host_page = f"https://{parsed_url.netloc}/{play_tag}/"
#        domain = parsed_url.netloc.split('.')[-1]
#        host_page = f"https://www.animeworld.{domain}/play/"
#        anime_id = url.split('/')[-2]
        return host_page, anime_id

    except IndexError as indx_err:
        raise ValueError("Invalid URL format.") from indx_err

def extract_anime_name(soup):
    """
    Extracts the anime name from the provided BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML of
                              the anime page.

    Returns:
        str: The name of the anime.

    Raises:
        ValueError: If the <h1> tag with class "title" is not found in the HTML.
        AttributeError: If there is an issue accessing the text of the <h1> tag.
    """
    try:
        title_tag = soup.find('h1', {'class': "title", 'data-jtitle': True})

        if title_tag is None:
            raise ValueError("Anime title tag not found.")

        return title_tag['data-jtitle']

    except AttributeError as attr_err:
        return AttributeError(f"Error extracting anime name: {attr_err}")

def get_episode_ids(soup):
    """
    Extracts episode IDs and the maximum episode count from parsed HTML soup.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed
                              HTML.

    Returns:
        tuple: A tuple containing:
            - episode_ids (list): List of episode IDs extracted.

    Raises:
        AttributeError: If the `soup` object is missing or invalid.
        ValueError: If no episode items are found or if the episode count
                    cannot be converted to an integer or is missing.
    """
    def get_active_server_container(soup):
        return soup.find('div', {'class': "server active"})

    try:
        server_container = get_active_server_container(soup)
        episode_items = server_container.find_all('li', {'class': "episode"})

        if not episode_items:
            raise ValueError("No episode items found.")

        return [item.find('a').get('data-id') for item in episode_items]

    except AttributeError as attr_err:
        raise AttributeError(
            f"Error accessing tag attributes: {attr_err}"
        ) from attr_err

    except ValueError as val_err:
        raise ValueError("Error processing episode counts or IDs.") from val_err

def generate_episodes_urls(host_page, anime_id, episode_ids):
    """
    Generates a list of episode URLs for a given anime.

    Args:
        host_page (str): The base URL of the host page.
        anime_id (str): The unique identifier for the anime.
        episode_ids (list of str): A list of unique identifiers for each
                                   episode.

    Returns:
        list of str: A list of formatted URLs for each episode.
    """
    return [
        f"{host_page}{anime_id}/{episode_id}"
        for episode_id in episode_ids
    ]
