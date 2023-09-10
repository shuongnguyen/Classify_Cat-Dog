import tornado.ioloop
import tornado.web
import numpy as np
import onnxruntime
from PIL import Image
from io import BytesIO
import json

# Load ONNX model
def load_model(model_path):
    return onnxruntime.InferenceSession(model_path)

def classify_image(model, image_data):
    try:
        image = Image.open(BytesIO(image_data))
        image = image.resize((160, 160))  
        image_array = np.array(image)
        image_array = image_array.astype(np.float32)
        image_array = np.expand_dims(image_array, axis=0)

        # Thực hiện phân loại hình ảnh
        input_name = model.get_inputs()[0].name
        output_name = model.get_outputs()[0].name
        result = model.run([output_name], {input_name: image_array})
        

        # Xử lý dự đoán 
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
        raise Exception(f"Lỗi phân loại hình ảnh: {str(e)}")

class ImageClassificationHandler(tornado.web.RequestHandler):
    def initialize(self, model):
        self.model = model

    async def post(self):
        try:
            if 'image' in self.request.files:
                image_data = self.request.files['image'][0]['body']
                class_name, confidence = classify_image(self.model, image_data)

                result = {
                    "class_name": class_name,
                    #"confidence": float(confidence)
                }
                self.set_header("Content-Type", "application/json")
                self.write(json.dumps(result))
            else:
                self.set_status(400)  # Yêu cầu không hợp lệ
                self.write({"error": "Không có trường 'image' được tìm thấy trong yêu cầu."})
        except Exception as e:
            self.set_status(500)  

def make_app(model):
    return tornado.web.Application([
        (r"/classify", ImageClassificationHandler, dict(model=model)),
    ])

if __name__ == "__main__":
    model_path = 'my_model.onnx' 
    model = load_model(model_path)
    
    

    app = make_app(model)
    app.listen(8888)
    print("Dịch vụ phân loại hình ảnh đang chạy tại http://localhost:8888/classify")
    tornado.ioloop.IOLoop.current().start()
