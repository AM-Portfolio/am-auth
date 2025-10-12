package com.am.reporting.controller;

import com.am.reporting.model.GenerateReportRequest;
import com.am.reporting.model.Report;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/internal")
public class ReportingController {

    private static final Logger logger = LoggerFactory.getLogger(ReportingController.class);

    // Mock data
    private static final List<Report> MOCK_REPORTS = Arrays.asList(
        new Report("rpt-001", "User Activity Report", "activity", "completed", "user-123",
                   LocalDateTime.of(2024, 1, 15, 10, 0),
                   Map.of("total_users", 1250, "active_users", 892, "new_users", 45),
                   Map.of("date_range", "last_30_days", "include_inactive", false)),
        new Report("rpt-002", "Revenue Summary", "financial", "completed", "user-456",
                   LocalDateTime.of(2024, 1, 16, 14, 30),
                   Map.of("total_revenue", 125000.50, "transactions", 1834, "avg_transaction", 68.15),
                   Map.of("currency", "USD", "period", "Q1_2024")),
        new Report("rpt-003", "System Performance", "technical", "pending", "user-123",
                   LocalDateTime.of(2024, 1, 17, 9, 15),
                   Map.of("avg_response_time", 0.245, "uptime_percentage", 99.8, "errors", 12),
                   Map.of("metrics_type", "performance", "include_alerts", true))
    );

    @GetMapping("/reports")
    public ResponseEntity<List<Report>> getReports() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Map<String, Object> details = (Map<String, Object>) auth.getDetails();
        String tokenType = (String) details.get("token_type");

        if ("user".equals(tokenType)) {
            String userId = (String) details.get("user_id");
            List<Report> userReports = MOCK_REPORTS.stream()
                .filter(report -> userId.equals(report.getUserId()))
                .collect(Collectors.toList());
            
            logger.info("Retrieved {} reports for user {}", userReports.size(), details.get("username"));
            return ResponseEntity.ok(userReports);
        } else {
            logger.info("Service {} requested all reports", details.get("service_id"));
            return ResponseEntity.ok(MOCK_REPORTS);
        }
    }

    @GetMapping("/reports/all")
    public ResponseEntity<List<Report>> getAllReports() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Map<String, Object> details = (Map<String, Object>) auth.getDetails();
        String tokenType = (String) details.get("token_type");

        if (!"service".equals(tokenType)) {
            return ResponseEntity.status(403).build(); // Only services can access all reports
        }

        logger.info("Service {} requested all reports", details.get("service_id"));
        return ResponseEntity.ok(MOCK_REPORTS);
    }

    @PostMapping("/reports/generate")
    public ResponseEntity<Report> generateReport(@RequestBody GenerateReportRequest request) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Map<String, Object> details = (Map<String, Object>) auth.getDetails();
        String tokenType = (String) details.get("token_type");

        if (!"user".equals(tokenType)) {
            return ResponseEntity.status(403).build(); // Only users can generate reports
        }

        String userId = (String) details.get("user_id");
        String username = (String) details.get("username");

        // Simulate report generation
        String reportId = "rpt-" + System.currentTimeMillis();
        LocalDateTime now = LocalDateTime.now();

        Map<String, Object> generatedData = new HashMap<>();
        generatedData.put("report_type", request.getReportType());
        generatedData.put("generated_by", username);
        generatedData.put("generation_time_ms", 1500);
        
        // Add mock data based on report type
        switch (request.getReportType().toLowerCase()) {
            case "activity":
                generatedData.put("total_actions", 2450);
                generatedData.put("unique_users", 156);
                break;
            case "financial":
                generatedData.put("total_amount", 45000.75);
                generatedData.put("transaction_count", 892);
                break;
            case "technical":
                generatedData.put("system_load", 0.67);
                generatedData.put("memory_usage", 0.82);
                break;
            default:
                generatedData.put("items_processed", 100);
        }

        Report newReport = new Report(
            reportId,
            request.getReportName(),
            request.getReportType(),
            "completed",
            userId,
            now,
            generatedData,
            request.getParameters()
        );
        newReport.setGeneratedAt(now);

        logger.info("Generated report {} of type {} for user {}", 
                   reportId, request.getReportType(), username);

        return ResponseEntity.ok(newReport);
    }

    @GetMapping("/reports/{reportId}")
    public ResponseEntity<Report> getReport(@PathVariable String reportId) {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Map<String, Object> details = (Map<String, Object>) auth.getDetails();
        String tokenType = (String) details.get("token_type");

        Report report = MOCK_REPORTS.stream()
            .filter(r -> reportId.equals(r.getId()))
            .findFirst()
            .orElse(null);

        if (report == null) {
            return ResponseEntity.notFound().build();
        }

        if ("user".equals(tokenType)) {
            String userId = (String) details.get("user_id");
            if (!userId.equals(report.getUserId())) {
                return ResponseEntity.status(403).build(); // User can only access their own reports
            }
        }

        return ResponseEntity.ok(report);
    }

    @GetMapping("/service-info")
    public ResponseEntity<Map<String, Object>> getServiceInfo() {
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        Map<String, Object> details = (Map<String, Object>) auth.getDetails();
        String tokenType = (String) details.get("token_type");

        if (!"service".equals(tokenType)) {
            return ResponseEntity.status(403).build(); // Only services can access service info
        }

        Map<String, Object> serviceInfo = new HashMap<>();
        serviceInfo.put("service_id", "am-java-internal-service");
        serviceInfo.put("service_name", "Reporting Service");
        serviceInfo.put("version", "1.0.0");
        serviceInfo.put("capabilities", Arrays.asList(
            "report_generation", "report_listing", "data_analysis"
        ));
        serviceInfo.put("total_reports", MOCK_REPORTS.size());
        serviceInfo.put("completed_reports", MOCK_REPORTS.stream()
            .mapToLong(r -> "completed".equals(r.getStatus()) ? 1 : 0)
            .sum());

        logger.info("Service {} requested service info", details.get("service_id"));
        return ResponseEntity.ok(serviceInfo);
    }
}