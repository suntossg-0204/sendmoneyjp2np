import requests


class APIClient:

    def get_json(self, url, headers=None):

        if headers is None:
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response.json()