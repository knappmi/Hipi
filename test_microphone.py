#!/usr/bin/env python3
"""Test script to verify microphone input is working"""

import pyaudio
import time
import sys

def test_microphone():
    """Test microphone input"""
    p = pyaudio.PyAudio()
    
    # Find PulseAudio device
    input_device_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            if 'pulse' in info['name'].lower():
                input_device_index = i
                print(f"Using device {i}: {info['name']}")
                break
            elif input_device_index is None:
                input_device_index = i
                print(f"Using device {i}: {info['name']}")
    
    if input_device_index is None:
        print("ERROR: No input device found")
        return False
    
    try:
        print(f"Opening stream on device {input_device_index}...")
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=1024
        )
        
        print("Stream opened successfully!")
        print("Listening for 5 seconds... (speak into microphone)")
        
        frames_read = 0
        for _ in range(50):  # 5 seconds at 100ms intervals
            try:
                data = stream.read(1024, exception_on_overflow=False)
                frames_read += 1
                # Check if we're getting actual audio (not just silence)
                audio_level = max(abs(int.from_bytes(data[i:i+2], byteorder='little', signed=True)) 
                                 for i in range(0, min(1024, len(data)), 2))
                if audio_level > 100:  # Threshold for detecting sound
                    print(f"✓ Audio detected! Level: {audio_level}")
            except Exception as e:
                print(f"Error reading: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        print(f"Test complete. Read {frames_read} frames.")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        p.terminate()

if __name__ == "__main__":
    success = test_microphone()
    sys.exit(0 if success else 1)



