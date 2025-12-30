import 'package:flutter/material.dart';
import '../models/api_result.dart';
import '../services/api_service.dart';
import '../constants.dart';

class TestProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  
  // Grouped tests
  Map<String, List<EndpointTest>> _testGroups = {};
  Map<String, List<EndpointTest>> get testGroups => _testGroups;

  bool _isLoggedIn = false;
  // Shared State for UX
  String? _lastCreatedEmail;
  String? _lastCreatedPassword;
  String? _lastCreatedUserId;

  bool get isLoggedIn => _isLoggedIn;
  
  // Getters for shared state
  String? get lastCreatedEmail => _lastCreatedEmail;
  String? get lastCreatedPassword => _lastCreatedPassword;
  String? get lastCreatedUserId => _lastCreatedUserId;

  void setLastCreatedUser(String email, String password, String userId) {
    _lastCreatedEmail = email;
    _lastCreatedPassword = password;
    _lastCreatedUserId = userId;
    notifyListeners();
  }

  String? _authToken;

  TestProvider() {
    _initializeTests();
  }

  void _initializeTests() {
    // We initialize groupings but 'Login' status drives the UI state
    _testGroups = {
      'Service Health': [
        EndpointTest(iD: 'h2', group: 'Service Health', name: 'User Service', url: AppConstants.userHealth, method: 'GET'),
        EndpointTest(iD: 'h3', group: 'Service Health', name: 'Auth Service', url: AppConstants.authHealth, method: 'GET'),
        EndpointTest(iD: 'h4', group: 'Service Health', name: 'Diagnostic UI', url: '/health', method: 'GET'),
      ],
      'Infrastructure Health': [
        EndpointTest(iD: 'i1', group: 'Infrastructure Health', name: 'PostgreSQL', url: AppConstants.infraHealth, method: 'GET', description: 'Checks core relational DB connection'),
        EndpointTest(iD: 'i2', group: 'Infrastructure Health', name: 'MongoDB', url: AppConstants.infraHealth, method: 'GET', description: 'Checks document store connectivity'),
        EndpointTest(iD: 'i3', group: 'Infrastructure Health', name: 'Redis', url: AppConstants.infraHealth, method: 'GET', description: 'Checks cache layer connectivity'),
        EndpointTest(iD: 'i4', group: 'Infrastructure Health', name: 'InfluxDB', url: AppConstants.infraHealth, method: 'GET', description: 'Checks time-series DB connectivity'),
        EndpointTest(iD: 'i5', group: 'Infrastructure Health', name: 'Kafka', url: AppConstants.infraHealth, method: 'GET', description: 'Checks message broker connectivity'),
      ],
      'Authentication': [
        EndpointTest(
          iD: 'a1', 
          group: 'Authentication', 
          name: 'Login (Get Token)', 
          url: AppConstants.apiLogin, 
          method: 'POST',
          body: {'username': '', 'password': ''}, 
        ),
        EndpointTest(
          iD: 'a2', 
          group: 'Authentication', 
          name: 'Validate Token', 
          url: '${AppConstants.authUrl}/auth/v1/validate', 
          method: 'POST',
        ),
      ],
      'Registration': [
        EndpointTest(
          iD: 'r1',
          group: 'Registration',
          name: 'Register User',
          url: AppConstants.apiRegister,
          method: 'POST',
          body: {
            "email": "test_ui_${DateTime.now().millisecondsSinceEpoch}@example.com",
            "password": "SecurePassword123!",
          },
        ),
      ],
      'Protected Resources': [
        EndpointTest(iD: 'p1', group: 'Protected Resources', name: 'Documents', url: AppConstants.protectedDocuments, method: 'GET', requiresAuth: true),
        EndpointTest(iD: 'p2', group: 'Protected Resources', name: 'Reports', url: AppConstants.protectedReports, method: 'GET', requiresAuth: true),
      ]
    };
  }

  Future<bool> login(String email, String password) async {
    // 1. Setup specific test
    final loginTest = EndpointTest(
       iD: 'login_init', group: 'Init', name: 'Initial Login', 
       url: '${AppConstants.authUrl}/auth/v1/tokens', 
       method: 'POST',
       body: {'username': email, 'password': password}
    );

    // 2. Run
    final resultPair = await _apiService.executeTestWithData(loginTest);
    final result = resultPair['result'] as EndpointTest;
    final data = resultPair['data'] as Map<String, dynamic>;

    if (result.status == TestStatus.success) {
       final token = data['access_token'];
       if (token != null) {
          _authToken = token;
          _apiService.setAuthToken(token);
          _isLoggedIn = true;
          
          // Update the list test body to match successful credentials
          _updateLoginTestCase(email, password);
          
          notifyListeners();
          return true;
       }
    }
    return false;
  }

  void _updateLoginTestCase(String email, String password) {
    List<EndpointTest>? list = _testGroups['Authentication'];
    if (list != null) {
       int idx = list.indexWhere((t) => t.iD == 'a1');
       if (idx != -1) {
         list[idx] = list[idx].copyWith(body: {'username': email, 'password': password});
       }
    }
  }

  Future<void> runTest(EndpointTest test) async {
    // UI update to running
    _updateTestStatus(test.group, test.iD, TestStatus.running);
    notifyListeners();

    // Prepare dynamic body if needed (e.g. validate token)
    EndpointTest testToRun = test;
    if (test.iD == 'a2' && _authToken != null) {
       testToRun = test.copyWith(body: {'token': _authToken});
    }

    // Execute
    final resultPair = await _apiService.executeTestWithData(testToRun);
    final result = resultPair['result'] as EndpointTest;
    
    // Update UI
    _updateTestResult(result);
  }

  Future<void> runGroup(String groupName) async {
    final list = _testGroups[groupName] ?? [];
    for (var test in list) {
       await runTest(test);
    }
  }

  void _updateTestStatus(String group, String iD, TestStatus status) {
    final list = _testGroups[group];
    if (list != null) {
      final index = list.indexWhere((t) => t.iD == iD);
      if (index != -1) {
        list[index] = list[index].copyWith(status: status);
      }
    }
  }

  void _updateTestResult(EndpointTest result) {
    final list = _testGroups[result.group];
    if (list != null) {
      final index = list.indexWhere((t) => t.iD == result.iD);
      if (index != -1) {
        list[index] = result;
        notifyListeners();
      }
    }
  }
}
