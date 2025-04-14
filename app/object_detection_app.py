import os
import cv2
import numpy as np
from flask import Flask, request, render_template, url_for, redirect, flash
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
import time
import argparse

app = Flask(__name__)
app.config['SECRET_KEY'] = 'objectdetection'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# YOLO model parameters
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD = 0.4

# Initialize model variables
net = None
output_layers = None
classes = None

# Color ranges for invisibility cloak
COLOR_RANGES = {
    'red': {
        'lower': np.array([0, 120, 70]),
        'upper': np.array([10, 255, 255]),
        'lower2': np.array([170, 120, 70]),  # Red wraps around in HSV
        'upper2': np.array([180, 255, 255])
    },
    'blue': {
        'lower': np.array([100, 100, 70]),
        'upper': np.array([140, 255, 255])
    },
    'green': {
        'lower': np.array([35, 50, 50]),   # Widened green range to capture more shades
        'upper': np.array([90, 255, 255])  # Including darker and less saturated greens
    }
}

# Animal classes in COCO dataset
ANIMAL_CLASSES = [
    "bird", "cat", "dog", "horse", "sheep", "cow", 
    "elephant", "bear", "zebra", "giraffe"
]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    global net, output_layers, classes
    
    # Load COCO class labels
    classes_path = os.path.join(app.root_path, "model", "coco.names")
    if os.path.exists(classes_path):
        with open(classes_path, 'r') as f:
            classes = [line.strip() for line in f.readlines()]
    else:
        # Fallback with common COCO classes
        classes = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
                  "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                  "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
                  "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
                  "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
                  "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
                  "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
                  "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
                  "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
                  "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
    
    # Load model
    config_path = os.path.join(app.root_path, "model", "yolov4-tiny.cfg")
    weights_path = os.path.join(app.root_path, "model", "yolov4-tiny.weights")
    
    if os.path.exists(config_path) and os.path.exists(weights_path):
        print("Loading YOLO model...")
        net = cv2.dnn.readNet(weights_path, config_path)
        
        # Get output layer names
        layer_names = net.getLayerNames()
        try:
            # OpenCV 4.5.4+
            output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
        except:
            # Older OpenCV versions
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        
        print("YOLO model loaded successfully!")
        return True
    else:
        print("Model files not found. Please download the model first.")
        return False

def detect_objects(image_path):
    global net, output_layers, classes
    
    # Check if model is loaded
    if net is None:
        if not load_model():
            return None
    
    # Read image
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    
    # Create blob and run forward pass
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)
    
    # Process outputs
    class_ids = []
    confidences = []
    boxes = []
    
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > CONFIDENCE_THRESHOLD:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    # Apply non-maximum suppression to remove duplicate detections
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    
    # Store detection details for displaying in results
    detection_results = []
    
    # Count objects by category
    object_counts = {}
    
    # Draw bounding boxes
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    if len(indices) > 0:
        indices = indices.flatten()
        for i in indices:
            x, y, w, h = boxes[i]
            class_id = class_ids[i]
            label = str(classes[class_id])
            confidence = confidences[i]
            color = colors[class_id]
            
            # Update object count
            if label in object_counts:
                object_counts[label] += 1
            else:
                object_counts[label] = 1
            
            # Save detection details
            detection_results.append({
                'label': label,
                'confidence': confidence,
                'x': x,
                'y': y,
                'width': w,
                'height': h
            })
            
            # Draw rectangle with thicker line
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 3)
            
            # Draw label with bigger font and background
            text = f"{label} {int(confidence * 100)}%"
            font_scale = 1.0  # Increased from 0.5
            font_thickness = 2
            (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)
            
            # Draw background rectangle for text
            cv2.rectangle(image, (x, y - text_height - 10), (x + text_width, y), color, -1)
            
            # Draw text
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 
                       font_scale, (255, 255, 255), font_thickness)
    
    # Save processed image
    filename = os.path.basename(image_path)
    base_name, ext = os.path.splitext(filename)
    output_filename = f"{base_name}_detected{ext}"
    output_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], output_filename)
    cv2.imwrite(output_path, image)
    
    # Convert object_counts to sorted list for display
    object_count_list = [{'label': label, 'count': count} for label, count in object_counts.items()]
    object_count_list.sort(key=lambda x: x['count'], reverse=True)
    
    return output_filename, detection_results, object_count_list

