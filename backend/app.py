from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# Initialize extensions
cors = CORS()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.bookings import bookings_bp
    from routes.admin import admin_bp
    from routes.ml_inference import ml_bp
    from routes.rewards import rewards_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(bookings_bp, url_prefix='/api/bookings')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(rewards_bp, url_prefix='/api/rewards')

    # Basic error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "EcoAI-Backend"}), 200

    from flask import send_from_directory
    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=app.config.get('PORT', 5000), debug=app.config.get('DEBUG', True))
