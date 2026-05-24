import os
import uuid
from werkzeug.utils import secure_filename
from config import Config
import logging

logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_image_locally(file, user_id):
    """
    Save an image to the local filesystem securely.
    Returns the relative URL to access the image.
    """
    try:
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{user_id}_{uuid.uuid4().hex}.{ext}"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            file.save(filepath)
            
            # Return URL path (served by Flask app)
            return f"http://localhost:5000/uploads/{filename}"
        return None
    except Exception as e:
        logger.error(f"Error saving image locally: {e}")
        return None