def create_invisibility_effect(image_path, color_name):
    # Read the image
    image = cv2.imread(image_path)
    
    # Create a copy for background reference
    background = image.copy()
    
    # Apply a stronger Gaussian blur to reduce noise and smooth the background
    background = cv2.GaussianBlur(background, (21, 21), 0)
    
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Get color range
    color_range = COLOR_RANGES.get(color_name, COLOR_RANGES['red'])
    
    # Create mask for the selected color
    if color_name == 'red':
        # Red color wraps around in HSV, so we need two masks
        mask1 = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
        mask2 = cv2.inRange(hsv, color_range['lower2'], color_range['upper2'])
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])
    
    # Clean up the mask with morphological operations
    kernel = np.ones((7, 7), np.uint8)  # Larger kernel for better connectivity
    
    # Opening to remove small noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Dilate to fill gaps and make the cloak area more connected
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=3)
    
    # Additional closing to fill any remaining holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Create the invisibility effect
    # Where the mask is white (255), replace the original image with the background
    invisible = np.where(mask[:, :, np.newaxis] == 255, background, image)
    
    # Optional: Add a slight blur to the final result to make transitions smoother
    invisible = cv2.GaussianBlur(invisible, (3, 3), 0)
    
    # Save processed image
    filename = os.path.basename(image_path)
    base_name, ext = os.path.splitext(filename)
    output_filename = f"{base_name}_invisible{ext}"
    output_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], output_filename)
    cv2.imwrite(output_path, invisible)
    
    return output_filename

def censor_detected_objects(image_path, censor_classes, censor_method):
    global net, output_layers, classes
    
    # Check if model is loaded
    if net is None:
        if not load_model():
            return None
    
    # Read image
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    
    # Create blob and run forward pass
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outputs = net.forward(output_layers)
    
    # Process outputs
    class_ids = []
    confidences = []
    boxes = []
    
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > CONFIDENCE_THRESHOLD:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    # Apply non-maximum suppression to remove duplicate detections
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
    
    # Count censored objects
    censored_count = 0
    censored_objects = []
    
    # Censor objects based on class
    if len(indices) > 0:
        indices = indices.flatten()
        for i in indices:
            x, y, w, h = boxes[i]
            class_id = class_ids[i]
            label = str(classes[class_id])
            
            # Check if this object should be censored
            should_censor = False
            
            # Check specific classes
            if "person" in censor_classes and label == "person":
                should_censor = True
            elif "car" in censor_classes and label in ["car", "truck", "bus", "motorcycle"]:
                should_censor = True
            elif "animal" in censor_classes and label in ANIMAL_CLASSES:
                should_censor = True
            
            if should_censor:
                # Ensure the coordinates are within image boundaries
                x = max(0, x)
                y = max(0, y)
                w = min(w, width - x)
                h = min(h, height - y)
                
                # Actual censoring - select method
                if censor_method == "blur":
                    # Extract the region to blur
                    roi = image[y:y+h, x:x+w]
                    # Apply a strong blur
                    blurred = cv2.GaussianBlur(roi, (99, 99), 30)
                    # Put the blurred region back
                    image[y:y+h, x:x+w] = blurred
                
                elif censor_method == "pixelate":
                    # Extract the region to pixelate
                    roi = image[y:y+h, x:x+w]
                    # Downsample and upsample to create pixelation effect
                    pixelation_factor = 0.05  # adjust for different pixelation levels
                    small = cv2.resize(roi, (0, 0), fx=pixelation_factor, fy=pixelation_factor, interpolation=cv2.INTER_NEAREST)
                    pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
                    # Put the pixelated region back
                    image[y:y+h, x:x+w] = pixelated
                
                elif censor_method == "black":
                    # Simply black out the region
                    image[y:y+h, x:x+w] = np.zeros((h, w, 3), dtype=np.uint8)
                
                # Count the censored object
                censored_count += 1
                
                # Save censored object details
                censored_objects.append(label)
    
    # Save processed image
    filename = os.path.basename(image_path)
    base_name, ext = os.path.splitext(filename)
    output_filename = f"{base_name}_censored{ext}"
    output_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], output_filename)
    cv2.imwrite(output_path, image)
    
    # Group censored objects by type for display
    censored_classes_summary = list(set(censored_objects))
    
    return output_filename, censored_count, censored_classes_summary

