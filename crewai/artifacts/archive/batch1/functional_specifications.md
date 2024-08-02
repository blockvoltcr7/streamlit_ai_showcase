```markdown
# Detailed Functional Specifications for Customized Financial Report API

## 1. Overview
This document outlines the detailed functional specifications for the Customized Financial Report API, designed to allow financial analysts to generate customized financial reports based on specific criteria through a RESTful API endpoint.

## 2. API Endpoint
- **Endpoint URL**: `/api/v1/reports/custom`
- **HTTP Method**: POST

## 3. Request Body Structure
The request body must be a JSON object that includes the following parameters:

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

### 3.1 Parameters Description:
- **report_type**: Specifies the type of report to generate. Possible values include:
  - "income_statement"
  - "balance_sheet"
  - "cash_flow"
  
- **start_date**: The start date for the report data in `YYYY-MM-DD` format.
  
- **end_date**: The end date for the report data in `YYYY-MM-DD` format.
  
- **granularity**: Defines the level of detail for the report. Acceptable values are:
  - "daily"
  - "weekly"
  - "monthly"
  - "quarterly"
  - "yearly"
  
- **accounts**: An array of account IDs to include in the report. The maximum allowed is 50.
  
- **currencies**: An array of currency codes for the report. The API will handle conversions as necessary.
  
- **include_subtotals**: A boolean indicating whether to include subtotals in the report.
  
- **custom_metrics**: An array of user-defined calculations that will be included in the report.

## 4. Input Validation
The API must validate input parameters according to the following rules:
- **Date Validation**:
  - Ensure the `start_date` is before the `end_date`.
  - The date range must not exceed 5 years.
  
- **Account Limit**: The number of accounts in the `accounts` array must not exceed 50.

- **Data Type Validation**: Ensure all parameters are of the correct type (e.g., strings, dates, arrays).

- **Mandatory Fields**: The following fields are mandatory and must be included:
  - `report_type`
  - `start_date`
  - `end_date`
  - `granularity`
  - `accounts`

### 4.1 Error Handling
If validation fails, the API must return a JSON response with a status of "error" and a meaningful message detailing the validation failure.

## 5. Report Generation
Upon successful validation, the API will:
1. Query the financial database to retrieve the necessary data based on the specified parameters.
2. Aggregate the data according to the specified granularity.
3. Convert currencies if multiple currencies are specified.
4. Calculate any custom metrics and include them in the report.
5. Include subtotals if requested.

## 6. API Response Structure
The response will be a JSON object structured as follows:

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

### 6.1 Response Details
- **status**: Indicates the result of the request, which can be "success", "partial_success", or "error".
- **message**: Provides additional information about the result.
- **report_data**: Contains the generated report details.
- **warnings**: An array of warning messages if applicable (e.g., if some requested data is unavailable).

## 7. Non-functional Requirements
The API must also meet the following non-functional requirements:
- **Performance**: Respond within 5 seconds for reports covering up to 1 year of data.
- **Concurrency**: Support up to 100 concurrent requests.
- **Availability**: Achieve 99.9% uptime.
- **Security**: Use TLS 1.3 for all communications.
- **Logging**: Log all requests and responses for auditing.
- **Rate Limiting**: Implement mechanisms to prevent abuse.

## 8. Constraints and Assumptions
- The API assumes all financial data is stored in a relational database.
- Authentication and authorization will be managed through the company's existing systems.
- Date and time values will be processed in UTC format.
- The API will utilize standard logging and monitoring tools.

## 9. Out of Scope
- Real-time data updates during report generation.
- Integration with external data sources.
- Exporting reports to formats other than JSON (e.g., PDF, Excel).
- User interface for report customization (API only).

## 10. Documentation
API documentation will be generated using Swagger/OpenAPI to ensure clarity and accessibility for all users.

```