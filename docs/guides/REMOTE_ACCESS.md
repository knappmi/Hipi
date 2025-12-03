# Remote Access Guide

## Finding Your Raspberry Pi's IP Address

### Method 1: From the Raspberry Pi
```bash
hostname -I
# or
ip addr show
```

### Method 2: From your local network
```bash
# Scan your network (from another computer)
nmap -sn 192.168.1.0/24 | grep -B 2 "Raspberry Pi"
```

### Method 3: Check your router
- Log into your router's admin panel
- Look for connected devices
- Find "raspberrypi" or your Pi's hostname

## Accessing the Platform Remotely

Once you have the IP address (e.g., `192.168.1.100`):

### Web UI
Open in your browser:
```
http://YOUR_PI_IP:5000
```
Example: `http://192.168.1.100:5000`

### API
Access the API at:
```
http://YOUR_PI_IP:8000
```
Example: `http://192.168.1.100:8000`

### API Documentation
```
http://YOUR_PI_IP:8000/docs
```

## Testing from Your Computer

### Test Web UI
```bash
curl http://YOUR_PI_IP:5000
```

### Test API Health
```bash
curl http://YOUR_PI_IP:8000/health
```

### Test API Root
```bash
curl http://YOUR_PI_IP:8000/
```

## Firewall Configuration

If you can't access the services, you may need to configure the firewall:

### Ubuntu/Debian (ufw)
```bash
sudo ufw allow 5000/tcp
sudo ufw allow 8000/tcp
sudo ufw status
```

### Raspberry Pi OS (iptables)
```bash
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables-save
```

## Docker Network Configuration

The platform is configured to listen on `0.0.0.0` (all interfaces), so it should be accessible remotely by default.

### Verify Docker is listening on all interfaces
```bash
sudo docker compose ps
sudo netstat -tlnp | grep -E "5000|8000"
```

## Security Considerations

### For Production Use:

1. **Use HTTPS**: Set up a reverse proxy (nginx) with SSL certificates
2. **Firewall**: Only allow access from trusted IPs
3. **Authentication**: Implement proper authentication (currently basic)
4. **VPN**: Consider using a VPN for remote access instead of exposing ports

### Quick Security Setup
```bash
# Only allow local network access (adjust IP range)
sudo ufw allow from 192.168.1.0/24 to any port 5000
sudo ufw allow from 192.168.1.0/24 to any port 8000
```

## Troubleshooting

### Can't connect from remote machine

1. **Check if services are running:**
   ```bash
   sudo docker compose ps
   ```

2. **Check if ports are listening:**
   ```bash
   sudo netstat -tlnp | grep -E "5000|8000"
   ```

3. **Check firewall:**
   ```bash
   sudo ufw status
   ```

4. **Test locally first:**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Check Docker network:**
   ```bash
   sudo docker compose logs platform
   ```

### Connection Refused

- Verify the IP address is correct
- Check if you're on the same network
- Ensure firewall allows the ports
- Check Docker container is running

### Timeout

- Check network connectivity: `ping YOUR_PI_IP`
- Verify router doesn't block internal traffic
- Check if Pi has internet connection

## Access from Internet (Advanced)

If you want to access from outside your local network:

1. **Port Forwarding**: Configure your router to forward ports 5000 and 8000 to your Pi
2. **Dynamic DNS**: Use a service like DuckDNS or No-IP
3. **Reverse Proxy**: Use nginx with SSL (recommended)
4. **VPN**: Set up a VPN server (most secure)

**Warning**: Exposing services directly to the internet without proper security is risky. Always use HTTPS and authentication.