def recognize_text(image_path, preprocess=False, highlight=False, language='eng'):
    """
    Perform OCR on an image to extract text.
    
    Args:
        image_path: Path to the image file
        preprocess: Whether to preprocess the image for better OCR results
        highlight: Whether to highlight detected text regions
        language: Language for OCR ('eng' for English, 'multi' for multiple languages)
    
    Returns:
        Tuple containing (output_filename, extracted_text, ocr_stats)
    """
    start_time = time.time()
    
    # Read image using PIL (better for OCR)
    pil_image = Image.open(image_path)
    original_width, original_height = pil_image.size
    
    # Set language config
    lang_config = language
    if language == 'multi':
        lang_config = 'eng+fra+deu+spa'  # English, French, German, Spanish
    
    # Preprocess image if required
    if preprocess:
        # Convert to opencv format for preprocessing
        cv_image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get black and white image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Noise removal
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Convert back to PIL for OCR
        processed_pil = Image.fromarray(opening)
        text = pytesseract.image_to_string(processed_pil, lang=lang_config)
        
        # Save the processed image for display
        processed_image = opening
    else:
        # Perform OCR directly on the original image
        text = pytesseract.image_to_string(pil_image, lang=lang_config)
        processed_image = cv2.imread(image_path)  # Just for display
    
    # Calculate statistics
    word_count = len(text.split())
    char_count = len(text.replace(" ", "").replace("\n", ""))
    
    # Get data about text boxes
    if highlight:
        # Read image using OpenCV
        cv_image = cv2.imread(image_path)
        
        # Get data for each detected text region
        boxes = pytesseract.image_to_data(pil_image, lang=lang_config, output_type=pytesseract.Output.DICT)
        
        # Draw boxes around text
        n_boxes = len(boxes['text'])
        text_boxes_count = 0
        
        for i in range(n_boxes):
            # Filter empty text and low confidence
            if int(boxes['conf'][i]) > 30 and boxes['text'][i].strip() != '':
                text_boxes_count += 1
                # Extract coordinates
                x, y, w, h = boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i]
                
                # Draw rectangle
                cv2.rectangle(cv_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Add text label
                text = boxes['text'][i]
                # Only show very short text to avoid cluttering the image
                if len(text) <= 5:
                    cv2.putText(cv_image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Use this as processed image for display
        processed_image = cv_image
    
    # Calculate processing time
    end_time = time.time()
    processing_time = round(end_time - start_time, 2)
    
    # Calculate confidence (approximation)
    confidence = "High" if word_count > 10 and char_count > 50 else "Medium" if word_count > 3 else "Low"
    
    # Save processed image
    filename = os.path.basename(image_path)
    base_name, ext = os.path.splitext(filename)
    output_filename = f"{base_name}_ocr{ext}"
    output_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], output_filename)
    cv2.imwrite(output_path, processed_image)
    
    # Prepare stats object for template
    ocr_stats = {
        'char_count': char_count,
        'word_count': word_count,
        'processing_time': processing_time,
        'confidence': confidence,
        'preprocess': 'Yes' if preprocess else 'No',
        'highlight': 'Yes' if highlight else 'No',
        'language': 'English' if language == 'eng' else 'Multiple Languages'
    }
    
    return output_filename, text, ocr_stats

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            result = detect_objects(file_path)
            if result:
                processed_image, detection_results, object_counts = result
                return render_template('result.html', 
                                      original=os.path.join('uploads', filename),
                                      processed=os.path.join('uploads', processed_image),
                                      detections=detection_results,
                                      object_counts=object_counts)
            else:
                flash('Model not loaded. Please download the model first.')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a PNG or JPG image.')
    return redirect(url_for('index'))

