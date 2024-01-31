import logging
import time
from urllib import robotparser
from urllib.parse import urlsplit

import requests

from .backend import FileBackend
from .exceptions import BackendException

logger = logging.getLogger(__name__)


class WebBackend(FileBackend):
    backend = "web"
    retry_timeout = 30

    _ignore_robots = False

    def __init__(self, config: dict):
        self._user_agent = requests.utils.default_headers()["User-Agent"]
        self._parser = robotparser.RobotFileParser()

    def _get_robots_txt(self, url: str):
        logger.debug("Fetching robots.txt from \"%s\".", url)
        resp = requests.head(url, timeout=60)
        if resp.status_code == requests.codes.NOT_FOUND:
            # Robots.txt doesn't exist for this site
            self._ignore_robots = True
            return
        elif resp.status_code != requests.codes.OK:
            # Received a different error code, assume we aren't allowed to crawl
            raise BackendException(f"got {resp.status_code} while trying to fetch robots.txt")
        self._parser.set_url(url)
        self._parser.read()

    def _can_fetch(self, url: str) -> bool:
        return self._ignore_robots or self._parser.can_fetch(self._user_agent, url)

    def get_file(self, uri: str) -> bytes:
        logger.info("Retrieving file \"%s\" using 'web' backend.", uri)

        # Get robots.txt
        try:
            path = urlsplit(uri)
            scheme = f"{path.scheme}://" if path.scheme else ""
            path = f"{scheme}{path.netloc}/robots.txt"
            self._get_robots_txt(path)
        except Exception as e:
            raise BackendException(f"failed to parse robots.txt, must assume we are not allowed to look at the URL: {str(e)}")

        # Figure out of robots.txt allows us to crawl the URL
        logger.debug("Determining if \"%s\" can crawl the path.", self._user_agent)
        if not self._can_fetch(uri):
            raise BackendException(f"robots.txt has disallowed crawling of \"{uri}\"")

        while True:  # Loop until the lambda times out, max of 15 mins
            try:
                resp = requests.get(uri, timeout=60)
            except requests.exceptions.Timeout:
                logger.warning("GET request timed out. Retrying in %i seconds.", self.retry_timeout)
                time.sleep(self.retry_timeout)
                continue
            except requests.exceptions.RequestException as e:
                raise BackendException(f"GET request failed: {str(e)}")

            if resp.status_code == requests.codes.OK:
                return resp.content
            elif "Retry-After" in resp.headers:
                retry = resp.headers["Retry-After"]
                logger.warning("Received a %i response with a 'Retry-After' of %i seconds.", resp.status_code, retry)
                time.sleep(retry)
                continue
            elif resp.status_code == requests.codes.TOO_MANY:
                logger.warning("Got a 'too many requests' error for \"%s\". Retrying in %i seconds.", uri, self.retry_timeout)
                time.sleep(self.retry_timeout)
                continue
            else:
                raise BackendException(f"GET request failed with a {resp.status_code} code: '{resp.content}'")
