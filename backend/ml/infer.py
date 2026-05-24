import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Try to import TensorFlow, gracefully handle if not installed properly (e.g. Windows Long Path issue)
try:
    import tensorflow as tf
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow is not available or broken. ML Inference will run in simulation mode.")

# Try to load custom fine-tuned model, otherwise fallback to base MobileNetV2
MODEL_PATH = 'saved_models/ewaste_mobilenetv2.h5'
CUSTOM_CATEGORIES = [
    'Smartphone', 'Laptop', 'Keyboard/Mouse', 'Cables/Wires', 
    'Battery', 'Display/Monitor', 'Printer/Scanner'
]

# A simple mapping heuristic for fallback mode
FALLBACK_MAPPING = {
    'cellular_telephone': 'Smartphone',
    'laptop': 'Laptop',
    'notebook': 'Laptop',
    'computer_keyboard': 'Keyboard/Mouse',
    'mouse': 'Keyboard/Mouse',
    'monitor': 'Display/Monitor',
    'television': 'Display/Monitor',
    'printer': 'Printer/Scanner',
    'modem': 'Cables/Wires' # Approximate
}

model = None
is_custom = False

if TF_AVAILABLE:
    try:
        if os.path.exists(MODEL_PATH):
            model = tf.keras.models.load_model(MODEL_PATH)
            is_custom = True
            logger.info("Loaded custom E-Waste model.")
        else:
            model = tf.keras.applications.MobileNetV2(weights='imagenet')
            is_custom = False
            logger.info("Loaded fallback MobileNetV2 (ImageNet weights).")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model = None

def preprocess_image(image_bytes):
    """Decode image bytes and preprocess for MobileNetV2."""
    try:
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Check for blur using Laplacian variance
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = blur_score < 50.0  # Threshold
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (224, 224))
        
        # Expand dims and preprocess
        img_array = np.expand_dims(img, axis=0)
        img_array = preprocess_input(img_array)
        
        return img_array, is_blurry
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return None, False

def predict_ewaste(image_bytes):
    """
    Predict the e-waste category from image bytes.
    Returns: category (str), confidence (float), is_blurry (bool)
    """
    # If TensorFlow is missing, simulate the ML inference
    if not TF_AVAILABLE or model is None:
        logger.info("Simulation mode: Pretending to classify image.")
        import random
        # Just pick a random category for demo purposes
        category = random.choice(CUSTOM_CATEGORIES)
        confidence = round(random.uniform(0.7, 0.99), 2)
        return category, confidence, False

    img_array, is_blurry = preprocess_image(image_bytes)
    if img_array is None:
        return "Invalid Image", 0.0, False

    try:
        preds = model.predict(img_array)
        
        if is_custom:
            idx = np.argmax(preds[0])
            confidence = float(preds[0][idx])
            category = CUSTOM_CATEGORIES[idx] if confidence > 0.5 else "Unrecognized E-Waste"
        else:
            # Fallback mode using ImageNet labels
            decoded = decode_predictions(preds, top=3)[0]
            # decoded looks like: [('n03085013', 'keyboard', 0.8), ...]
            
            category = "Unrecognized Item"
            confidence = 0.0
            
            for _, label, conf in decoded:
                label_clean = label.lower()
                # Find in mapping
                mapped_cat = FALLBACK_MAPPING.get(label_clean)
                if mapped_cat:
                    category = mapped_cat
                    confidence = float(conf)
                    break
            
            # If not found in mapping but we have a generic prediction
            if category == "Unrecognized Item" and decoded[0][2] > 0.3:
                # Just return the top label capitalized as a generic fallback
                category = decoded[0][1].replace('_', ' ').title()
                confidence = float(decoded[0][2])

        return category, confidence, is_blurry

    except Exception as e:
        logger.error(f"Inference error: {e}")
        return "Inference Error", 0.0, False
