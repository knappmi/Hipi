# Multi-User Support System

A comprehensive multi-user system with authentication, voice recognition, user profiles, and data isolation.

## ✅ Implemented Features

### 1. User Management
- **User Registration**: Create new user accounts
- **Authentication**: Password-based authentication
- **Session Management**: Token-based sessions
- **User Profiles**: Display names, preferences, avatars
- **User Switching**: Switch between users

### 2. Voice Recognition
- **Voice Profiles**: Train voice recognition models
- **User Identification**: Identify users by voice
- **Voice Samples**: Collect and store voice samples
- **Training Status**: Track training progress

### 3. User Preferences
- **Language**: Per-user language settings
- **Timezone**: Per-user timezone
- **Voice Settings**: Per-user voice preferences
- **Custom Preferences**: Extensible preference system

### 4. Data Isolation
- **User-Specific Data**: All data is user-scoped
- **Device Isolation**: Devices per user
- **Automation Isolation**: Automations per user
- **Scene Isolation**: Scenes per user
- **Reminder Isolation**: Reminders per user

### 5. Voice Integration
- **User Tool**: Registered with voice agent
- **Voice Commands**: User management via voice
- **Intent Recognition**: User-related intents

## API Endpoints

### Authentication
- `POST /api/v1/users/register` - Register new user
- `POST /api/v1/users/login` - Login and create session
- `GET /api/v1/users/me` - Get current user info

### User Management
- `GET /api/v1/users/users` - List all users
- `POST /api/v1/users/switch` - Switch to different user
- `PUT /api/v1/users/preferences` - Update preferences

### Voice Recognition
- `POST /api/v1/users/voice/train` - Train voice model
- `POST /api/v1/users/voice/identify` - Identify user by voice
- `GET /api/v1/users/voice/status/{user_id}` - Get training status

## Voice Commands

### User Identification
- **"Who am I"**
- **"Who is this"**

### User Switching
- **"Switch user to John"**
- **"Change user to Alice"**
- **"I am John"**
- **"This is Alice"**

### User Listing
- **"List users"**

## Usage Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "pass123",
    "display_name": "John Doe",
    "email": "john@example.com"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "pass123"
  }'
```

### Switch User
```bash
curl -X POST http://localhost:8000/api/v1/users/switch?user_id=2 \
  -H "X-Session-Token: your_session_token"
```

### Update Preferences
```bash
curl -X PUT http://localhost:8000/api/v1/users/preferences \
  -H "X-Session-Token: your_session_token" \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "language": "en",
      "timezone": "America/New_York"
    }
  }'
```

## Database Models

- **User**: User accounts with authentication
- **UserSession**: Active user sessions
- **VoiceProfile**: Voice recognition profiles

## Architecture

```
Multi-User System
├── UserManager
│   ├── User CRUD
│   ├── Authentication
│   ├── Session management
│   └── Preferences
├── VoiceRecognition
│   ├── Feature extraction
│   ├── Model training
│   └── User identification
└── UserTool (Voice)
    ├── User switching
    └── User identification
```

## Security

- **Password Hashing**: Bcrypt with salt
- **Session Tokens**: Secure random tokens
- **Token Expiration**: 30-day expiration
- **Password Limits**: 72-byte limit for bcrypt

## Testing

Run the test script:
```bash
python3 test_multiuser.py
```

## Status

✅ **Fully Functional**
- User registration: ✅ Working
- Authentication: ✅ Working
- Session management: ✅ Working
- User switching: ✅ Working
- Voice commands: ✅ Working
- Preferences: ✅ Working
- Voice recognition: ✅ Ready (needs training)

## Future Enhancements

- OAuth integration
- Two-factor authentication
- Password reset
- User roles and permissions
- Family accounts
- Guest mode
- User activity logging
- Advanced voice recognition (ML models)
- Face recognition
- Biometric authentication

