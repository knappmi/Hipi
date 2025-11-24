"""
Light Controller Plugin - Example plugin for controlling smart lights
"""

from flask import Flask, request, jsonify
import os
import logging
import paho.mqtt.client as mqtt

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLUGIN_ID = os.getenv("PLUGIN_ID", "light-controller")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# MQTT client
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()


@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "plugin_id": PLUGIN_ID,
        "mqtt_connected": mqtt_client.is_connected()
    })


@app.route('/command', methods=['POST'])
def command():
    """Execute light control command"""
    data = request.get_json()
    command = data.get("command")
    params = data.get("params", {})
    
    device = params.get("device", "light1")
    action = params.get("action", "toggle")
    
    if command == "control_light":
        topic = f"home/light/{device}/set"
        
        if action == "on":
            payload = "ON"
        elif action == "off":
            payload = "OFF"
        elif action == "toggle":
            payload = "TOGGLE"
        else:
            return jsonify({
                "success": False,
                "error": f"Unknown action: {action}"
            }), 400
        
        mqtt_client.publish(topic, payload)
        logger.info(f"Published {payload} to {topic}")
        
        return jsonify({
            "success": True,
            "device": device,
            "action": action,
            "topic": topic
        })
    
    return jsonify({
        "success": False,
        "error": f"Unknown command: {command}"
    }), 400


@app.route('/status', methods=['GET'])
def status():
    """Get plugin status"""
    return jsonify({
        "plugin_id": PLUGIN_ID,
        "status": "running",
        "mqtt_connected": mqtt_client.is_connected(),
        "mqtt_broker": f"{MQTT_BROKER}:{MQTT_PORT}"
    })


@app.route('/config', methods=['POST'])
def config():
    """Update configuration"""
    config_data = request.get_json()
    
    global MQTT_BROKER, MQTT_PORT
    
    if "mqtt_broker" in config_data:
        MQTT_BROKER = config_data["mqtt_broker"]
    
    if "mqtt_port" in config_data:
        MQTT_PORT = int(config_data["mqtt_port"])
    
    # Reconnect MQTT
    mqtt_client.disconnect()
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    return jsonify({
        "success": True,
        "message": "Configuration updated"
    })


if __name__ == '__main__':
    port = int(os.getenv("PORT", 8000))
    app.run(host='0.0.0.0', port=port, debug=False)



