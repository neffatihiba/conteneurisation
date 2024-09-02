
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import torch
from PIL import Image
from io import BytesIO
import numpy as np

app = FastAPI()


MODEL_PATH = "yolov5s.pt"


def load_model(model_path):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
    return model


model = load_model(MODEL_PATH)


def predict_and_save_image(image_bytes, output_path):
 
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    img = np.array(image)

 
    results = model(img)

  
    results.save(save_dir=output_path)
    return os.path.join(output_path, os.listdir(output_path)[0])
    

@app.post("/predict", tags=["detection"])
async def predict(file: UploadFile = File(...)):
    try:
        upload_folder = "uploadedimages"
        os.makedirs(upload_folder, exist_ok=True)
        temp_file_path = os.path.join(upload_folder, file.filename)

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        
        image_bytes = open(temp_file_path, "rb").read()

       
        output_dir = "processed_img"
        os.makedirs(output_dir, exist_ok=True)

        output_image_path = predict_and_save_image(image_bytes, output_dir)

        return FileResponse(output_image_path, media_type="image/jpeg", filename="result.jpg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("appfast:app", host="0.0.0.0", port=8080)
