# Calendar & Reminder System

A comprehensive calendar and reminder system with voice commands, recurring reminders, and calendar integration.

## ✅ Implemented Features

### 1. Calendar Management
- **Multiple Calendars**: Support for local, Google Calendar, and iCal calendars
- **Event Management**: Create, list, update, and delete events
- **Calendar Sync**: Sync events from iCal URLs
- **Upcoming Events**: Get events for next N days

### 2. Reminder System
- **Voice Commands**: Natural language reminder creation
- **Time Parsing**: Understands "at 3 PM", "in 30 minutes", "tomorrow at 10 AM"
- **Recurring Reminders**: Daily, weekly, monthly, yearly patterns
- **Reminder Notifications**: Voice notifications when reminders trigger
- **Reminder Management**: Complete, delete, list reminders

### 3. Natural Language Processing
- **Time Parsing**: Handles various time formats
  - "at 3 PM"
  - "in 30 minutes"
  - "tomorrow at 10 AM"
  - "daily at 8 AM"
- **Title Extraction**: Extracts reminder title from voice commands
- **Recurrence Detection**: Detects recurring patterns

### 4. Reminder Scheduler
- **Background Scheduler**: Checks reminders every minute
- **Voice Notifications**: Speaks reminders when they trigger
- **Notification Logging**: Tracks notification delivery

## API Endpoints

### Calendars
- `GET /api/v1/calendar/calendars` - List calendars
- `POST /api/v1/calendar/calendars` - Create calendar
- `POST /api/v1/calendar/calendars/{id}/sync` - Sync calendar

### Events
- `GET /api/v1/calendar/events` - List events
- `GET /api/v1/calendar/events/upcoming` - Get upcoming events
- `POST /api/v1/calendar/events` - Create event
- `DELETE /api/v1/calendar/events/{id}` - Delete event

### Reminders
- `GET /api/v1/calendar/reminders` - List reminders
- `GET /api/v1/calendar/reminders/upcoming` - Get upcoming reminders
- `POST /api/v1/calendar/reminders` - Create reminder
- `POST /api/v1/calendar/reminders/voice` - Create reminder from voice
- `POST /api/v1/calendar/reminders/{id}/complete` - Complete reminder
- `DELETE /api/v1/calendar/reminders/{id}` - Delete reminder

## Voice Commands

### Set Reminders
- **"Remind me to call mom at 3 PM"**
- **"Remind me to water plants daily at 8 AM"**
- **"Set reminder to exercise in 30 minutes"**
- **"Remind me to call the dentist tomorrow at 2 PM"**

### List Reminders
- **"List reminders"**
- **"What reminders do I have?"**
- **"Show my reminders"**

## Usage Examples

### Create Reminder via Voice
```bash
curl -X POST http://localhost:8000/api/v1/calendar/reminders/voice \
  -H "Content-Type: application/json" \
  -d '{"text": "remind me to call mom at 3 PM"}'
```

### Create Calendar Event
```bash
curl -X POST http://localhost:8000/api/v1/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "calendar_id": 1,
    "title": "Team Meeting",
    "start_time": "2025-12-04T14:00:00",
    "end_time": "2025-12-04T15:00:00",
    "description": "Weekly team sync"
  }'
```

### Get Upcoming Events
```bash
curl http://localhost:8000/api/v1/calendar/events/upcoming?days=7
```

## Recurrence Patterns

Supported recurrence types:
- **daily**: Every day
- **weekly**: Every week
- **monthly**: Every month
- **yearly**: Every year

Example: "remind me to water plants daily at 8 AM"

## Integration

### Voice Integration
The reminder tool is automatically registered with the voice agent:
- Voice commands are parsed and converted to reminders
- Reminders trigger voice notifications
- Natural language time parsing

### Automation Integration
- Reminders can trigger automations
- Calendar events can be used in automation conditions
- Event-based automations (coming soon)

## Architecture

```
Calendar & Reminder System
├── CalendarManager
│   ├── Calendar CRUD
│   ├── Event management
│   └── iCal sync
├── ReminderManager
│   ├── Reminder CRUD
│   ├── Natural language parsing
│   ├── Recurrence handling
│   └── Notification callbacks
└── ReminderScheduler
    ├── Background checking
    └── Notification triggering
```

## Database Models

- **Calendar**: Calendar sources (local, Google, iCal)
- **CalendarEvent**: Calendar events with recurrence
- **Reminder**: Reminders with recurrence patterns
- **ReminderNotification**: Notification log

## Testing

Run the test script:
```bash
python3 test_calendar_reminders.py
```

## Status

✅ **Fully Functional**
- Calendar management: ✅ Working
- Event management: ✅ Working
- Reminder creation: ✅ Working
- Voice commands: ✅ Working
- Natural language parsing: ✅ Working
- Recurring reminders: ✅ Working
- Reminder notifications: ✅ Working

## Future Enhancements

- Google Calendar OAuth integration
- Email notifications
- Push notifications
- Calendar event reminders
- Event conflict detection
- Calendar sharing
- Time zone support