@app.route('/invisibility_cloak', methods=['POST'])
def invisibility_cloak():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    color = request.form.get('color', 'red')
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            processed_image = create_invisibility_effect(file_path, color)
            return render_template('invisibility_result.html', 
                                  original=os.path.join('uploads', filename),
                                  processed=os.path.join('uploads', processed_image),
                                  color=color)
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a PNG or JPG image.')
    return redirect(url_for('index'))

@app.route('/censor_objects', methods=['POST'])
def censor_objects():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # Get censoring options
    censor_classes = request.form.getlist('censor_classes')
    censor_method = request.form.get('censor_method', 'blur')
    
    if not censor_classes:
        flash('Please select at least one object type to censor')
        return redirect(url_for('index'))
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            result = censor_detected_objects(file_path, censor_classes, censor_method)
            if result:
                processed_image, censored_count, censored_classes_summary = result
                return render_template('censored_result.html', 
                                      original=os.path.join('uploads', filename),
                                      processed=os.path.join('uploads', processed_image),
                                      method=censor_method,
                                      censored_classes=censored_classes_summary,
                                      censored_count=censored_count)
            else:
                flash('Model not loaded. Please download the model first.')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a PNG or JPG image.')
    return redirect(url_for('index'))

@app.route('/recognize_text', methods=['POST'])
def recognize_text_route():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # Get OCR options
    preprocess = 'preprocess' in request.form
    highlight = 'highlight' in request.form
    language = request.form.get('language', 'eng')
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            processed_image, extracted_text, ocr_stats = recognize_text(
                file_path, preprocess, highlight, language
            )
            return render_template('text_recognition_result.html',
                                  original=os.path.join('uploads', filename),
                                  processed=os.path.join('uploads', processed_image),
                                  text=extracted_text,
                                  stats=ocr_stats)
        except Exception as e:
            flash(f'Error processing image: {str(e)}')
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a PNG or JPG image.')
    return redirect(url_for('index'))

@app.route('/download_model')
def download_model():
    # Create model directory if it doesn't exist
    model_dir = os.path.join(app.root_path, "model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    # Check if model files already exist
    weights_path = os.path.join(model_dir, "yolov4-tiny.weights")
    config_path = os.path.join(model_dir, "yolov4-tiny.cfg")
    classes_path = os.path.join(model_dir, "coco.names")
    
    if os.path.exists(weights_path) and os.path.exists(config_path) and os.path.exists(classes_path):
        flash("Model already downloaded. Ready for object detection!")
    else:
        # In a real application, you would download the files here
        # For this example, we'll just create a note about it
        flash("In a real app, the YOLOv4-tiny model would be downloaded from the official repository.")
        flash("For this example, you'll need to manually download the model files.")
        
        # Create a sample COCO classes file
        with open(classes_path, 'w') as f:
            classes = ["person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
                      "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                      "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack"]
            f.write("\n".join(classes))
    
    # Try to load the model
    if load_model():
        flash("Model loaded successfully. Ready for object detection!")
    else:
        flash("Model config created, but weights file is required for detection.")
        flash("Download YOLOv4-tiny weights and config from the official darknet repository.")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure upload directory exists
    upload_dir = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Try to load model if it exists
    load_model()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Object Detection App')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the app on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the app on')
    args = parser.parse_args()
    
    # Run the app
    app.run(debug=True, host=args.host, port=args.port) 