from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required
from utils.upload_utils import save_image_locally, allowed_file
from ml.infer import predict_ewaste
from utils.rewards_utils import calculate_reward_points
from database import get_db_connection
import logging

logger = logging.getLogger(__name__)
ml_bp = Blueprint('ml', __name__)

@ml_bp.route('/predict', methods=['POST'])
@token_required
def predict(current_user):
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    try:
        # Read file bytes for ML inference
        image_bytes = file.read()
        
        # 1. Run ML Inference
        category, confidence, is_blurry = predict_ewaste(image_bytes)
        
        if is_blurry:
            return jsonify({
                "error": "Image is too blurry. Please upload a clearer image of the e-waste."
            }), 400

        # Reset file pointer before uploading locally
        file.seek(0)
        
        # 2. Upload to local file system
        image_url = save_image_locally(file, user_id=current_user['id'])
        
        if not image_url:
            return jsonify({"error": "Failed to securely store image locally"}), 500

        # 3. Calculate estimated reward
        conn = None
        estimated_reward = 50
        try:
            conn = get_db_connection()
            estimated_reward = calculate_reward_points(category, conn)
        except Exception as db_err:
            logger.warning(f"Could not connect to database for dynamic reward estimation: {db_err}")
            estimated_reward = calculate_reward_points(category)
        finally:
            if conn and conn.is_connected():
                conn.close()

        return jsonify({
            "category": category,
            "confidence": confidence,
            "image_url": image_url,
            "estimated_reward": estimated_reward
        }), 200

    except Exception as e:
        logger.error(f"Prediction route error: {e}")
        return jsonify({"error": "Internal server error during prediction"}), 500

