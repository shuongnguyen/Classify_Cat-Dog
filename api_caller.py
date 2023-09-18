import tornado.httpclient
import tornado.ioloop
import json
import logging

class ApiCaller:
    def __init__(self):
        self.http_client = tornado.httpclient.AsyncHTTPClient()
        self.logger = logging.getLogger("api_calls")

    async def make_api_call(self, url):
        try:
            response = await self.http_client.fetch(url)
            self.logger.info(f"API Call to {url} successful")
            return response.body, response.code
        except tornado.httpclient.HTTPError as e:
            self.logger.error(f"HTTP Error ({e.code}) while calling {url}")
            return None, e.code
        except Exception as e:
            self.logger.error(f"Error while calling {url}: {str(e)}")
            return None, 500

if __name__ == "__main__":
    api_caller = ApiCaller()
    ioloop = tornado.ioloop.IOLoop.current()
    
    num_requests = 1000
    base_url = "https://catfact.ninja/fact"  # Replace with your API base URL
    
    for i in range(1, num_requests + 1):
        url = f"{base_url}{i}"
        response, status_code = ioloop.run_sync(lambda: api_caller.make_api_call(url))
        
        if status_code == 200:
            # Process the response as needed
            response_data = json.loads(response)
            print(f"Response from {url}: {response_data}")
        else:
            print(f"Failed to retrieve data from {url} (HTTP {status_code})")

    ioloop.close()
