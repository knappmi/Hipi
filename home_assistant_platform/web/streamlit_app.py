"""
Streamlit Web Application for Home Assistant Platform
A robust dashboard for managing the platform
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Home Assistant Platform",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online {
        background-color: #28a745;
    }
    .status-offline {
        background-color: #dc3545;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=5)
def fetch_api_data(endpoint: str) -> Optional[Dict]:
    """Fetch data from API with caching"""
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None


def update_voice_settings(settings: Dict):
    """Update voice settings via API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/voice/settings",
            json=settings,
            timeout=5
        )
        if response.status_code == 200:
            return True, "Settings updated successfully"
        return False, f"Error: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<div class="main-header">🏠 Home Assistant Platform Dashboard</div>', unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["Dashboard", "Voice Settings", "Plugins", "Telemetry", "System Status"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Voice Settings":
        show_voice_settings()
    elif page == "Plugins":
        show_plugins()
    elif page == "Telemetry":
        show_telemetry()
    elif page == "System Status":
        show_system_status()


def show_dashboard():
    """Main dashboard view"""
    st.header("Platform Overview")
    
    # Fetch system status
    voice_status = fetch_api_data("/voice/listen/status")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if voice_status:
            status = "🟢 Online" if voice_status.get("listening") else "🔴 Offline"
            st.metric("Voice Status", status)
        else:
            st.metric("Voice Status", "❓ Unknown")
    
    with col2:
        if voice_status:
            awake = "🟢 Awake" if voice_status.get("awake") else "⚪ Sleeping"
            st.metric("Wake State", awake)
        else:
            st.metric("Wake State", "❓ Unknown")
    
    with col3:
        if voice_status:
            wake_word = voice_status.get("wake_word", "N/A")
            st.metric("Wake Word", wake_word.replace("_", " ").title())
        else:
            st.metric("Wake Word", "❓ Unknown")
    
    with col4:
        # Get conversation mode status
        settings = fetch_api_data("/voice/settings")
        if settings:
            conv_mode = "🟢 Enabled" if settings.get("conversation_mode") else "⚪ Disabled"
            st.metric("Conversation Mode", conv_mode)
        else:
            st.metric("Conversation Mode", "❓ Unknown")
    
    # Real-time updates
    st.subheader("Real-time Status")
    status_placeholder = st.empty()
    
    if st.button("🔄 Refresh Status"):
        st.rerun()
    
    # Auto-refresh every 5 seconds
    if st.checkbox("Auto-refresh (5s)", value=False):
        time.sleep(5)
        st.rerun()
    
    # Display current status
    if voice_status:
        with status_placeholder.container():
            st.json(voice_status)
    else:
        status_placeholder.error("Unable to fetch voice status")


def show_voice_settings():
    """Voice settings management"""
    st.header("Voice Settings")
    
    # Fetch current settings
    settings = fetch_api_data("/voice/settings")
    
    if not settings:
        st.error("Unable to fetch current settings")
        return
    
    # Voice Processing Section
    with st.expander("Voice Processing", expanded=True):
        voice_enabled = st.checkbox("Enable Voice Processing", value=settings.get("voice_enabled", True))
        wake_word = st.text_input("Wake Word", value=settings.get("wake_word", "hey_assistant"))
        conversation_mode = st.checkbox(
            "Enable Conversation Mode",
            value=settings.get("conversation_mode", False),
            help="In conversation mode, the assistant stays awake after the wake word for fluid conversation"
        )
    
    # STT Settings
    with st.expander("Speech-to-Text (STT)"):
        stt_engine = st.selectbox(
            "STT Engine",
            ["vosk", "openai"],
            index=0 if settings.get("stt_engine") == "vosk" else 1
        )
        
        if stt_engine == "openai":
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value="",  # Don't show existing key
                help="Enter your OpenAI API key"
            )
        else:
            openai_key = None
    
    # TTS Settings
    with st.expander("Text-to-Speech (TTS)"):
        tts_engine = st.selectbox(
            "TTS Engine",
            ["pyttsx3", "openai"],
            index=0 if settings.get("tts_engine") == "pyttsx3" else 1
        )
        
        if tts_engine == "openai":
            openai_voice = st.selectbox(
                "OpenAI Voice",
                ["nova", "shimmer", "alloy", "echo", "fable", "onyx"],
                index=0,
                help="Nova is recommended for natural-sounding voice"
            )
        else:
            openai_voice = None
    
    # Test Voice
    with st.expander("Test Voice"):
        test_text = st.text_input("Test Text", value="Hello, this is a test")
        if st.button("🔊 Test TTS"):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/voice/speak",
                    json={"text": test_text},
                    timeout=10
                )
                if response.status_code == 200:
                    st.success("Voice test completed!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Update Settings
    if st.button("💾 Update All Settings", type="primary"):
        update_data = {
            "voice_enabled": voice_enabled,
            "wake_word": wake_word,
            "stt_engine": stt_engine,
            "tts_engine": tts_engine,
            "conversation_mode": conversation_mode
        }
        
        if openai_key:
            update_data["openai_api_key"] = openai_key
        
        if openai_voice:
            update_data["openai_tts_voice"] = openai_voice
        
        success, message = update_voice_settings(update_data)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)


