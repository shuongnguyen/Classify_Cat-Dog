import tornado.httpclient
from tornado.httputil import url_concat
import asyncio
import urllib
import nest_asyncio

class ApiConnector:
    def __init__(self):
        self._headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": "8a1621535dmshc2b40537ec58d87p195d12jsnb94e212c6a53",
            "X-RapidAPI-Host": "bing-image-search1.p.rapidapi.com"
        }
        self._params = {"api-version": "3.0"}


    async def send_image_data(self, image_data):
        # Disable SSL certificate verification
        tornado.httpclient.AsyncHTTPClient.configure(None, defaults={"validate_cert": False})
        http_client = tornado.httpclient.AsyncHTTPClient()
            
        url = tornado.httputil.url_concat(
            "https://bing-image-search1.p.rapidapi.com/images/search",
            self._params
        )
        try:
             response = await http_client.fetch(url, method="POST", headers=self._headers, body=image_data)
        except urllib.error.HTTPError as e:
            print(e.response.body)
        else:
            print(response.body)
            
nest_asyncio.apply()
handler = ApiConnector()
asyncio.run(handler.send_image_data("Cats"))



