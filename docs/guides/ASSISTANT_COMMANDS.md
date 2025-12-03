# Assistant Commands Guide

Your assistant now supports basic commands! Just say **"Hi Pie"** followed by your question.

## Available Commands

### ⏰ Time & Date
- **"Hi Pie what time is it?"** - Get current time
- **"Hi Pie what's the time?"** - Get current time
- **"Hi Pie what date is it?"** - Get current date
- **"Hi Pie what's the date?"** - Get current date

### 😂 Entertainment
- **"Hi Pie tell me a joke"** - Get a random joke
- **"Hi Pie joke"** - Get a random joke
- **"Hi Pie make me laugh"** - Get a random joke

### 🌤️ Weather
- **"Hi Pie what's the weather?"** - Get weather (requires API setup)
- **"Hi Pie weather in New York"** - Get weather for location
- **"Hi Pie temperature"** - Get temperature

### ⏰ Alarms
- **"Hi Pie set alarm for 3 PM"** - Set an alarm
- **"Hi Pie alarm for 7:30 AM"** - Set an alarm
- **"Hi Pie list alarms"** - Show all alarms
- **"Hi Pie what alarms do I have?"** - Show all alarms

### 🧮 Calculator
- **"Hi Pie what is 5 plus 3?"** - Simple math (coming soon)
- **"Hi Pie calculate 10 times 2"** - Simple math (coming soon)

### ❓ Help
- **"Hi Pie help"** - Get list of available commands
- **"Hi Pie what can you do?"** - Get list of available commands

## Example Usage

1. **Get the time:**
   - You: "Hi Pie what time is it?"
   - Assistant: "The time is 3:45 PM"

2. **Get a joke:**
   - You: "Hi Pie tell me a joke"
   - Assistant: "Why don't scientists trust atoms? Because they make up everything!"

3. **Get the date:**
   - You: "Hi Pie what's the date?"
   - Assistant: "Today is Monday, November 17, 2025"

## Tips

- Speak clearly and wait for the beep after saying "Hi Pie"
- The assistant will respond with both a beep and spoken response
- If the assistant doesn't understand, try rephrasing your question
- Say "help" to see all available commands

## Coming Soon

- Full calculator functionality
- Weather API integration
- Alarm scheduling and notifications
- More jokes and entertainment
- News updates
- Reminders

## Troubleshooting

If commands aren't working:
1. Make sure you said the wake word first ("Hi Pie")
2. Check logs: `sudo docker compose logs -f platform | grep -E "Intent|Assistant"`
3. Try speaking more clearly
4. Check that the wake word is set correctly in Voice Settings



