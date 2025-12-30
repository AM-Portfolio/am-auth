import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:animate_do/animate_do.dart';
import '../providers/analytics_provider.dart';
import '../theme/app_colors.dart';
import '../widgets/info_card.dart';

class UserAnalyticsScreen extends StatelessWidget {
  const UserAnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AnalyticsProvider(),
      child: Scaffold(
        backgroundColor: AppColors.background,
        appBar: AppBar(
          title: const Text('User Analytics'),
          backgroundColor: AppColors.surface,
          elevation: 0,
          titleTextStyle: const TextStyle(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.download_rounded, color: AppColors.primary),
              onPressed: () {},
              tooltip: 'Export Report',
            ),
          ],
        ),
        body: Consumer<AnalyticsProvider>(
          builder: (context, provider, _) {
            return SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                   // Time Filter
                  FadeInDown(child: _buildTimeFilter(provider)),
                  const SizedBox(height: 24),

                  // KPI Grid
                  FadeInUp(child: _buildKPIGrid(provider)),
                  const SizedBox(height: 24),

                  // Growth Chart
                  FadeInUp(
                    delay: const Duration(milliseconds: 100),
                    child: _buildGrowthChartSection(provider),
                  ),
                  const SizedBox(height: 24),

                  // Lower Section: Distribution & Activity
                  FadeInUp(
                    delay: const Duration(milliseconds: 200),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: _buildPortfolioDistribution(provider)),
                        const SizedBox(width: 16),
                        Expanded(child: _buildStatusDistribution(provider)),
                      ],
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildTimeFilter(AnalyticsProvider provider) {
    return Container(
      height: 48,
      padding: const EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.border),
      ),
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: TimeFilter.values.map((filter) {
          final isSelected = provider.selectedFilter == filter;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: InkWell(
              onTap: () => provider.setFilter(filter),
              borderRadius: BorderRadius.circular(8),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                padding: const EdgeInsets.symmetric(horizontal: 16),
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: isSelected ? AppColors.primary : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  provider.getFilterLabel(filter),
                  style: TextStyle(
                    color: isSelected ? Colors.white : AppColors.textSecondary,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildKPIGrid(AnalyticsProvider provider) {
    final data = provider.kpiData;
    return Column(
      children: [
        Row(
          children: [
            Expanded(child: _buildKPICard('Total Users', '${data['total_users']}', Icons.group, Colors.blue)),
            const SizedBox(width: 16),
            Expanded(child: _buildKPICard('Active Users', '${data['active_users']}', Icons.person_add, Colors.green)),
            const SizedBox(width: 16),
            Expanded(child: _buildKPICard('Online Now', '${data['online_now']}', Icons.wifi_tethering, Colors.amber)),
            const SizedBox(width: 16),
             Expanded(child: _buildKPICard('New (24h)', '+${data['new_users']}', Icons.trending_up, Colors.purple)),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(child: _buildBusinessCard('Total AUM', '\$${data['total_aum']}M', Icons.monetization_on, AppColors.textPrimary)),
            const SizedBox(width: 16),
            Expanded(child: _buildBusinessCard('Avg Portfolio', '\$${data['avg_portfolio']}', Icons.pie_chart, AppColors.textPrimary)),
          ],
        )
      ],
    );
  }
  
  Widget _buildKPICard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: color.withOpacity(0.1), blurRadius: 10, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(color: color.withOpacity(0.1), shape: BoxShape.circle),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(height: 12),
          Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          const SizedBox(height: 4),
          Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildBusinessCard(String label, String value, IconData icon, Color bg) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(colors: [AppColors.primary, AppColors.primary.withOpacity(0.8)], begin: Alignment.topLeft, end: Alignment.bottomRight),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: const TextStyle(fontSize: 12, color: Colors.white70)),
              const SizedBox(height: 4),
              Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white)),
            ],
          ),
          Icon(icon, color: Colors.white.withOpacity(0.3), size: 32),
        ],
      ),
    );
  }

  Widget _buildGrowthChartSection(AnalyticsProvider provider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
           const Text('User Growth Trend', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
           const SizedBox(height: 24),
           SizedBox(
             height: 250,
             child: LineChart(
               LineChartData(
                 gridData: FlGridData(show: false),
                 titlesData: FlTitlesData(
                    show: true,
                    bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                 ),
                 borderData: FlBorderData(show: false),
                 lineBarsData: [
                   LineChartBarData(
                     spots: provider.growthData,
                     isCurved: true,
                     color: AppColors.primary,
                     barWidth: 3,
                     isStrokeCapRound: true,
                     dotData: FlDotData(show: false),
                     belowBarData: BarAreaData(
                       show: true,
                       color: AppColors.primary.withOpacity(0.1),
                     ),
                   ),
                 ],
               ),
             ),
           ),
        ],
      ),
    );
  }

  Widget _buildStatusDistribution(AnalyticsProvider provider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('User Status', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          SizedBox(
            height: 200,
            child: PieChart(
              PieChartData(
                sectionsSpace: 0,
                centerSpaceRadius: 40,
                sections: [
                   PieChartSectionData(
                     color: AppColors.success,
                     value: provider.statusDistribution['Active']!,
                     title: '${provider.statusDistribution['Active']}%',
                     radius: 50,
                     titleStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.white),
                   ),
                   PieChartSectionData(
                     color: AppColors.warning,
                     value: provider.statusDistribution['Pending']!,
                     title: '${provider.statusDistribution['Pending']}%',
                     radius: 40,
                     titleStyle: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.white),
                   ),
                   PieChartSectionData(
                     color: AppColors.error,
                     value: provider.statusDistribution['Suspended']!,
                     title: '${provider.statusDistribution['Suspended']}%',
                     radius: 30,
                     titleStyle: const TextStyle(fontSize: 8, fontWeight: FontWeight.bold, color: Colors.white),
                   ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildLegendItem('Active', AppColors.success),
              const SizedBox(width: 8),
              _buildLegendItem('Pending', AppColors.warning),
               const SizedBox(width: 8),
              _buildLegendItem('Suspended', AppColors.error),
            ],
          )
        ],
      ),
    );
  }
  
  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 10, color: AppColors.textSecondary)),
      ],
    );
  }

  Widget _buildPortfolioDistribution(AnalyticsProvider provider) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Portfolio Value', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          SizedBox(
            height: 200,
            child: BarChart(
              BarChartData(
                 gridData: FlGridData(show: false),
                 titlesData: FlTitlesData(
                   show: true,
                   bottomTitles: AxisTitles(
                     sideTitles: SideTitles(
                       showTitles: true,
                       getTitlesWidget: (value, meta) {
                          switch (value.toInt()) {
                            case 0: return const Text('<1k', style: TextStyle(fontSize: 10));
                            case 1: return const Text('1-10k', style: TextStyle(fontSize: 10));
                            case 2: return const Text('10k+', style: TextStyle(fontSize: 10));
                            case 3: return const Text('50k+', style: TextStyle(fontSize: 10));
                          }
                          return const Text('');
                       },
                     ),
                   ),
                   leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                   topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                   rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
                 ),
                 borderData: FlBorderData(show: false),
                 barGroups: provider.portfolioDistribution,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
