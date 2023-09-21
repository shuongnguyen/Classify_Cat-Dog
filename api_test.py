import tornado.ioloop
import tornado.web
import tornado.httpclient
import certifi
import ssl

class ConnectorHandler(tornado.web.RequestHandler):
    async def get(self):
        url = "https://arimagesynthesizer.p.rapidapi.com/my_images"
        headers = {
            'X-RapidAPI-Key': "8a1621535dmshc2b40537ec58d87p195d12jsnb94e212c6a53",
            'X-RapidAPI-Host': "arimagesynthesizer.p.rapidapi.com"
        }
        ssl._create_default_https_context = ssl._create_unverified_context
        ssl._create_default_https_context().load_verify_locations(certifi.where())
        try:
            response = await self.fetch_url(url, headers)
            self.write(response.body.decode('utf-8'))
        except Exception as e:
            self.write({'error': str(e)})

    async def fetch_url(self, url, headers):
        http_client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(url, method="GET", headers=headers)
        return await http_client.fetch(request)

def make_app():
    return tornado.web.Application([
        (r'/api', ConnectorHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)  
    print("Server is running on port 8888...")
    tornado.ioloop.IOLoop.current().start()
