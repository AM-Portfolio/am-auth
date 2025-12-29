import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:math';
import '../constants.dart';

enum TimeFilter { h24, w1, m1, m3, m6, y1 }

class AnalyticsProvider extends ChangeNotifier {
  TimeFilter _selectedFilter = TimeFilter.w1;
  TimeFilter get selectedFilter => _selectedFilter;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  // Data
  List<FlSpot> _growthData = [];
  Map<String, double> _statusDistribution = {};
  Map<String, dynamic> _kpiData = {};
  List<BarChartGroupData> _portfolioDistribution = [];
  
  List<FlSpot> get growthData => _growthData;
  Map<String, double> get statusDistribution => _statusDistribution;
  Map<String, dynamic> get kpiData => _kpiData;
  List<BarChartGroupData> get portfolioDistribution => _portfolioDistribution;

  AnalyticsProvider() {
    fetchData();
  }

  void setFilter(TimeFilter filter) {
    _selectedFilter = filter;
    fetchData(); // In real app, pass filter to API
  }

  Future<void> fetchData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // 1. Fetch real user stats
      final response = await http.get(Uri.parse('${AppConstants.userUrl}/api/v1/users/stats'));
      
      Map<String, dynamic> stats;
      
      if (response.statusCode == 200) {
        stats = json.decode(response.body);
      } else {
        throw Exception('Failed to load stats: ${response.statusCode}');
      }

      // 2. Process KPI Data (Real + Derived)
      final totalUsers = stats['total_users'] as int;
      final activeUsers = stats['active_users'] as int;
      
      // Enhance backend data with business logic derivatives
      final random = Random();
      
      _kpiData = {
        'total_users': totalUsers,
        'active_users': activeUsers,
        'online_now': stats['online_now'] ?? 0,
        'new_users': stats['new_users_24h'] ?? 0,
        // Mock business metrics until Portfolio Service is ready
        'total_aum': 45.2 + (totalUsers * 0.001), 
        'avg_portfolio': 3650.0,
      };

      // 3. Process Status Distribution (Real)
      final dist = stats['status_distribution'] as Map<String, dynamic>;
      double total = (dist['active'] ?? 0) + (dist['pending'] ?? 0) + (dist['suspended'] ?? 0) + 0.0001; // Avoid div/0
      
      _statusDistribution = {
        'Active': ((dist['active'] ?? 0) / total) * 100,
        'Pending': ((dist['pending'] ?? 0) / total) * 100,
        'Suspended': ((dist['suspended'] ?? 0) / total) * 100,
      };

      // 4. Generate Historical Trends (Simulated based on Real Total)
      _generateTrendData(totalUsers);

      // 5. Generate Portfolio Distribution (Simulated)
      _generatePortfolioData();

    } catch (e) {
      _error = e.toString();
      // Fallback to mock data on error for demo stability
      _generateMockData(); 
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _generateTrendData(int currentTotal) {
    final random = Random();
    _growthData = [];
    int points = 0;
    
    switch (_selectedFilter) {
      case TimeFilter.h24: points = 24; break;
      case TimeFilter.w1: points = 7; break;
      case TimeFilter.m1: points = 30; break;
      case TimeFilter.m3: points = 12; break;
      case TimeFilter.m6: points = 6; break;
      case TimeFilter.y1: points = 12; break;
    }

    // Work backwards from current real total
    double val = currentTotal.toDouble();
    List<double> values = [val];
    
    for (int i = 0; i < points - 1; i++) {
        val -= random.nextInt(5); // Simulate growth
        values.add(val);
    }
    
    values = values.reversed.toList();
    for (int i = 0; i < points; i++) {
        _growthData.add(FlSpot(i.toDouble(), values[i]));
    }
  }

  void _generatePortfolioData() {
    _portfolioDistribution = [
      _makeBarGroup(0, 45, Colors.blue.shade300),
      _makeBarGroup(1, 30, Colors.blue.shade500),
      _makeBarGroup(2, 15, Colors.blue.shade700),
      _makeBarGroup(3, 10, Colors.indigo.shade900),
    ];
  }

  void _generateMockData() {
     // Fallback if API fails
     _kpiData = {'total_users': 0, 'active_users': 0, 'online_now': 0, 'new_users': 0, 'total_aum': 0.0, 'avg_portfolio': 0.0};
     _statusDistribution = {'Active': 0, 'Pending': 0, 'Suspended': 0};
     _growthData = [const FlSpot(0, 0), const FlSpot(1, 0)];
     _portfolioDistribution = [];
  }

  BarChartGroupData _makeBarGroup(int x, double y, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: color,
          width: 20,
          borderRadius: const BorderRadius.only(
            topLeft: Radius.circular(6),
            topRight: Radius.circular(6),
          ),
        ),
      ],
    );
  }

  String getFilterLabel(TimeFilter filter) {
    switch (filter) {
      case TimeFilter.h24: return '24H';
      case TimeFilter.w1: return '1W';
      case TimeFilter.m1: return '1M';
      case TimeFilter.m3: return '3M';
      case TimeFilter.m6: return '6M';
      case TimeFilter.y1: return '1Y';
    }
  }
}
