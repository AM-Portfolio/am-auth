import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/api_result.dart';

class ApiService {
  String? _authToken;
  
  void setAuthToken(String token) {
    _authToken = token;
  }

  // Returns a Pair of [EndpointTest result, ResponseBody]
  Future<Map<String, dynamic>> executeTestWithData(EndpointTest test) async {
    final stopwatch = Stopwatch()..start();
    
    try {
      final uri = Uri.parse(test.url);
      
      final Map<String, String> headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

      if (test.requiresAuth && _authToken != null && _authToken!.isNotEmpty) {
        headers['Authorization'] = 'Bearer $_authToken';
      }

      http.Response response;
      final bodyString = test.body != null ? jsonEncode(test.body) : null;

      switch (test.method.toUpperCase()) {
        case 'GET':
          response = await http.get(uri, headers: headers);
          break;
        case 'POST':
          response = await http.post(uri, headers: headers, body: bodyString);
          break;
        case 'PUT':
          response = await http.put(uri, headers: headers, body: bodyString);
          break;
        case 'PATCH':
          response = await http.patch(uri, headers: headers, body: bodyString);
          break;
        case 'DELETE':
          response = await http.delete(uri, headers: headers);
          break;
        default:
          throw Exception("Method ${test.method} not supported");
      }

      stopwatch.stop();
      final isSuccess = response.statusCode >= 200 && response.statusCode < 300;
      
      String message = 'OK';
      Map<String, dynamic> responseData = {};
      
      try {
        if (response.body.isNotEmpty) {
          final decoded = jsonDecode(response.body);
          if (decoded is Map<String, dynamic>) {
            responseData = decoded;
            if (!isSuccess) {
              message = decoded['detail'] ?? decoded['message'] ?? response.body;
            }
          }
        }
      } catch (_) {
        message = response.body; 
      }

      final updatedTest = test.copyWith(
        status: isSuccess ? TestStatus.success : TestStatus.failure,
        statusCode: response.statusCode,
        responseMessage: message,
        durationMs: stopwatch.elapsedMilliseconds,
      );

      return {
        'result': updatedTest,
        'data': responseData
      };

    } catch (e) {
      stopwatch.stop();
      return {
        'result': test.copyWith(
          status: TestStatus.failure,
          statusCode: 0,
          responseMessage: e.toString(),
          durationMs: stopwatch.elapsedMilliseconds,
        ),
        'data': {}
      };
    }
  }
}
