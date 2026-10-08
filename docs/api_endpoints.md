# AgriGenius AI - REST API Endpoint Specifications

All endpoints are versioned and follow RESTful naming conventions. The API base URL is `/api/v1`.

---

## 1. Authentication Endpoints (`/auth`)

### POST `/auth/register`
Creates a new user account.
- **Request Body**:
  ```json
  {
    "email": "farmer@example.com",
    "password": "strongpassword123",
    "roles": ["farmer"]
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-user-string",
    "email": "farmer@example.com",
    "roles": ["farmer"],
    "is_active": true,
    "created_at": "2026-07-15T12:00:00Z"
  }
  ```

### POST `/auth/login`
Authenticates user and returns access + refresh tokens.
- **Request Body**:
  ```json
  {
    "email": "farmer@example.com",
    "password": "strongpassword123"
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "access_token": "jwt.access.token",
    "refresh_token": "jwt.refresh.token",
    "token_type": "bearer"
  }
  ```

### POST `/auth/refresh`
Refreshes access tokens.
- **Request Query Parameter**: `refresh_token` (JWT String)
- **Response** (200 OK):
  ```json
  {
    "access_token": "new.jwt.access.token",
    "refresh_token": "new.jwt.refresh.token",
    "token_type": "bearer"
  }
  ```

### GET `/auth/me`
Fetches authenticated user data.
- **Headers**: `Authorization: Bearer <access_token>`
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-user-string",
    "email": "farmer@example.com",
    "roles": ["farmer"],
    "is_active": true,
    "created_at": "2026-07-15T12:00:00Z"
  }
  ```

---

## 2. Profile Management (`/users`)

### POST `/users/profiles`
Configures a farm profile.
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "fullname": "John Doe",
    "phone": "+1234567890",
    "location": "Central Valley, California",
    "farm_size_hectares": 12.5,
    "primary_crops": ["Almonds", "Grapes"],
    "soil_profile": {
      "nitrogen": 45.2,
      "phosphorus": 22.1,
      "potassium": 120.5,
      "ph": 6.8,
      "moisture": 40.0
    }
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-profile-string",
    "user_id": "uuid-user-string",
    "fullname": "John Doe",
    "phone": "+1234567890",
    "location": "Central Valley, California",
    "farm_size_hectares": 12.5,
    "primary_crops": ["Almonds", "Grapes"],
    "soil_profile": {
      "nitrogen": 45.2,
      "phosphorus": 22.1,
      "potassium": 120.5,
      "ph": 6.8,
      "moisture": 40.0
    }
  }
  ```

### GET `/users/profiles/me`
Retrieves logged in user's profile.
- **Headers**: `Authorization: Bearer <access_token>`
- **Response** (200 OK): Same structure as profiles schema.

### PUT `/users/profiles/me`
Modifies farmer profile metrics.
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**: Partial parameters schema matching profiles values.
- **Response** (200 OK): Updated profiles object.

---

## 3. Chat & AI Assistant (`/chats`)

### POST `/chats`
Creates a new discussion thread.
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "title": "Soil analysis inquiry"
  }
  ```
- **Response** (201 Created):
  ```json
  {
    "id": "uuid-chat-string",
    "user_id": "uuid-user-string",
    "title": "Soil analysis inquiry",
    "created_at": "2026-07-15T12:05:00Z",
    "updated_at": "2026-07-15T12:05:00Z"
  }
  ```

### GET `/chats`
Lists user discussion history.
- **Headers**: `Authorization: Bearer <access_token>`
- **Response** (200 OK): List of chat objects.

### GET `/chats/{chat_id}/messages`
Loads discussion logs.
- **Headers**: `Authorization: Bearer <access_token>`
- **Response** (200 OK): List of messages.

### POST `/chats/{chat_id}/messages`
Sends a message and fetches bot response.
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "content": "Check today's weather advisor summary.",
    "attachments": []
  }
  ```
- **Response** (200 OK):
  ```json
  {
    "id": "uuid-message-string",
    "chat_id": "uuid-chat-string",
    "sender": "assistant",
    "content": "Here is what AgriGenius resolved for your query: 'Check today's weather advisor summary.'\nRelated checks performed: weather_advisor",
    "attachments": [],
    "tool_calls": [
      {
        "tool_name": "weather_advisor",
        "parameters": {
          "location": "current_location",
          "days_forecast": 3
        },
        "output": {
          "success": true,
          "result": {
            "location": "current_location",
            "temperature_celsius": 28.5,
            "humidity_percentage": 65,
            "rainfall_probability": 0.12,
            "warning": "No active weather warnings. Great time for fertilizer spraying.",
            "status": "success"
          }
        },
        "executed_at": "2026-07-15T12:10:00Z"
      }
    ],
    "created_at": "2026-07-15T12:10:02Z"
  }
  ```
