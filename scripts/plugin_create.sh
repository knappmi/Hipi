#!/bin/bash
# Plugin creation script

PLUGIN_NAME=$1

if [ -z "$PLUGIN_NAME" ]; then
    echo "Usage: $0 <plugin-name>"
    echo "Example: $0 my-awesome-plugin"
    exit 1
fi

PLUGIN_DIR="plugins/${PLUGIN_NAME}"
TEMPLATE_DIR="plugin_sdk/template"

if [ -d "$PLUGIN_DIR" ]; then
    echo "Error: Plugin directory already exists: $PLUGIN_DIR"
    exit 1
fi

echo "Creating plugin: $PLUGIN_NAME"
echo "Directory: $PLUGIN_DIR"

# Create plugin directory
mkdir -p "$PLUGIN_DIR"

# Copy template files
cp "${TEMPLATE_DIR}/app.py" "$PLUGIN_DIR/"
cp "${TEMPLATE_DIR}/Dockerfile" "$PLUGIN_DIR/"
cp "${TEMPLATE_DIR}/requirements.txt" "$PLUGIN_DIR/"

# Create manifest.json
cat > "$PLUGIN_DIR/manifest.json" << EOF
{
  "id": "${PLUGIN_NAME}",
  "name": "$(echo $PLUGIN_NAME | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')",
  "version": "1.0.0",
  "description": "Description of ${PLUGIN_NAME}",
  "author": "Your Name",
  "image": "${PLUGIN_NAME}:latest",
  "api_port": 8000,
  "cpu_limit": 0.5,
  "memory_limit": "512m",
  "network_access": true,
  "device_access": false,
  "price": 0.0,
  "category": "utilities",
  "tags": ["custom"]
}
EOF

# Create README
cat > "$PLUGIN_DIR/README.md" << EOF
# ${PLUGIN_NAME}

Plugin description here.

## Installation

\`\`\`bash
# Build plugin
docker build -t ${PLUGIN_NAME}:latest .

# Test locally
docker run -p 8000:8000 ${PLUGIN_NAME}:latest
\`\`\`

## Usage

Describe how to use the plugin.

## API Endpoints

- \`GET /health\` - Health check
- \`POST /command\` - Execute commands
- \`GET /status\` - Get status
- \`POST /config\` - Update configuration
EOF

echo ""
echo "✓ Plugin created successfully!"
echo ""
echo "Next steps:"
echo "  1. Edit $PLUGIN_DIR/app.py to implement your plugin logic"
echo "  2. Update $PLUGIN_DIR/manifest.json with your plugin details"
echo "  3. Build: docker build -t ${PLUGIN_NAME}:latest $PLUGIN_DIR"
echo "  4. Test: docker run -p 8000:8000 ${PLUGIN_NAME}:latest"
echo "  5. Install: Use the platform UI or API to install"

