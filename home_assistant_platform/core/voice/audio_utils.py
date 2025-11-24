"""Audio utility functions"""

import subprocess
import logging
import tempfile
import os
import struct
import wave

logger = logging.getLogger(__name__)


def generate_beep_wav(frequency=800, duration=0.15, sample_rate=44100):
    """Generate a pleasant beep WAV file"""
    num_samples = int(sample_rate * duration)
    
    # Create a more pleasant beep with a fade in/out
    samples = []
    for i in range(num_samples):
        # Sine wave with fade in/out
        t = float(i) / sample_rate
        fade_in = min(1.0, t * 20)  # Quick fade in
        fade_out = min(1.0, (duration - t) * 20)  # Quick fade out
        fade = min(fade_in, fade_out)
        
        # Generate sine wave
        value = int(32767 * 0.3 * fade * struct.unpack('>f', struct.pack('>f', 2.0 * 3.14159 * frequency * t))[0])
        samples.append(struct.pack('<h', value))
    
    # Create WAV file in memory
    wav_data = b''
    wav_data += b'RIFF'
    wav_data += struct.pack('<I', 36 + len(b''.join(samples)))
    wav_data += b'WAVE'
    wav_data += b'fmt '
    wav_data += struct.pack('<I', 16)  # fmt chunk size
    wav_data += struct.pack('<H', 1)   # audio format (PCM)
    wav_data += struct.pack('<H', 1)   # num channels
    wav_data += struct.pack('<I', sample_rate)  # sample rate
    wav_data += struct.pack('<I', sample_rate * 2)  # byte rate
    wav_data += struct.pack('<H', 2)   # block align
    wav_data += struct.pack('<H', 16)  # bits per sample
    wav_data += b'data'
    wav_data += struct.pack('<I', len(b''.join(samples)))
    wav_data += b''.join(samples)
    
    return wav_data


def play_beep(frequency=800, duration=0.15):
    """Play a pleasant beep sound"""
    try:
        # Generate a nice beep WAV file
        wav_data = generate_beep_wav(frequency, duration)
        
        # Save to temp file and play
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(wav_data)
            tmp_path = tmp_file.name
        
        try:
            # Try aplay first (most reliable on Linux)
            subprocess.run(
                ['aplay', '-q', tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=1
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            try:
                # Fallback to paplay (PulseAudio)
                subprocess.run(
                    ['paplay', tmp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=1
                )
            except (FileNotFoundError, subprocess.TimeoutExpired):
                try:
                    # Last resort: use sox if available
                    subprocess.run(
                        ['play', '-q', tmp_path],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=1
                    )
                except:
                    logger.debug("Could not play beep sound - no audio player available")
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    except Exception as e:
        logger.debug(f"Beep error: {e}")


def play_acknowledgment():
    """Play a pleasant acknowledgment sound (two-tone chime)"""
    try:
        # Play a pleasant two-tone chime (like a notification)
        # First tone: 880Hz (A5)
        play_beep(frequency=880, duration=0.08)
        
        # Small pause
        import time
        time.sleep(0.02)
        
        # Second tone: 1108Hz (C#6) - pleasant interval
        play_beep(frequency=1108, duration=0.12)
        
        logger.debug("Acknowledgment chime played")
    except Exception as e:
        try:
            # Fallback to simple beep
            play_beep(frequency=800, duration=0.15)
        except:
            logger.debug(f"Could not play acknowledgment: {e}")
