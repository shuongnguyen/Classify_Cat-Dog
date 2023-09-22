
import tornado.ioloop
import tornado.web
import tornado.httpclient
import certifi
import ssl
import json
import logging


class MyLogger:
    def __init__(self, filename=None, filemode='a', level=logging.INFO):
        # Create a logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        # Create a formatter
        formatter = logging.Formatter('time="%(asctime)s" level=%(levelname)s service=S3Connector - parameters={%(bucket)s, %(key)s} - description=%(message)s')

        # Create a console handler and set the formatter
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # Create a file handler if a filename is provided and set the formatter
        if filename:
            fh = logging.FileHandler(filename, mode=filemode)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

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

# Create a logger instance with a filename (optional) and log level
logger = MyLogger(filename='mylog.log', level=logging.DEBUG)

# Log messages at different levels
# logger.debug('This is a debug message')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.critical('This is a critical message')

api_config = {
    'url': "https://text-translator2.p.rapidapi.com",
    'headers' : {
	"content-type": "application/x-www-form-urlencoded",
	"X-RapidAPI-Key": "8a1621535dmshc2b40537ec58d87p195d12jsnb94e212c6a53",
	"X-RapidAPI-Host": "text-translator2.p.rapidapi.com"
    }
}

class body:
    def __init__(self, source_language, target_language, text):
        self.source_language = source_language
        self.target_language = target_language
        self.text = text

request_body = body(source_language="", target_language="", text="")

request_body_json = json.dumps(request_body.__dict__)

class ConnectorHandler(tornado.web.RequestHandler):
    async def get(self):
        try:
            response = await self.fetch_url(api_config['url'] + "/getLanguages", api_config['headers'])
            self.write(response.body.decode('utf-8'))
        except Exception as e:
            self.write({'error': str(e)})

    async def post(self):
        try:
            response = await self.fetch_url(api_config['url'] + "/translate", api_config['headers'], method="POST", body=request_body_json)
            response_text = response.body.decode('utf-8')
            self.write(response_text)
            # Log the response for debugging
            self.logger.info(f"POST Response: Status Code: {response.code}, Body: {response_text}")
        except Exception as e:
            self.write({'error': str(e)})


    async def fetch_url(self, url, headers, method="GET", body=None):
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(url, method=method, headers=headers, body=body,  validate_cert=False)
        return await http_client.fetch(request)
    
                                                                                                                                                                                        

def make_app():
    return tornado.web.Application([
        (r'/api', ConnectorHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  
    print("Server is running at http://localhost:8888/api")
    # num_api_calls = 1000
    # async def call_apis():
    #     futures = []
    #     for _ in range(num_api_calls):
    #         # Choose whether to make GET or POST request
    #         if _ % 2 == 0:
    #             future = tornado.httpclient.AsyncHTTPClient().fetch(f"http://localhost:8888/api", method="GET")
    #         else:
    #             future = tornado.httpclient.AsyncHTTPClient().fetch(f"http://localhost:8888/api", method="POST", body=json.dumps(request_body))
    #         futures.append(future)

        # await tornado.gen.multi(futures)
    tornado.ioloop.IOLoop.current().start()
