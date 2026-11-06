import httpx

from src.fetcher import Fetcher


def test_robots_disallow_blocks_fetching():
    calls = []

    def handler(request):
        calls.append(request.url.path)

        if request.url.path == "/robots.txt":
            return httpx.Response(
                200,
                text="User-agent: *\nDisallow: /private",
            )

        return httpx.Response(200, text="Secret")

    fetcher = Fetcher(
        delay_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    try:
        assert fetcher.fetch_page(
            "https://example.com/private"
        ) is None

        assert calls == ["/robots.txt"]

        assert fetcher.fetch_page(
            "https://example.com/public"
        ) == "Secret"

        assert calls == ["/robots.txt", "/public"]

    finally:
        fetcher.close()


def test_robots_404_allows_access_and_network_error_returns_none():

    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)

        raise httpx.ConnectError(
            "Simulated outage",
            request=request,
        )

    fetcher = Fetcher(
        delay_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    try:
        assert fetcher.fetch_page(
            "https://example.com/article"
        ) is None

    finally:
        fetcher.close()


def test_robot_policy_error_fails_closed():

    def handler(request):
        return httpx.Response(503)

    fetcher = Fetcher(
        delay_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    try:
        assert fetcher.fetch_page(
            "https://example.com/article"
        ) is None

    finally:
        fetcher.close()


def test_http_status_failure_returns_none():

    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404)

        return httpx.Response(403)

    fetcher = Fetcher(
        delay_seconds=0,
        transport=httpx.MockTransport(handler),
    )

    try:
        assert fetcher.fetch_page(
            "https://example.com/article"
        ) is None

    finally:
        fetcher.close()