import logging
import tornado.httpclient
import json
import asyncio
import tornado.web
import time

class Logger:
    def __init__(self, filename=None, filemode='a', level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        handler = (
            logging.FileHandler(filename, mode=filemode) if filename
            else logging.StreamHandler()
        )

        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, level, message):
        if level == 'debug':
            self.logger.debug(message)
        elif level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        elif level == 'critical':
            self.logger.critical(message)
        else:
            raise ValueError("Invalid log level")

    def debug(self, message):
        self.log('debug', message)

    def info(self, message):
        self.log('info', message)

    def warning(self, message):
        self.log('warning', message)

    def error(self, message):
        self.log('error', message)

    def critical(self, message):
        self.log('critical', message)

class Connector:
    def __init__(self, api_url, api_headers, logger):
        self.api_url = api_url
        self.api_headers = api_headers
        self.logger = logger

    async def make_get_request(self, endpoint):
        try:
            response = await self.fetch_url(self.api_url + endpoint, self.api_headers)
            return response.body.decode('utf-8')
        except Exception as e:
            self.logger.error(f"GET Request Error: {str(e)}")
            return {'error': str(e)}

    async def make_post_request(self, endpoint, request_body):
        try:
            request_body_json = json.dumps(request_body)
            response = await self.fetch_url(self.api_url + endpoint, self.api_headers, method="POST", body=request_body_json)
            return response.body.decode('utf-8')
        except Exception as e:
            self.logger.error(f"POST Request Error: {str(e)}")
            return {'error': str(e)}

    async def fetch_url(self, url, headers, method="GET", body=None):
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(url, method=method, headers=headers, body=body, validate_cert=False)
        return await http_client.fetch(request)

async def make_post_requests(connector, num_requests):
    payload = "source_language=en&target_language=fr&text=What%20is%20your%20name%3F"

    results = []

    # Use a semaphore to control concurrency
    semaphore = asyncio.Semaphore(10)  # Adjust the concurrency limit as needed

    async def do_post_request(i):
        async with semaphore:
            try:
                response = await connector.make_post_request("/translate", payload)
                results.append((i, response))
            except Exception as e:
                results.append((i, {'error': str(e)}))

    # Create and gather tasks
    tasks = [do_post_request(i) for i in range(num_requests)]
    await asyncio.gather(*tasks)

    return results



async def main():
    logger = Logger(filename='mylog.log', level=logging.DEBUG)
    api_config = {
        'url': "https://text-translator2.p.rapidapi.com",
        'headers': {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": "0b4f84a007msh88a4bc1868d6a98p1fdf0ejsnbb2330d895e4",
            "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
        }
    }

    connector = Connector(api_url=api_config['url'], api_headers=api_config['headers'], logger=logger)
    

    #GET request
    get_response = await connector.make_get_request("/getLanguages")
    logger.info(f"GET Response: {get_response}")
    
    # payload = "source_language=en&target_language=fr&text=What%20is%20your%20name%3F"

    #POST request with a request body
    
    # post_response = await connector.make_post_request("/translate", payload)
    # logger.info(f"POST Response: {post_response}")
    
    num_requests = 500
    post_responses = await make_post_requests(connector, num_requests)
    for i, response in enumerate(post_responses):
        logger.info(f"POST Response {response[0] + 1}: {response[1]}")
    


if __name__ == "__main__":
    asyncio.run(main())