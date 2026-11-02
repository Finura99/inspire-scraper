import httpx

def fetch_page(url):
    try:
        #send an HTTP GET request and store the server response
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    except httpx.RequestError as error:
        print(f"Request failed for{url}: {error}")
        return None
        #no normal HTTP response was completed, raises for timeouts, dns failures, connection refused

    except httpx.HTTPStatusError as error:
        print(
            f"Bad response: {url}: "
            f"{error.response.status_code}"
            )
        return None
        #HTTP response came back, but status was an error


