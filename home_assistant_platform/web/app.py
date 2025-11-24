"""Flask web management UI"""

import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
import json
import requests

from home_assistant_platform.config.settings import settings
from home_assistant_platform.config.logging_config import setup_logging

logger = setup_logging()

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = settings.secret_key
CORS(app)

# FastAPI base URL
API_BASE_URL = f"http://localhost:{settings.api_port}/api/v1"


@app.route('/')
def index():
    """Dashboard home page"""
    return render_template('dashboard.html')


@app.route('/api/status')
def api_status():
    """Get platform status"""
    return jsonify({
        "status": "running",
        "version": settings.platform_version,
        "name": settings.platform_name
    })


@app.route('/plugins')
def plugins_page():
    """Plugin management page"""
    return render_template('plugins.html')


@app.route('/marketplace')
def marketplace_page():
    """Marketplace page"""
    return render_template('marketplace.html')


@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')


@app.route('/voice')
def voice_page():
    """Voice settings page"""
    return render_template('voice.html')


@app.route('/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_api(path):
    """Proxy API requests to FastAPI"""
    try:
        url = f"{API_BASE_URL}/{path}"
        
        # Forward the request to FastAPI
        if request.method == 'GET':
            response = requests.get(url, params=request.args, timeout=10)
        elif request.method == 'POST':
            response = requests.post(
                url, 
                json=request.get_json() if request.is_json else None,
                data=request.form if request.form else None,
                params=request.args,
                timeout=10
            )
        elif request.method == 'PUT':
            response = requests.put(
                url,
                json=request.get_json() if request.is_json else None,
                params=request.args,
                timeout=10
            )
        elif request.method == 'DELETE':
            response = requests.delete(url, params=request.args, timeout=10)
        elif request.method == 'PATCH':
            response = requests.patch(
                url,
                json=request.get_json() if request.is_json else None,
                params=request.args,
                timeout=10
            )
        else:
            return jsonify({"error": "Method not allowed"}), 405
        
        # Return the response from FastAPI
        return response.json(), response.status_code
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API proxy error: {e}")
        return jsonify({"error": f"Failed to connect to API: {str(e)}"}), 503
    except Exception as e:
        logger.error(f"Unexpected error in API proxy: {e}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=settings.web_ui_port,
        debug=settings.debug
    )

