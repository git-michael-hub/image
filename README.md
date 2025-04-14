# Object Detection App

A simple Python application that identifies and labels objects in images using computer vision.

## Features

- Upload images (PNG, JPG) for object detection
- Identify common objects in uploaded images
- Display bounding boxes and labels around detected objects
- Show confidence percentage for each detected object

## Requirements

- Python 3.8+
- OpenCV
- NumPy
- Flask
- YOLOv4-tiny model weights and configuration

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd object-detection-app
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Download the YOLOv4-tiny model:
   - The app will create a placeholder for the model files
   - For actual detection, you need to download:
     - YOLOv4-tiny weights file: `yolov4-tiny.weights`
     - YOLOv4-tiny configuration file: `yolov4-tiny.cfg`
   - Place these files in the `app/model` directory
   - You can download them from the official Darknet repository

## Usage

1. Start the application:
```
cd app
python object_detection_app.py
```

2. Open your web browser and go to:
```
http://127.0.0.1:5000
```

3. Click the "Download Object Detection Model" button if this is your first time (or click it to verify the model is ready)

4. Upload an image using the form

5. View the detection results showing the original image and the processed image with labeled objects

## How It Works

This application uses YOLOv4-tiny (You Only Look Once), a real-time object detection system:

1. The uploaded image is processed using OpenCV
2. The YOLO neural network detects objects in the image
3. Non-maximum suppression is applied to remove overlapping detections
4. Bounding boxes are drawn around detected objects with labels
5. The processed image is displayed alongside the original

## Model Information

YOLOv4-tiny is a smaller, faster version of the YOLOv4 object detection model:

- Pre-trained on the COCO dataset (Common Objects in Context)
- Can detect 80 different object categories
- Optimized for speed while maintaining reasonable accuracy
- Suitable for real-time applications and devices with limited computational resources

## Customization

You can modify the following parameters in `object_detection_app.py`:

- `CONFIDENCE_THRESHOLD`: Minimum confidence to consider a detection valid (default: 0.5)
- `NMS_THRESHOLD`: Non-maximum suppression threshold (default: 0.4)

## Troubleshooting

- If you encounter issues with model loading, ensure the model files are correctly placed in the `app/model` directory
- For best results, use clear images with well-defined objects
- The app works best with common objects found in the COCO dataset # image
