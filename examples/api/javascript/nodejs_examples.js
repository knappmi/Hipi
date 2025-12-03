/**
 * Example: Using the API with Node.js
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Device Control
async function listDevices() {
    const response = await axios.get(`${API_BASE_URL}/devices`);
    return response.data;
}

async function turnOnDevice(deviceId, brightness = null) {
    const data = { action: 'turn_on' };
    if (brightness !== null) {
        data.brightness = brightness;
    }
    const response = await axios.post(
        `${API_BASE_URL}/devices/${deviceId}/control`,
        data
    );
    return response.data;
}

async function turnOffDevice(deviceId) {
    const response = await axios.post(
        `${API_BASE_URL}/devices/${deviceId}/control`,
        { action: 'turn_off' }
    );
    return response.data;
}

// Scene Management
async function listScenes() {
    const response = await axios.get(`${API_BASE_URL}/scenes/scenes`);
    return response.data;
}

async function activateScene(sceneId) {
    const response = await axios.post(
        `${API_BASE_URL}/scenes/scenes/${sceneId}/activate`
    );
    return response.data;
}

// Example usage
async function main() {
    try {
        // List devices
        console.log('Listing devices...');
        const devices = await listDevices();
        console.log(devices);
        
        // Turn on first device
        if (devices.length > 0) {
            const deviceId = devices[0].id;
            console.log(`\nTurning on ${deviceId}...`);
            await turnOnDevice(deviceId, 50);
            
            // Turn off
            console.log('Turning off...');
            await turnOffDevice(deviceId);
        }
        
        // List scenes
        console.log('\nListing scenes...');
        const scenes = await listScenes();
        console.log(scenes);
        
        // Activate first scene
        if (scenes.length > 0) {
            console.log(`\nActivating scene ${scenes[0].id}...`);
            await activateScene(scenes[0].id);
        }
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = {
    listDevices,
    turnOnDevice,
    turnOffDevice,
    listScenes,
    activateScene
};

