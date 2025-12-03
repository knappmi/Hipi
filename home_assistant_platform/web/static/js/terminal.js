/**
 * Web Terminal using xterm.js
 */

class WebTerminal {
    constructor(containerId, wsUrl) {
        this.container = document.getElementById(containerId);
        this.wsUrl = wsUrl;
        this.term = null;
        this.socket = null;
        this.sessionId = null;
        this.init();
    }
    
    init() {
        // Initialize xterm.js terminal
        this.term = new Terminal({
            cursorBlink: true,
            fontSize: 14,
            fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
                cursor: '#ffffff',
                selection: '#264f78'
            }
        });
        
        this.term.open(this.container);
        
        // Add welcome message (will be overwritten by shell prompt)
        this.term.write('Connecting to terminal server...\r\n');
        
        // Handle input
        this.term.onData(data => {
            if (this.socket && this.socket.connected && this.sessionId) {
                // Send input with session ID
                try {
                    this.socket.emit('input', {
                        type: 'input',
                        data: data,
                        session_id: this.sessionId
                    });
                } catch (e) {
                    console.error('Error sending input:', e);
                }
            } else {
                console.warn('Cannot send input - socket not ready:', {
                    socket: !!this.socket,
                    connected: this.socket?.connected,
                    sessionId: this.sessionId
                });
            }
        });
        
        // Connect to WebSocket
        this.connect();
    }
    
    connect() {
        // Prevent multiple connections
        if (this.socket && this.socket.connected) {
            console.log('Already connected, skipping reconnect');
            return;
        }
        
        // Use Socket.IO instead of raw WebSocket
        if (typeof io === 'undefined') {
            this.term.writeln('\r\n\x1b[31mSocket.IO not loaded. Please refresh the page.\x1b[0m\r\n');
            return;
        }
        
        // Disconnect existing socket if any
        if (this.socket) {
            this.socket.removeAllListeners();
            this.socket.disconnect();
        }
        
        // Socket.IO connection - connect to namespace properly
        console.log('Connecting to Socket.IO namespace:', this.wsUrl);
        
        // Connect directly to the namespace URL
        this.socket = io(this.wsUrl, {
            transports: ['websocket', 'polling'],
            reconnection: false,
            autoConnect: true,
            timeout: 10000
        });
        
        this.socket.on('connect', () => {
            console.log('Terminal socket connected to namespace:', this.wsUrl);
            this.term.write('\r\n\x1b[32mConnected to terminal server.\x1b[0m\r\n');
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Terminal socket connection error:', error);
            this.term.write(`\r\n\x1b[31mConnection error: ${error.message || error}\x1b[0m\r\n`);
        });
        
        this.socket.on('output', (data) => {
            if (data && data.data) {
                this.term.write(data.data);
            }
        });
        
        this.socket.on('error', (error) => {
            console.error('Terminal socket error:', error);
        });
        
        this.socket.on('disconnect', (reason) => {
            console.log('Terminal socket disconnected:', reason);
        });
        
        this.socket.on('connected', (data) => {
            console.log('Terminal session connected:', data.session_id);
            this.sessionId = data.session_id;
        });
        
        // Timeout if connection doesn't complete
        setTimeout(() => {
            if (!this.sessionId) {
                console.warn('Terminal connection timeout - session not established');
                this.term.write('\r\n\x1b[33mConnection timeout. Please refresh the page.\x1b[0m\r\n');
            }
        }, 10000);
    }
    
    writePrompt() {
        // Don't write prompt - let the shell do it
        // This method kept for compatibility but not used
    }
    
    resize(cols, rows) {
        if (this.term && this.socket && this.socket.connected) {
            this.term.resize(cols, rows);
            this.socket.emit('resize', {
                cols: cols,
                rows: rows
            });
        }
    }
    
    destroy() {
        if (this.socket) {
            this.socket.disconnect();
        }
        if (this.term) {
            this.term.destroy();
        }
    }
}
