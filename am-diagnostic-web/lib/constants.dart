class AppConstants {
  // Use environment variables or default to localhost for development
  // In Docker, these will be set to use nginx proxy paths
  static const String baseUrl = String.fromEnvironment(
    'API_GATEWAY_URL',
    defaultValue: 'http://localhost:8002', // Point to User Service by default since Gateway is gone
  );
  
  static const String authUrl = String.fromEnvironment(
    'AUTH_SERVICE_URL',
    defaultValue: 'http://localhost:8001',
  );
  
  static const String userUrl = String.fromEnvironment(
    'USER_SERVICE_URL',
    defaultValue: 'http://localhost:8002',
  );

  // Endpoint specific
  static const String apiHealth = '$baseUrl/health';
  static const String authHealth = '$authUrl/health';
  static const String userHealth = '$userUrl/health';
  static const String infraHealth = '$userUrl/users/v1/infra/health';
  
  static const String apiLogin = '$authUrl/auth/v1/tokens';
  static const String apiRegister = '$userUrl/users/v1/auth/register';
  
  // Protected Routes
  static const String protectedDocuments = '$baseUrl/users/v1/documents';
  static const String protectedReports = '$baseUrl/users/v1/reports';
}
