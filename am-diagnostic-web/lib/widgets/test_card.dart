import 'package:flutter/material.dart';
import '../models/api_result.dart';
import '../theme/app_colors.dart';

class TestCard extends StatelessWidget {
  final EndpointTest test;
  final VoidCallback onRun;

  const TestCard({
    super.key,
    required this.test,
    required this.onRun,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    IconData statusIcon;

    switch (test.status) {
      case TestStatus.success:
        statusColor = AppColors.success;
        statusIcon = Icons.check_circle;
        break;
      case TestStatus.failure:
        statusColor = AppColors.error;
        statusIcon = Icons.error;
        break;
      case TestStatus.running:
        statusColor = AppColors.primary;
        statusIcon = Icons.sync;
        break;
      default:
        statusColor = AppColors.textSecondary;
        statusIcon = Icons.radio_button_unchecked;
    }

    return InkWell(
      onTap: test.status == TestStatus.running ? null : onRun,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // Status Icon
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: statusColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: test.status == TestStatus.running
                  ? SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation(statusColor),
                      ),
                    )
                  : Icon(statusIcon, color: statusColor, size: 20),
            ),
            const SizedBox(width: 12),

            // Test Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    test.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                      fontSize: 14,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${test.method} ${test.url}',
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 12,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (test.responseMessage.isNotEmpty && test.status != TestStatus.pending)
                    Padding(
                      padding: const EdgeInsets.only(top: 4),
                      child: Text(
                        test.responseMessage,
                        style: TextStyle(
                          color: statusColor,
                          fontSize: 11,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(width: 12),

            // Status Code & Duration
            if (test.statusCode > 0)
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: statusColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${test.statusCode}',
                      style: TextStyle(
                        color: statusColor,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${test.durationMs}ms',
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
