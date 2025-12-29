# AM Diagnostic UI

A comprehensive Flutter-based diagnostic dashboard for testing and monitoring all AM microservices endpoints.

## Features

### 🔐 Authentication Flow
- **Login Screen**: Clean, animated login interface
- **Credential Management**: Automatically captures and stores JWT tokens
- **Session Handling**: Maintains authentication state across tests

### 🧪 Endpoint Testing
- **Grouped Tests**: Organized by service category
  - Service Health Checks
  - Authentication & Authorization
  - User Registration
  - Protected Resources
  - Security Testing
  - Rate Limiting

- **Individual Test Execution**: Run tests one at a time
- **Batch Execution**: Run all tests in a group
- **Real-time Status**: Live updates with color-coded results
  - ✅ Green: Success (200-299)
  - ❌ Red: Failure (400-599)
  - 🔵 Blue: Running
  - ⚪ Gray: Pending

### 📊 Visual Feedback
- **Animated UI**: Smooth transitions and micro-interactions
- **Status Indicators**: Clear visual feedback for each test
- **Response Details**: Status codes, duration, and error messages
- **Clean Design**: Modern white theme with professional aesthetics

## Architecture

```
lib/
├── main.dart                 # App entry point
├── constants.dart            # API endpoints configuration
├── models/
│   └── api_result.dart      # Test result models
├── services/
│   └── api_service.dart     # HTTP client & test execution
├── providers/
│   └── test_provider.dart   # State management
├── screens/
│   ├── login_screen.dart    # Authentication UI
│   └── dashboard_screen.dart # Main testing dashboard
├── widgets/
│   └── test_card.dart       # Reusable test result card
└── theme/
    └── app_colors.dart      # Color palette
```

## Configuration

### API Endpoints
Edit `lib/constants.dart` to configure your service URLs:

```dart
class AppConstants {
  static const String baseUrl = 'http://localhost:8000';  // API Gateway
  static const String authUrl = 'http://localhost:8001';  // Auth Service
  static const String userUrl = 'http://localhost:8010';  // User Service
}
```

### Test Credentials
Default test credentials (can be changed in login screen):
- **Email**: `testuser@example.com`
- **Password**: `password123`

## Running the Application

### Prerequisites
- Flutter SDK 3.38.3 or higher
- Chrome browser
- Running AM microservices (see docker-compose.yml)

### Launch Steps

1. **Navigate to project**:
   ```bash
   cd am/am_diagnostic_ui
   ```

2. **Install dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run on Chrome**:
   ```bash
   flutter run -d chrome
   ```

4. **Login**: Use your test credentials to authenticate

5. **Run Tests**: Click individual tests or "Run All" for groups

## Test Groups

### 1. Service Health
- API Gateway Health Check
- User Service Health Check
- Auth Service Health Check

### 2. Authentication
- Login (Get JWT Token)
- Validate Token

### 3. Registration
- Register New User (with dynamic email)

### 4. Protected Resources
- Documents Endpoint (requires auth)
- Reports Endpoint (requires auth)
- Portfolio Endpoint (requires auth)

## Adding New Tests

To add a new endpoint test, edit `lib/providers/test_provider.dart`:

```dart
'Your Group Name': [
  EndpointTest(
    iD: 'unique_id',
    group: 'Your Group Name',
    name: 'Test Display Name',
    url: 'http://localhost:8000/api/endpoint',
    method: 'GET', // or POST, PUT, DELETE, PATCH
    requiresAuth: true, // if needs JWT token
    body: {'key': 'value'}, // for POST/PUT requests
  ),
],
```

## Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.6.0                          # HTTP client
  provider: ^6.1.5                      # State management
  google_fonts: ^6.3.3                  # Typography
  animate_do: ^4.2.0                    # Animations
  flutter_staggered_animations: ^1.1.1  # List animations
```

## Color Palette

- **Background**: `#F8F9FA` (Off-white)
- **Surface**: `#FFFFFF` (White)
- **Primary**: `#2563EB` (Modern Blue)
- **Success**: `#10B981` (Emerald Green)
- **Error**: `#EF4444` (Red)
- **Warning**: `#F59E0B` (Amber)

## Troubleshooting

### Services Not Responding
1. Ensure Docker containers are running:
   ```bash
   docker-compose -f am/docker-compose.yml ps
   ```

2. Check service health manually:
   ```bash
   curl http://localhost:8000/health
   ```

### Login Fails
1. Verify credentials in database
2. Check Auth Service logs:
   ```bash
   docker logs am-am-auth-tokens-1
   ```

### CORS Issues
If running from browser, ensure services allow CORS from `localhost:*`

## Future Enhancements

- [ ] Export test results to JSON/CSV
- [ ] Test history and comparison
- [ ] Custom test sequences
- [ ] Performance metrics visualization
- [ ] WebSocket connection testing
- [ ] Database connectivity checks
- [ ] Kafka message testing

## License

Part of the AM Portfolio Management System