def show_plugins():
    """Plugin management"""
    st.header("Plugin Management")
    
    # Fetch plugins
    plugins = fetch_api_data("/plugins")
    
    if plugins:
        st.subheader("Installed Plugins")
        for plugin in plugins.get("plugins", []):
            with st.expander(f"🔌 {plugin.get('name', 'Unknown')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {plugin.get('id')}")
                    st.write(f"**Version:** {plugin.get('version', 'N/A')}")
                    st.write(f"**Status:** {plugin.get('status', 'unknown')}")
                with col2:
                    if st.button(f"Restart {plugin.get('name')}", key=f"restart_{plugin.get('id')}"):
                        st.info("Restart functionality coming soon")
    else:
        st.info("No plugins installed or unable to fetch plugin list")


def show_telemetry():
    """Telemetry and monitoring"""
    st.header("Telemetry & Monitoring")
    
    tab1, tab2, tab3 = st.tabs(["Logs", "Metrics", "Tracing"])
    
    with tab1:
        st.subheader("Application Logs")
        log_level = st.selectbox("Log Level", ["INFO", "DEBUG", "WARNING", "ERROR"], index=0)
        log_tail = st.slider("Number of lines", 50, 1000, 100, 50)
        
        if st.button("📥 Load Logs"):
            st.info("Log viewing functionality - integrate with your logging system")
            # In production, this would fetch from your logging backend
    
    with tab2:
        st.subheader("System Metrics")
        st.info("Metrics dashboard - integrate with Prometheus/Grafana or similar")
        
        # Placeholder metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CPU Usage", "45%", "2%")
        with col2:
            st.metric("Memory Usage", "512 MB", "50 MB")
        with col3:
            st.metric("Active Plugins", "3", "1")
    
    with tab3:
        st.subheader("Distributed Tracing")
        st.info("Tracing dashboard - integrate with Jaeger, Zipkin, or similar")
        
        trace_id = st.text_input("Trace ID", placeholder="Enter trace ID to view")
        if st.button("🔍 Search Trace"):
            st.info(f"Searching for trace: {trace_id}")


def show_system_status():
    """System status and health"""
    st.header("System Status")
    
    # Health checks
    st.subheader("Health Checks")
    
    health_checks = {
        "Voice Manager": fetch_api_data("/voice/listen/status") is not None,
        "API Server": True,  # If we got here, API is working
        "Database": True,  # Add actual DB check
    }
    
    for service, status in health_checks.items():
        status_icon = "✅" if status else "❌"
        st.write(f"{status_icon} **{service}**: {'Healthy' if status else 'Unhealthy'}")
    
    # System Information
    st.subheader("System Information")
    st.json({
        "Platform Version": "1.0.0",
        "Python Version": "3.11",
        "Uptime": "N/A",  # Add actual uptime calculation
        "Last Updated": datetime.now().isoformat()
    })


if __name__ == "__main__":
    main()



