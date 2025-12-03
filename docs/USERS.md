# Multi-User System

## User Management
- User registration with password hashing
- Authentication with bcrypt
- Session management with secure tokens
- User profiles (display names, preferences)

## Voice Recognition
- Voice profile creation
- Voice feature extraction (MFCC)
- User identification by voice
- Training status tracking

## User Preferences
- Per-user language settings
- Per-user timezone
- Per-user voice preferences
- Extensible preference system

## Data Isolation
- All data is user-scoped
- Devices, automations, scenes, reminders per user
- Session-based access control

## Voice Commands
- "Who am I"
- "Switch user to John"
- "I am John"

**API**: `/api/v1/users/*`

See [MULTI_USER_SYSTEM.md](../MULTI_USER_SYSTEM.md) for details.

