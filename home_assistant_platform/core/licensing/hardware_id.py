"""Hardware ID generation for licensing"""

import hashlib
import subprocess
import logging
from pathlib import Path
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)


def get_raspberry_pi_serial() -> str:
    """Get Raspberry Pi serial number"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if line.startswith('Serial'):
                    return line.split(':')[1].strip()
    except Exception as e:
        logger.warning(f"Failed to read CPU serial: {e}")
    
    # Fallback: use machine-id
    try:
        with open('/etc/machine-id', 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.warning(f"Failed to read machine-id: {e}")
    
    # Last resort: use hostname
    import socket
    return socket.gethostname()


def generate_hardware_id() -> str:
    """Generate a unique hardware ID based on Raspberry Pi serial"""
    serial = get_raspberry_pi_serial()
    # Create a hash of the serial for privacy
    hardware_id = hashlib.sha256(serial.encode()).hexdigest()[:16]
    return hardware_id


def get_or_create_hardware_id() -> str:
    """Get existing hardware ID or create and save a new one"""
    hardware_id_file = settings.data_dir / "hardware_id.txt"
    
    if hardware_id_file.exists():
        try:
            with open(hardware_id_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.warning(f"Failed to read hardware ID: {e}")
    
    # Generate new hardware ID
    hardware_id = generate_hardware_id()
    
    try:
        with open(hardware_id_file, 'w') as f:
            f.write(hardware_id)
        logger.info(f"Generated new hardware ID: {hardware_id}")
    except Exception as e:
        logger.error(f"Failed to save hardware ID: {e}")
    
    return hardware_id

