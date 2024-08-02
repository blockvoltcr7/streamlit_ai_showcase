```markdown
# Technical Design Document for Customized Financial Report API

## 1. Overview
This document provides the technical design for the Customized Financial Report API, enabling financial analysts to generate tailored financial reports based on specific criteria. The API follows RESTful principles and is designed for performance, security, and scalability.

## 2. API Design

### 2.1 API Endpoint
- **Endpoint URL**: `/api/v1/reports/custom`
- **HTTP Method**: POST
- **Content-Type**: application/json

### 2.2 Request Body Structure
The request must be sent as a JSON object containing the following parameters:

```json
{
  "report_type": "string",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "granularity": "string",
  "accounts": ["account_id_1", "account_id_2", ...],
  "currencies": ["currency_code_1", "currency_code_2", ...],
  "include_subtotals": true | false,
  "custom_metrics": [
    {
      "metric_name": "string",
      "calculation": "string"
    }
  ]
}
```

### 2.3 Response Structure
The API response will be structured as follows:

```json
{
  "status": "success" | "partial_success" | "error",
  "message": "string",
  "report_data": {
    "report_type": "string",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "granularity": "string",
    "currency": "string",
    "data": [
      {
        "date": "YYYY-MM-DD",
        "accounts": {
          "account_id": "string",
          "account_name": "string",
          "value": "number"
        },
        "subtotals": {
          "category": "string",
          "value": "number"
        },
        "custom_metrics": {
          "metric_name": "string",
          "value": "number"
        }
      }
    ]
  },
  "warnings": ["string"]
}
```

## 3. Input Validation
The API will implement the following validation rules before processing the request:

- **Date Validation**:
  - Ensure `start_date` is earlier than `end_date`.
  - Restrict the date range to a maximum of 5 years.
  
- **Account Limit**: The `accounts` array should contain no more than 50 entries.

- **Data Type Validation**: Validate that each parameter is of the expected data type.

- **Mandatory Fields**: Ensure the following fields are present:
  - `report_type`
  - `start_date`
  - `end_date`
  - `granularity`
  - `accounts`

### 3.1 Error Handling
In case of validation failure, the API will respond with an error message in the following format:

```json
{
  "status": "error",
  "message": "Validation error message"
}
```

## 4. Report Generation Logic
Upon successful validation, the API will execute the following steps:

1. **Data Retrieval**: Query the financial database for relevant data using SQL queries optimized for performance.
2. **Data Aggregation**: Aggregate the retrieved data based on the specified `granularity`.
3. **Currency Conversion**: If multiple currencies are specified, perform necessary conversions using a currency conversion service.
4. **Custom Metric Calculation**: Calculate and include custom metrics as defined in the request.
5. **Subtotal Calculation**: If `include_subtotals` is true, calculate and append subtotals to the report.

## 5. Non-functional Requirements

- **Performance**: The API should respond within 5 seconds for reports covering up to 1 year of data.
- **Concurrency**: The system should support up to 100 concurrent requests.
- **Availability**: Target an uptime of 99.9%.
- **Security**: All communications should be secured using TLS 1.3.
- **Logging**: Implement logging for all requests and responses for auditing purposes.
- **Rate Limiting**: Implement rate limiting to mitigate abuse.

## 6. Technology Stack
- **Programming Language**: Java
- **Framework**: Spring Boot
- **Database**: Relational Database (e.g., PostgreSQL, MySQL)
- **Logging**: SLF4J with Logback
- **API Documentation**: Swagger/OpenAPI

## 7. Constraints and Assumptions
- All financial data is assumed to be stored in a relational database.
- The API will utilize the existing authentication and authorization mechanisms.
- All date-time values will be processed in UTC.
- The API will adhere to standard logging and monitoring practices.

## 8. Potential Technical Challenges
1. **Data Volume**: Handling large volumes of financial data efficiently to meet performance requirements.
2. **Currency Conversion**: Implementing accurate and timely currency conversion, especially with fluctuating exchange rates.
3. **Custom Metric Calculation**: Defining a flexible mechanism for calculating user-defined metrics without compromising performance.
4. **Concurrency Management**: Ensuring the API can handle multiple concurrent requests without degradation in performance.
5. **Error Handling**: Providing meaningful error messages while maintaining user privacy and security.

## 9. Out of Scope
- Real-time data updates during report generation.
- Integration with external data sources.
- Export of reports to formats other than JSON (e.g., PDF, Excel).
- User interface for report customization (API only).
```