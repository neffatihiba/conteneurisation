
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import shutil
import os
import torch
from PIL import Image
from io import BytesIO
import numpy as np

# Initialize FastAPI app
app = FastAPI()

# Path to YOLOv5 model
MODEL_PATH = "yolov5s.pt"

# Function to load YOLOv5 model
def load_model(model_path):
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)
    return model

# Load the model at startup
model = load_model(MODEL_PATH)

# Function to perform object detection and save image with predictions
def predict_and_save_image(image_bytes, output_path):
    # Load image from bytes
    image = Image.open(BytesIO(image_bytes)).convert('RGB')
    img = np.array(image)

    # Perform inference
    results = model(img)

    # Save the results image with detections
    results.save(save_dir=output_path)
    return os.path.join(output_path, os.listdir(output_path)[0])
    
# Route for object detection endpoint
@app.post("/predict", tags=["detection"])
async def predict(file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily in uploadedimages folder
        upload_folder = "uploadedimages"
        os.makedirs(upload_folder, exist_ok=True)
        temp_file_path = os.path.join(upload_folder, file.filename)

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read the saved file as bytes
        image_bytes = open(temp_file_path, "rb").read()

        # Define the output directory for the processed image in results folder
        output_dir = "processed_img"
        os.makedirs(output_dir, exist_ok=True)

        # Perform object detection and save the image with predictions
        output_image_path = predict_and_save_image(image_bytes, output_dir)

        # Remove the temporary file from uploadedimages folder
       # os.remove(temp_file_path)

        # Return the processed image as a response
        return FileResponse(output_image_path, media_type="image/jpeg", filename="result.jpg")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("appfast:app", host="0.0.0.0", port=8080)
