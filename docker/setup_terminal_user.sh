#!/bin/bash
# Setup restricted terminal user

TERMINAL_USER="${TERMINAL_USER:-hapuser}"
TERMINAL_UID="${TERMINAL_UID:-1001}"
TERMINAL_GID="${TERMINAL_GID:-1001}"
TERMINAL_HOME="${TERMINAL_HOME:-/app/home}"
RESTRICTED_SHELL="${RESTRICTED_SHELL:-/bin/bash}"

echo "Setting up terminal user: $TERMINAL_USER"

# Create group if it doesn't exist
if ! getent group $TERMINAL_GID > /dev/null 2>&1; then
    groupadd -g $TERMINAL_GID $TERMINAL_USER 2>/dev/null || true
fi

# Create user if it doesn't exist
if ! id -u $TERMINAL_USER > /dev/null 2>&1; then
    useradd -m -d $TERMINAL_HOME -s $RESTRICTED_SHELL -u $TERMINAL_UID -g $TERMINAL_GID $TERMINAL_USER
    echo "Created user $TERMINAL_USER"
else
    echo "User $TERMINAL_USER already exists"
fi

# Create and setup home directory
mkdir -p $TERMINAL_HOME
chown $TERMINAL_UID:$TERMINAL_GID $TERMINAL_HOME
chmod 755 $TERMINAL_HOME

# Create restricted .bashrc
cat > $TERMINAL_HOME/.bashrc << 'EOF'
# Restricted bashrc for terminal user
# Only source if running interactively
[ -z "$PS1" ] && return

# Prevent multiple sourcing - use a lock file approach
LOCK_FILE="$HOME/.bashrc_lock_$$"
if [ -f "$LOCK_FILE" ]; then
    return
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE 2>/dev/null" EXIT

# Suppress ALL job control and terminal errors
# Redirect stderr to /dev/null for job control commands
(set +m) 2>/dev/null || true

# Set prompt
export PS1='\u@\h:\w\$ '

# History settings
export HISTSIZE=1000
export HISTFILESIZE=2000
export HISTCONTROL=ignoredups

# Terminal settings
export TERM=xterm-256color

# Safe aliases
alias ll='ls -lh'
alias la='ls -lah'
alias ..='cd ..'
alias ...='cd ../..'
alias rm='rm -i'
alias mv='mv -i'
alias cp='cp -i'

# Welcome message (only show once using a persistent flag)
WELCOME_FILE="$HOME/.welcome_shown"
if [ ! -f "$WELCOME_FILE" ]; then
    echo "Welcome to Home Assistant Platform Terminal"
    echo "Running as restricted user: $(whoami)"
    echo "Type 'help' for available commands"
    echo ""
    touch "$WELCOME_FILE"
fi
EOF

chown $TERMINAL_UID:$TERMINAL_GID $TERMINAL_HOME/.bashrc
chmod 644 $TERMINAL_HOME/.bashrc

# Create restricted .bash_profile (don't source .bashrc to prevent double sourcing)
cat > $TERMINAL_HOME/.bash_profile << 'EOF'
# Restricted bash_profile - minimal setup
# Don't source .bashrc here to prevent double sourcing when using --rcfile
[ -z "$PS1" ] && return

# Set prompt if not already set
[ -z "$PS1" ] || export PS1='\u@\h:\w\$ '
EOF

chown $TERMINAL_UID:$TERMINAL_GID $TERMINAL_HOME/.bash_profile
chmod 644 $TERMINAL_HOME/.bash_profile

# Set up restricted directories
mkdir -p $TERMINAL_HOME/bin
chown $TERMINAL_UID:$TERMINAL_GID $TERMINAL_HOME/bin
chmod 755 $TERMINAL_HOME/bin

# Create a help command
cat > $TERMINAL_HOME/bin/help << 'EOF'
#!/bin/bash
echo "Home Assistant Platform Terminal Help"
echo ""
echo "Available commands:"
echo "  hap              - Platform CLI tool"
echo "  ls, cd, pwd      - File navigation"
echo "  cat, less        - View files"
echo "  echo             - Print text"
echo ""
echo "Restrictions:"
echo "  - Limited PATH"
echo "  - No sudo access"
echo "  - Restricted file permissions"
echo ""
EOF

chmod +x $TERMINAL_HOME/bin/help
chown $TERMINAL_UID:$TERMINAL_GID $TERMINAL_HOME/bin/help

# Add bin to PATH in bashrc
echo 'export PATH="$HOME/bin:$PATH"' >> $TERMINAL_HOME/.bashrc

echo "Terminal user setup complete"
echo "User: $TERMINAL_USER (UID: $TERMINAL_UID, GID: $TERMINAL_GID)"
echo "Home: $TERMINAL_HOME"

