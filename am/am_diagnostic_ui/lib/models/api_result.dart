enum TestStatus { pending, running, success, failure, partial }

class EndpointTest {
  final String iD;
  final String group;
  final String name;
  final String url;
  final String method;
  final String? description;
  final Map<String, dynamic>? body;
  final bool requiresAuth;
  
  // State
  TestStatus status;
  int statusCode;
  String responseMessage;
  int durationMs;

  EndpointTest({
    required this.iD,
    required this.group,
    required this.name,
    required this.url,
    required this.method,
    this.description,
    this.body,
    this.requiresAuth = false,
    this.status = TestStatus.pending,
    this.statusCode = 0,
    this.responseMessage = '',
    this.durationMs = 0,
  });

  // Create a copy for state updates
  EndpointTest copyWith({
    TestStatus? status,
    int? statusCode,
    String? responseMessage,
    int? durationMs,
    Map<String, dynamic>? body,
  }) {
    return EndpointTest(
      iD: iD,
      group: group,
      name: name,
      url: url,
      method: method,
      description: description,
      body: body ?? this.body,
      requiresAuth: requiresAuth,
      status: status ?? this.status,
      statusCode: statusCode ?? this.statusCode,
      responseMessage: responseMessage ?? this.responseMessage,
      durationMs: durationMs ?? this.durationMs,
    );
  }
}
