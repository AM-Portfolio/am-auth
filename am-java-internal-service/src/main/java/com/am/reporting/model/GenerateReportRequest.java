package com.am.reporting.model;

import java.util.Map;

public class GenerateReportRequest {
    private String reportType;
    private String reportName;
    private Map<String, Object> parameters;

    // Constructors
    public GenerateReportRequest() {}

    public GenerateReportRequest(String reportType, String reportName, Map<String, Object> parameters) {
        this.reportType = reportType;
        this.reportName = reportName;
        this.parameters = parameters;
    }

    // Getters and Setters
    public String getReportType() { return reportType; }
    public void setReportType(String reportType) { this.reportType = reportType; }

    public String getReportName() { return reportName; }
    public void setReportName(String reportName) { this.reportName = reportName; }

    public Map<String, Object> getParameters() { return parameters; }
    public void setParameters(Map<String, Object> parameters) { this.parameters = parameters; }
}