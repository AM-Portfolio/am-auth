class AppConstants {
  // Use environment variables or default to localhost for development
  // In Docker, these will be set to use nginx proxy paths
  static const String baseUrl = String.fromEnvironment(
    'API_GATEWAY_URL',
    defaultValue: 'http://localhost:8000',
  );
  
  static const String authUrl = String.fromEnvironment(
    'AUTH_SERVICE_URL',
    defaultValue: 'http://localhost:8001',
  );
  
  static const String userUrl = String.fromEnvironment(
    'USER_SERVICE_URL',
    defaultValue: 'http://localhost:8010',
  );

  // Endpoint specific
  static const String apiHealth = '$baseUrl/health';
  static const String apiLogin = '$authUrl/api/v1/tokens';
  static const String apiRegister = '$userUrl/api/v1/auth/register';
  
  // Protected Routes
  static const String protectedDocuments = '$baseUrl/api/v1/documents';
  static const String protectedReports = '$baseUrl/api/v1/reports';
}
