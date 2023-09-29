import logging
import tornado.httpclient
import json
import asyncio
import aiohttp
import tornado.web
import uuid 


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

    # async def make_get_request(self, endpoint):
    #     try:
    #         response = await self.fetch_url(self.api_url + endpoint, self.api_headers)
    #         return response #.body.decode('utf-8')
    #     except Exception as e:
    #         self.logger.error(f"GET Request Error: {str(e)}")
    #         return {'error': str(e)}

    # async def make_post_request(self, endpoint, request_body):
    #     try:
    #         request_body_json = json.dumps(request_body)
    #         response = await self.fetch_url(self.api_url + endpoint, self.api_headers, method="POST", body=request_body_json)
    #         return response #.body.decode('utf-8')
    #     except Exception as e:
    #         self.logger.error(f"POST Request Error: {str(e)}")
    #         return {'error': str(e)}
    
    async def make_get_request(self, endpoint, max_retries=3):
        for _ in range(max_retries):
            try:
                response = await self.fetch_url(self.api_url + endpoint, self.api_headers)
                status_code = response.code
                response_body = response.body.decode('utf-8')
                self.logger.info(f"GET Response: {status_code}")
                #self.logger.info(f"Status Code: {status_code}")
                return status_code
            except tornado.httpclient.HTTPError as e:
                if e.code == 599:  # 599 indicates a timeout
                    self.logger.warning(f"GET Request Timeout: Retrying...")
                    await asyncio.sleep(1)  # Wait for a moment before retrying
                else:
                    self.logger.error(f"GET Request Error: {str(e)}")
                    return {'error': str(e)}
        return None  # If all retries fail

    async def make_post_request(self, endpoint, request_body, max_retries=3):
        for _ in range(max_retries):
            try:
                request_body_json = json.dumps(request_body)
                response = await self.fetch_url(self.api_url + endpoint, self.api_headers, method="POST", body=request_body_json)
                status_code = response.code
                response_body = response.body.decode('utf-8')
                request_id = str(uuid.uuid4())
                self.logger.info(f"Request ID: {request_id}")
                self.logger.info(f"POST Response: {status_code}")
                #self.logger.info(f"Status Code: {status_code}")
                return request_id, status_code
            except tornado.httpclient.HTTPError as e:
                if e.code == 599:  # 599 indicates a timeout
                    self.logger.warning(f"POST Request Timeout: Retrying...")
                    await asyncio.sleep(1)  # Wait for a moment before retrying
                else:
                    self.logger.error(f"POST Request Error: {str(e)}")
                    return {'error': str(e)}
        return None  # If all retries fail


    async def fetch_url(self, url, headers, method="GET", body=None):
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(url, method=method, headers=headers, body=body, validate_cert=False, request_timeout=30    )
        return await http_client.fetch(request)
        

async def main():
    logger = Logger(filename='mylog.log', level=logging.DEBUG)
    api_config = {
        'url': "https://text-translator2.p.rapidapi.com",
        'headers': {
            "content-type": "application/x-www-form-urlencoded",
            "X-RapidAPI-Key": "3a43eaf733mshe6dd48090544630p12601fjsn9bc81ea4a5d1",
            "X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
        }
    }

    connector = Connector(api_url=api_config['url'], api_headers=api_config['headers'], logger=logger)
    

    #GET request
    get_response = await connector.make_get_request("/getLanguages")
    #logger.info(f"GET Response: {get_response}")
    
    payload = "source_language=en&target_language=fr&text=What%20is%20your%20name%3F"

    #POST request
    # async def make_post_requests(connector, payload, num_requests):
    #     for _ in range(num_requests):
    #         post_response = await connector.make_post_request("/translate", payload)
    #         logger.info(f"POST Response: {post_response}")

    
    num_requests = 1000
    
    async def make_post_requests(connector, payload, num_requests):
        for _ in range(num_requests):
            await connector.make_post_request("/translate", payload)

    request_queue = asyncio.Queue()

    for _ in range(num_requests):
        await request_queue.put(payload)

    tasks = []
    for _ in range(num_requests):
        task = asyncio.create_task(make_post_requests(connector, await request_queue.get(), 1))
        tasks.append(task)

    await asyncio.gather(*tasks)
    
    # post_response = await connector.make_post_request("/translate", payload)
    # logger.info(f"POST Response: {post_response}")

    
if __name__ == "__main__":
    asyncio.run(main())