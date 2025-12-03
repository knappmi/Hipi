"""WebSocket terminal server for web UI"""

import logging
import asyncio
import subprocess
import os
import pty
import select
import struct
import fcntl
import termios
import pwd
import grp
from typing import Optional
from flask import Flask
from flask_socketio import SocketIO, emit, disconnect

logger = logging.getLogger(__name__)

# Terminal user configuration
TERMINAL_USER = os.getenv('TERMINAL_USER', 'hapuser')
TERMINAL_UID = int(os.getenv('TERMINAL_UID', '1001'))
TERMINAL_GID = int(os.getenv('TERMINAL_GID', '1001'))
TERMINAL_HOME = os.getenv('TERMINAL_HOME', '/app/home')
RESTRICTED_SHELL = os.getenv('RESTRICTED_SHELL', '/bin/bash')  # Can be /bin/rbash for restricted bash


class TerminalServer:
    """WebSocket-based terminal server"""
    
    def __init__(self, app: Flask, socketio: SocketIO):
        self.app = app
        self.socketio = socketio
        self.sessions = {}  # Store active terminal sessions
        self.setup_routes()
    
    def setup_routes(self):
        """Setup SocketIO event handlers"""
        
        @self.socketio.on('connect', namespace='/ws/terminal')
        def handle_connect():
            """Handle new terminal connection"""
            try:
                logger.info("Terminal client connecting...")
                
                # Clean up any stale sessions first
                self._cleanup_stale_sessions()
                
                # Clean up welcome file for new session
                welcome_file = os.path.join(TERMINAL_HOME, '.welcome_shown')
                try:
                    if os.path.exists(welcome_file):
                        os.remove(welcome_file)
                except:
                    pass
                
                # Clean up any stale lock files
                import glob
                lock_files = glob.glob(os.path.join(TERMINAL_HOME, '.bashrc_lock_*'))
                for lock_file in lock_files:
                    try:
                        os.remove(lock_file)
                    except:
                        pass
                
                # Create new session
                session_id = self._create_session()
                logger.info(f"Created terminal session {session_id}, emitting connected event")
                
                # Emit connected event immediately
                emit('connected', {'session_id': session_id})
                logger.info(f"Emitted 'connected' event for session {session_id}")
            except Exception as e:
                logger.error(f"Error creating terminal session on connect: {e}", exc_info=True)
                try:
                    emit('error', {'message': f'Failed to create terminal session: {str(e)}'})
                except:
                    pass
        
        @self.socketio.on('disconnect', namespace='/ws/terminal')
        def handle_disconnect():
            """Handle terminal disconnection"""
            # Find and cleanup session
            session_id = None
            for sid, session in self.sessions.items():
                if session.get('fd'):
                    session_id = sid
                    break
            
            if session_id:
                self._cleanup_session(session_id)
                logger.info(f"Terminal session {session_id} disconnected")
        
        @self.socketio.on('input', namespace='/ws/terminal')
        def handle_input(data):
            """Handle terminal input"""
            try:
                # Extract input data
                if isinstance(data, dict):
                    input_data = data.get('data', '')
                    session_id = data.get('session_id')
                else:
                    input_data = str(data)
                    session_id = None
                
                # Find the correct session
                if session_id and session_id in self.sessions:
                    session = self.sessions[session_id]
                else:
                    # Fallback: find first active session
                    session = None
                    for sid, s in self.sessions.items():
                        if s.get('fd') and s.get('process') and s['process'].poll() is None:
                            session = s
                            break
                
                if session and session.get('fd'):
                    try:
                        # Check if process is still alive
                        if session.get('process') and session['process'].poll() is not None:
                            logger.warning(f"Terminal process for session {session_id} has terminated")
                            emit('error', {'message': 'Terminal session has ended'})
                            return
                        
                        # Write input to PTY
                        if isinstance(input_data, str):
                            input_bytes = input_data.encode('utf-8')
                        else:
                            input_bytes = input_data
                        
                        written = os.write(session['fd'], input_bytes)
                        logger.debug(f"Wrote {written} bytes to terminal session {session_id}")
                    except OSError as e:
                        logger.error(f"Error writing to terminal: {e}")
                        # Don't emit error - it might cause client to reconnect
                    except Exception as e:
                        logger.error(f"Unexpected error writing to terminal: {e}", exc_info=True)
                        # Don't emit error - it might cause client to reconnect
                else:
                    logger.warning(f"No active terminal session found for input (session_id: {session_id})")
                    # Don't emit error - it might cause client to reconnect
            except Exception as e:
                logger.error(f"Error handling input: {e}", exc_info=True)
                emit('error', {'message': str(e)})
        
        @self.socketio.on('resize', namespace='/ws/terminal')
        def handle_resize(data):
            """Handle terminal resize"""
            try:
                cols = data.get('cols', 80)
                rows = data.get('rows', 24)
                
                # Find active session
                for session_id, session in self.sessions.items():
                    if session.get('fd'):
                        # Set terminal size
                        fcntl.ioctl(
                            session['fd'],
                            termios.TIOCSWINSZ,
                            struct.pack('HHHH', rows, cols, 0, 0)
                        )
                        break
            except Exception as e:
                logger.error(f"Error resizing terminal: {e}")
    
    def _create_session(self) -> str:
        """Create a new terminal session with restricted user permissions"""
        import uuid
        session_id = str(uuid.uuid4())
        
        try:
            # Ensure terminal user exists and setup home directory
            self._setup_terminal_user()
            
            # Create pseudo-terminal with proper settings
            master_fd, slave_fd = pty.openpty()
            
            # Set terminal attributes for proper operation
            try:
                # Get current terminal attributes
                attrs = termios.tcgetattr(master_fd)
                
                # Configure for interactive shell
                attrs[0] |= termios.IGNBRK  # Ignore break condition
                attrs[3] |= termios.ICANON | termios.ECHO | termios.ISIG  # Canonical mode, echo, signals
                attrs[6][termios.VMIN] = 1  # Minimum characters for read
                attrs[6][termios.VTIME] = 0  # Timeout
                
                # Set terminal attributes
                termios.tcsetattr(master_fd, termios.TCSANOW, attrs)
                termios.tcsetattr(slave_fd, termios.TCSANOW, attrs)
            except Exception as e:
                logger.debug(f"Could not set terminal attributes: {e}")
            
            # Set terminal size
            rows, cols = 24, 80
            try:
                fcntl.ioctl(
                    master_fd,
                    termios.TIOCSWINSZ,
                    struct.pack('HHHH', rows, cols, 0, 0)
                )
                fcntl.ioctl(
                    slave_fd,
                    termios.TIOCSWINSZ,
                    struct.pack('HHHH', rows, cols, 0, 0)
                )
            except Exception as e:
                logger.warning(f"Could not set terminal size: {e}")
            
            # Prepare environment for non-root user
            env = self._get_restricted_env()
            env['TERM'] = 'xterm-256color'
            env['COLUMNS'] = str(cols)
            env['LINES'] = str(rows)
            env['BASH_SILENCE_DEPRECATION_WARNING'] = '1'  # Suppress bash warnings
            env['DEBIAN_FRONTEND'] = 'noninteractive'  # Prevent interactive prompts
            env['TERMINAL_WELCOME_SHOWN'] = ''  # Reset welcome flag for new session
            
            # Start shell process as non-root user
            # Use preexec_fn to drop privileges before exec
            def preexec_fn():
                """Drop privileges to non-root user and setup terminal"""
                try:
                    # DON'T call os.setsid() - it causes "cannot set terminal process group" errors
                    # PTY doesn't support proper job control, so we skip session creation
                    
                    # Set supplementary groups
                    os.setgroups([])
                    
                    # Set GID
                    os.setgid(TERMINAL_GID)
                    
                    # Set UID (must be last)
                    os.setuid(TERMINAL_UID)
                    
                    # Change to home directory
                    os.chdir(TERMINAL_HOME)
                    
                    # Set umask for security
                    os.umask(0o027)  # Restrict file permissions
                    
                except Exception as e:
                    logger.error(f"Error in preexec_fn: {e}")
                    raise
            
            # Use bash directly with --rcfile - simplest and most reliable approach
            # The --rcfile flag ensures .bashrc is sourced once
            shell_cmd = [RESTRICTED_SHELL, '--rcfile', f'{TERMINAL_HOME}/.bashrc', '-i']
            
            # Use stderr=slave_fd but redirect job control errors to /dev/null in bash
            # We'll use bash's built-in error suppression instead of filtering
            process = subprocess.Popen(
                shell_cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,  # Send stderr to same PTY so prompts work
                env=env,
                preexec_fn=preexec_fn,
                start_new_session=False,  # Don't create new session (causes job control issues)
                cwd=TERMINAL_HOME
            )
            
            # Close slave_fd in parent process
            os.close(slave_fd)
            
            # Store session
            self.sessions[session_id] = {
                'fd': master_fd,
                'process': process,
                'user': TERMINAL_USER,
                'uid': TERMINAL_UID
            }
            
            # Start reading output in background
            self._start_output_reader(session_id, master_fd)
            
            logger.info(f"Created terminal session {session_id} for user {TERMINAL_USER} (UID: {TERMINAL_UID})")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating terminal session: {e}", exc_info=True)
            raise
    
    def _setup_terminal_user(self):
        """Setup terminal user if it doesn't exist"""
        try:
            # Try to get user info
            try:
                pwd.getpwnam(TERMINAL_USER)
                logger.debug(f"Terminal user {TERMINAL_USER} already exists")
            except KeyError:
                # User doesn't exist, create it
                logger.info(f"Creating terminal user {TERMINAL_USER}")
                
                # Create home directory
                os.makedirs(TERMINAL_HOME, mode=0o755, exist_ok=True)
                
                # Create user (requires root)
                subprocess.run([
                    'useradd',
                    '-m',
                    '-d', TERMINAL_HOME,
                    '-s', RESTRICTED_SHELL,
                    '-u', str(TERMINAL_UID),
                    '-g', str(TERMINAL_GID),
                    TERMINAL_USER
                ], check=False)  # Don't fail if user already exists
                
                # Set ownership
                os.chown(TERMINAL_HOME, TERMINAL_UID, TERMINAL_GID)
                
                # Create basic .bashrc with restrictions
                bashrc_path = os.path.join(TERMINAL_HOME, '.bashrc')
                if not os.path.exists(bashrc_path):
                    with open(bashrc_path, 'w') as f:
                        f.write(self._get_restricted_bashrc())
                    os.chown(bashrc_path, TERMINAL_UID, TERMINAL_GID)
                    os.chmod(bashrc_path, 0o644)
                
                logger.info(f"Terminal user {TERMINAL_USER} created")
        
        except PermissionError:
            logger.warning(f"Cannot create user {TERMINAL_USER} - not running as root. Using existing user.")
        except Exception as e:
            logger.warning(f"Error setting up terminal user: {e}")
    
    def _get_restricted_env(self) -> dict:
        """Get restricted environment variables for terminal user"""
        env = os.environ.copy()
        
        # Basic environment
        env['TERM'] = 'xterm-256color'
        env['HOME'] = TERMINAL_HOME
        env['USER'] = TERMINAL_USER
        env['LOGNAME'] = TERMINAL_USER
        env['SHELL'] = RESTRICTED_SHELL
        
        # Restricted PATH - only essential directories
        env['PATH'] = '/usr/local/bin:/usr/bin:/bin'
        
        # Remove dangerous environment variables
        dangerous_vars = [
            'SUDO_USER', 'SUDO_UID', 'SUDO_GID',
            'SSH_AUTH_SOCK', 'SSH_CONNECTION',
            'DOCKER_HOST', 'KUBECONFIG'
        ]
        for var in dangerous_vars:
            env.pop(var, None)
        
        return env
    
    def _get_restricted_bashrc(self) -> str:
        """Get restricted .bashrc content"""
        return """# Restricted bashrc for terminal user
# Limited functionality for security

# Basic prompt
export PS1='\\u@\\h:\\w\\$ '

# History settings
export HISTSIZE=1000
export HISTFILESIZE=2000
export HISTCONTROL=ignoredups

# Aliases (safe ones only)
alias ll='ls -lh'
alias la='ls -lah'
alias ..='cd ..'
alias ...='cd ../..'

# Prevent dangerous commands
alias rm='rm -i'
alias mv='mv -i'
alias cp='cp -i'

# Welcome message
echo "Welcome to Home Assistant Platform Terminal"
echo "Running as restricted user: $(whoami)"
echo "Type 'help' for available commands"
echo ""
"""
    
    def _start_output_reader(self, session_id: str, fd: int):
        """Start reading terminal output in background thread"""
        import threading
        
        def read_output():
            try:
                while True:
                    if fd not in [s.get('fd') for s in self.sessions.values()]:
                        break
                    
                    # Check if data is available
                    ready, _, _ = select.select([fd], [], [], 0.1)
                    if ready:
                        try:
                            data = os.read(fd, 1024)
                            if data:
                                # Emit output to client
                                self.socketio.emit(
                                    'output',
                                    {'type': 'output', 'data': data.decode('utf-8', errors='replace')},
                                    namespace='/ws/terminal'
                                )
                        except OSError:
                            break
            except Exception as e:
                logger.error(f"Error reading terminal output: {e}")
            finally:
                self._cleanup_session(session_id)
        
        thread = threading.Thread(target=read_output, daemon=True)
        thread.start()
    
    def _cleanup_session(self, session_id: str):
        """Cleanup terminal session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            if session.get('fd'):
                try:
                    os.close(session['fd'])
                except:
                    pass
            
            if session.get('process'):
                try:
                    session['process'].terminate()
                    session['process'].wait(timeout=2)
                except:
                    try:
                        session['process'].kill()
                    except:
                        pass
            
            del self.sessions[session_id]
    
    def _cleanup_stale_sessions(self):
        """Clean up stale/terminated sessions"""
        stale_sessions = []
        for session_id, session in list(self.sessions.items()):
            if session.get('process'):
                if session['process'].poll() is not None:
                    stale_sessions.append(session_id)
        
        for session_id in stale_sessions:
            logger.debug(f"Cleaning up stale session {session_id}")
            self._cleanup_session(session_id)

