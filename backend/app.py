import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config

cors = CORS()

def create_app(config_class=Config):
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
    app = Flask(__name__, static_folder=os.path.join(frontend_dir, 'static'), static_url_path='/static')
    app.config.from_object(config_class)

    # Initialize CORS for all origins and headers
    cors.init_app(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "service": "EcoAI-Backend"}), 200

    @app.route('/uploads/<filename>')
    def serve_uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Serve Frontend HTML Pages
    @app.route('/')
    def serve_index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/<path:filename>')
    def serve_frontend_page(filename):
        file_path = os.path.join(frontend_dir, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(frontend_dir, filename)
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=app.config.get('PORT', 5000), debug=app.config.get('DEBUG', True))

