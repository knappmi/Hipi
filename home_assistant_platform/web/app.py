"""Flask web management UI"""

import logging
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_cors import CORS
from flask_socketio import SocketIO
import json
import requests
import markdown

from home_assistant_platform.config.settings import settings
from home_assistant_platform.config.logging_config import setup_logging

logger = setup_logging()

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = settings.secret_key
CORS(app)

# Initialize SocketIO for WebSocket support
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=True
)

# Initialize terminal server
from home_assistant_platform.web.terminal_server import TerminalServer
terminal_server = TerminalServer(app, socketio)

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


@app.route('/onboarding')
def onboarding_page():
    """Onboarding wizard page"""
    return render_template('onboarding.html')


@app.route('/terminal')
def terminal_page():
    """Web terminal page"""
    return render_template('terminal.html')


@app.route('/docs')
def docs_index():
    """Documentation index page"""
    docs_dir = Path(__file__).parent.parent.parent / 'docs'
    docs_files = []
    
    if docs_dir.exists():
        for file in sorted(docs_dir.glob('*.md')):
            if file.name != 'README.md':  # Skip the index
                docs_files.append({
                    'name': file.stem.replace('_', ' ').title(),
                    'filename': file.name,
                    'path': f'/docs/{file.name}'
                })
    
    return render_template('docs_index.html', docs_files=docs_files)


@app.route('/docs/<doc_name>')
def docs_viewer(doc_name):
    """View a specific documentation file"""
    docs_dir = Path(__file__).parent.parent.parent / 'docs'
    doc_path = docs_dir / doc_name
    
    if not doc_path.exists() or not doc_name.endswith('.md'):
        return render_template('docs_viewer.html', 
                            doc_title="Not Found",
                            doc_content="<p>Documentation file not found.</p>",
                            doc_name=doc_name)
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML with fallback for missing extensions
        html_content = None
        extensions_to_try = [
            (['codehilite', 'fenced_code', 'tables', 'toc'], {'codehilite': {'css_class': 'highlight', 'use_pygments': False}}),
            (['fenced_code', 'tables', 'toc'], {}),
            (['fenced_code', 'tables'], {}),
            (['tables'], {}),
            ([], {})  # Basic markdown
        ]
        
        last_error = None
        for extensions, config in extensions_to_try:
            try:
                if extensions:
                    html_content = markdown.markdown(
                        markdown_content,
                        extensions=extensions,
                        extension_configs=config if config else {}
                    )
                else:
                    html_content = markdown.markdown(markdown_content)
                logger.debug(f"Successfully rendered markdown with extensions: {extensions}")
                break
            except Exception as e:
                last_error = e
                logger.debug(f"Failed with extensions {extensions}: {e}")
                continue
        
        if html_content is None:
            raise Exception(f"Failed to render markdown after trying all extension combinations: {last_error}")
        
        doc_title = doc_name.replace('_', ' ').replace('.md', '').title()
        
        return render_template('docs_viewer.html',
                              doc_title=doc_title,
                              doc_content=html_content,
                              doc_name=doc_name)
    except Exception as e:
        logger.error(f"Error reading or rendering documentation file {doc_name}: {e}", exc_info=True)
        return render_template('docs_viewer.html',
                            doc_title="Error",
                            doc_content=f"<p>Error loading documentation: {str(e)}</p><pre style='background: #f5f5f5; padding: 1rem; border-radius: 5px; overflow-x: auto;'>{repr(e)}</pre>",
                            doc_name=doc_name), 500


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
    # Ensure Flask binds to 0.0.0.0 to be accessible from outside container
    import os
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', settings.web_ui_port))
    
    socketio.run(
        app,
        host=host,
        port=port,
        debug=settings.debug,
        allow_unsafe_werkzeug=True,
        use_reloader=False  # Disable reloader in production
    )

