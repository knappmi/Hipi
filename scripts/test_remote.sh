#!/bin/bash
# Quick test script for remote access

PI_IP=$(hostname -I | awk '{print $1}')

echo "=========================================="
echo "Raspberry Pi Remote Access Information"
echo "=========================================="
echo ""
echo "Your Raspberry Pi IP: $PI_IP"
echo ""
echo "Access URLs:"
echo "  Web UI:  http://$PI_IP:5000"
echo "  API:     http://$PI_IP:8000"
echo "  API Docs: http://$PI_IP:8000/docs"
echo ""
echo "Testing services..."
echo ""

# Test API
echo "Testing API health endpoint..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ API is responding"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/health
else
    echo "✗ API is not responding"
fi

echo ""
echo "Testing Web UI..."
if curl -s http://localhost:5000 > /dev/null; then
    echo "✓ Web UI is responding"
else
    echo "✗ Web UI is not responding"
fi

echo ""
echo "=========================================="
echo "To test from another computer:"
echo "  curl http://$PI_IP:8000/health"
echo "  curl http://$PI_IP:5000"
echo "=========================================="



