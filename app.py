import tornado.ioloop
import tornado.web

import numpy as np
import onnxruntime
from PIL import Image
from io import BytesIO
import json
import os
import logging
#from api import ApiConnector


current_directory = os.getcwd()
model_path = os.path.join(current_directory, "my_model.onnx")
if not model_path:
    raise Exception("Environment variable ONNX_MODEL_PATH is not set")
# Load ONNX model
def load_model(model_path):
    return onnxruntime.InferenceSession(model_path)

'''api_url = "https://bing-image-search1.p.rapidapi.com/images/search"
api_headers = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "8a1621535dmshc2b40537ec58d87p195d12jsnb94e212c6a53",
    "X-RapidAPI-Host": "bing-image-search1.p.rapidapi.com"
}
api_connector = ApiConnector(api_url, api_headers)'''

# Define the classify_image function
def classify_image(model, image_data):
    try:
        image = Image.open(BytesIO(image_data))
        image = image.resize((160, 160))  
        image_array = np.array(image)
        image_array = image_array.astype(np.float32)
        image_array = np.expand_dims(image_array, axis=0)

         #Perform image classification
        input_name = model.get_inputs()[0].name
        output_name = model.get_outputs()[0].name
        result = model.run([output_name], {input_name: image_array})
        

        #Process the prediction 
        predicted_class_index = np.argmax(result)
        confidence = result[0][0][predicted_class_index]
        class_labels = ["cats", "dogs"]  
        class_name = class_labels[predicted_class_index]
        if confidence >= 0.5:
            class_name = "dog"
        else:
            class_name ="cat"
    
        return class_name, float(confidence)
    except Exception as e:
        raise Exception(f"Error classifying image: {str(e)}")

# Create a Tornado request handler for image classification
class ImageClassificationHandler(tornado.web.RequestHandler):
    def initialize(self, model): #api_connector):
        self.model = model
        #self.api_connector = api_connector
        
    async def get(self):
        self.render("upload_image.html")
        
    async def post(self):
        try:
            if 'image' in self.request.files:
                image_data = self.request.files['image'][0]['body']
                class_name, confidence = classify_image(self.model, image_data)
                
                 # Call the ApiConnector to send the image data to an external API
                #api_result = await self.api_connector.send_image_data(image_data)


                result = {
                    "class_name": class_name,
                    #"api_result": api_result,
                    #"confidence": float(confidence)
                }
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps(result))
            else:
                self.set_status(400)  # Error request
                self.write({"error": "No 'image' field found in the request."})
        except Exception as e:
            self.set_status(500)  #Error server



def make_app(model):
    #api_url = "https://bing-image-search1.p.rapidapi.com/images/search"
    #querystring = {"insightsToken": "</?insightsToken=?&query=cats>", "query": "<OPTIONAL>"}
    #api_connector = ApiConnector(api_url, querystring)
    return tornado.web.Application([
        (r"/classify", ImageClassificationHandler, dict(model=model)), #api_connector=api_connector)),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ],
    template_path=os.path.join(os.getcwd(), "templates"))

if __name__ == "__main__":
    logging.basicConfig(filename='api_calls.log', level=logging.INFO)
    app = make_app(load_model(model_path))
    logging.getLogger().setLevel(logging.ERROR)

    app.listen(8888)
    print("Image Classification Microservice is running at http://localhost:8888/classify")
    tornado.ioloop.IOLoop.current().start()