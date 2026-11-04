import logging
import time

from urllib.parse import urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx


LOGGER = logging.getLogger(__name__)

USER_AGENT = "InspireCareersResearch/0.1"


class Fetcher:

    def __init__(self, delay_seconds=0.8, transport=None):

        self.delay_seconds = delay_seconds

        self.client = httpx.Client(
            timeout=10.0,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
            transport=transport,
        )

        self._robots_rules = {}
        self._last_request = {}

    def close(self):
        self.client.close()

    def _get(self, url):

        host = urlsplit(url).netloc
        last = self._last_request.get(host)

        if last is not None and self.delay_seconds:

            remaining = self.delay_seconds - (
                time.monotonic() - last
            )

            if remaining > 0:
                time.sleep(remaining)

        try:
            return self.client.get(url)

        finally:
            self._last_request[host] = time.monotonic()

    def _allowed_by_robots(self, url):

        parts = urlsplit(url)

        if parts.scheme not in ("http", "https") or not parts.hostname:
            return False

        origin = (parts.scheme, parts.netloc)

        if origin not in self._robots_rules:

            robots_url = urlunsplit(
                (
                    parts.scheme,
                    parts.netloc,
                    "/robots.txt",
                    "",
                    "",
                )
            )

            try:
                response = self._get(robots_url)

                if response.status_code == 404:
                    self._robots_rules[origin] = None

                else:
                    response.raise_for_status()

                    rules = RobotFileParser()
                    rules.parse(response.text.splitlines())

                    self._robots_rules[origin] = rules

            except (httpx.RequestError, httpx.HTTPStatusError) as exc:

                LOGGER.warning(
                    "Cannot check robots.txt for %s: %s",
                    parts.netloc,
                    exc,
                )

                return False

        rules = self._robots_rules[origin]

        return (
            True
            if rules is None
            else rules.can_fetch(USER_AGENT, url)
        )

    def fetch_page(self, url):

        if not self._allowed_by_robots(url):

            LOGGER.info(
                "Skipped (robots.txt or invalid URL): %s",
                url,
            )

            return None

        try:
            response = self._get(url)

            response.raise_for_status()

            if len(response.content) > 3_000_000:

                LOGGER.warning(
                    "Page too large; skipped: %s",
                    url,
                )

                return None

            return response.text

        except (httpx.RequestError, httpx.HTTPStatusError) as exc:

            LOGGER.warning(
                "Request failed for %s: %s",
                url,
                exc,
            )

            return None