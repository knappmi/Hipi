# Web Terminal

A fully-featured web-based terminal interface for the Home Assistant Platform.

## Features

- **Real-time Terminal**: Full terminal emulation using xterm.js
- **WebSocket Communication**: Real-time bidirectional communication
- **Session Management**: Isolated terminal sessions per user
- **Auto-resize**: Terminal automatically resizes to fit container
- **Dark Theme**: Modern dark theme for comfortable viewing
- **Security Warnings**: Clear warnings about system access

## Access

Navigate to **Terminal** in the main navigation menu or visit:
```
http://localhost:5000/terminal
```

## Usage

### Basic Commands

The terminal provides full shell access. Common commands:

```bash
# Platform CLI
hap devices list
hap automations list
hap scenes list

# System commands
ls -la
cd /app
pwd

# Python commands
python3 --version
pip list

# Exit terminal
exit
```

### Terminal Controls

- **Clear**: Clear the terminal screen
- **Reconnect**: Reconnect to terminal server
- **Close**: Close terminal and return to dashboard

### Keyboard Shortcuts

- `Ctrl+C`: Interrupt running command
- `Ctrl+D`: Exit terminal session
- `Ctrl+L`: Clear screen (if supported)
- `Tab`: Auto-completion

## Security

⚠️ **Warning**: The terminal has full system access. Use with caution.

### Security Features

- **Session Isolation**: Each terminal session is isolated
- **Sandboxed Environment**: Commands run in containerized environment
- **Access Control**: Terminal access can be restricted (future feature)

### Best Practices

1. **Don't run destructive commands** without understanding consequences
2. **Use platform CLI** (`hap`) for platform operations
3. **Check current directory** before file operations
4. **Exit properly** when done

## Technical Details

### Architecture

- **Frontend**: xterm.js terminal emulator
- **Backend**: Flask-SocketIO WebSocket server
- **Terminal**: PTY-based pseudo-terminal
- **Shell**: Bash login shell

### Components

1. **terminal.html**: Terminal UI template
2. **terminal.js**: Client-side terminal logic
3. **terminal_server.py**: WebSocket server and session management
4. **app.py**: Flask route and SocketIO integration

### WebSocket Events

- `connect`: Establish terminal connection
- `input`: Send user input to terminal
- `output`: Receive terminal output
- `resize`: Resize terminal window
- `disconnect`: Close terminal session

## Troubleshooting

### Terminal Not Connecting

1. Check Flask-SocketIO is installed: `pip list | grep flask-socketio`
2. Check WebSocket connection in browser console
3. Verify server is running: `docker compose ps`

### Terminal Freezing

1. Click "Reconnect" button
2. Refresh the page
3. Check server logs for errors

### Commands Not Working

1. Verify you're in the correct directory
2. Check command syntax
3. Use `which <command>` to verify command exists
4. Check PATH: `echo $PATH`

## Future Enhancements

- [ ] Terminal history persistence
- [ ] Multiple terminal tabs
- [ ] Terminal themes customization
- [ ] Command autocomplete
- [ ] Terminal sharing/collaboration
- [ ] Access control and permissions
- [ ] Terminal session recording

