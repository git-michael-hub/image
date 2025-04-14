import os
import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, request, render_template, url_for, redirect, flash, send_from_directory
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'objectdetection'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Load pre-trained model
model = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    global model
    model = tf.saved_model.load('model/saved_model')
    print("Model loaded successfully!")

def detect_objects(image_path):
    # Read image
    image = cv2.imread(image_path)
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    
    # Run inference
    detections = model(input_tensor)
    
    # Process output
    num_detections = int(detections.pop('num_detections'))
    detections = {key: value[0, :num_detections].numpy() 
                  for key, value in detections.items()}
    
    boxes = detections['detection_boxes']
    classes = detections['detection_classes'].astype(np.int64)
    scores = detections['detection_scores']
    
    # Draw bounding boxes
    height, width, _ = image.shape
    for i in range(len(boxes)):
        if scores[i] > 0.5:  # Confidence threshold
            box = boxes[i]
            y_min, x_min, y_max, x_max = box
            y_min = int(y_min * height)
            x_min = int(x_min * width)
            y_max = int(y_max * height)
            x_max = int(x_max * width)
            
            # Draw rectangle
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            
            # Draw label
            class_id = int(classes[i])
            class_name = category_index.get(class_id, {}).get('name', 'N/A')
            label = f"{class_name}: {int(scores[i] * 100)}%"
            cv2.putText(image, label, (x_min, y_min - 10), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Save processed image
    output_path = image_path.replace('.', '_detected.')
    cv2.imwrite(output_path, image)
    return os.path.basename(output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            processed_image = detect_objects(file_path)
            return render_template('result.html', 
                                  original=os.path.join(app.config['UPLOAD_FOLDER'], filename),
                                  processed=os.path.join(app.config['UPLOAD_FOLDER'], processed_image))
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a PNG or JPG image.')
    return redirect(url_for('index'))

@app.route('/download_model')
def download_model():
    global category_index
    # Download model and label map
    try:
        if not os.path.exists('model'):
            os.makedirs('model')
            
        # For simplicity, we'll use a pre-trained model from TensorFlow Hub
        # In a real app, you'd want to download a specific model here
        model_url = 'http://download.tensorflow.org/models/object_detection/tf2/20200711/ssd_mobilenet_v2_320x320_coco17_tpu-8.tar.gz'
        
        # Label map
        label_map_url = 'https://raw.githubusercontent.com/tensorflow/models/master/research/object_detection/data/mscoco_label_map.pbtxt'
        
        # Code to download and extract model would go here
        # For now, we'll just inform the user
        flash("Model download would happen here in a production app")
        
        # Load labels
        category_index = {1: {'id': 1, 'name': 'person'},
                          2: {'id': 2, 'name': 'bicycle'},
                          # ... more classes would be added here
                         }
        
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"Error downloading model: {str(e)}")
        return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure upload directory exists
    if not os.path.exists(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])):
        os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']))
    
    # For demo purposes, we'll initialize with dummy label map
    # In a real app, this would be loaded from the model
    global category_index
    category_index = {1: {'id': 1, 'name': 'person'},
                      2: {'id': 2, 'name': 'bicycle'},
                      3: {'id': 3, 'name': 'car'},
                      4: {'id': 4, 'name': 'motorcycle'},
                      5: {'id': 5, 'name': 'airplane'},
                      6: {'id': 6, 'name': 'bus'},
                      7: {'id': 7, 'name': 'train'},
                      8: {'id': 8, 'name': 'truck'},
                      9: {'id': 9, 'name': 'boat'},
                      10: {'id': 10, 'name': 'traffic light'}}
    
    # For demonstration, we won't load the model immediately
    # Users will need to click a button to download it
    app.run(debug=True) 