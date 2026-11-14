# AWS Automated Data Quality Pipeline

## 1. Project Overview

This project implements a serverless, event-driven data quality pipeline using Amazon Web Services (AWS) and Python.

The pipeline automatically processes customer CSV files uploaded to Amazon S3. When a new file is uploaded, an AWS Lambda function is triggered to retrieve the file, validate customer records, separate valid and invalid records, and generate a JSON data quality report.

The purpose of this project is to demonstrate how cloud services and Python can be used to automate data validation and improve data reliability.

## 2. Architecture

### AWS Services Used

| Service | Purpose |
|---|---|
| Amazon S3 | Stores incoming CSV files and processed outputs |
| AWS Lambda | Executes the automated data validation logic |
| AWS IAM | Manages permissions between AWS services |
| Amazon CloudWatch | Captures execution logs and processing statistics |

### Processing Workflow

1. A customer CSV file is uploaded to the S3 `raw/` folder.
2. An S3 ObjectCreated event automatically triggers the Lambda function.
3. Lambda retrieves the uploaded CSV file from S3.
4. Python processes and validates each customer record.
5. Valid records are saved to the `processed/` folder.
6. Invalid records and their rejection reasons are saved to the `quarantine/` folder.
7. A JSON data quality report is generated and saved to the `reports/` folder.
8. CloudWatch captures execution logs and processing statistics.

## 3. Data Quality Rules

The pipeline currently checks for:

- Missing customer IDs.
- Duplicate customer IDs.
- Missing customer names.
- Customer ages outside the accepted range of 18–100.
- Missing or incorrectly formatted email addresses.
- Missing required CSV column headings.

Records that fail validation are rejected and accompanied by explanations of the validation errors.

## 4. Technologies Used

- Python 3
- Boto3 (AWS SDK for Python)
- Amazon S3
- AWS Lambda
- AWS IAM
- Amazon CloudWatch
- CSV and JSON processing

## 5. Project Structure

```text
aws-automated-data-quality-pipeline/
├── src/
│   └── lambda_function.py
├── data/
│   └── sample_customers.csv
├── outputs/
│   ├── customers_valid.csv
│   ├── customers_invalid.csv
│   └── customers_quality_report.json
├── docs/
├── architecture/
├── README.md
└── .gitignore
```

## 6. Sample Test Results

The pipeline was tested using a sample dataset containing 20 customer records.

| Metric | Result |
|---|---:|
| Total records | 20 |
| Valid records | 13 |
| Invalid records | 7 |
| Data quality percentage | 65% |

The test confirmed that the Lambda function successfully processed the dataset and generated the expected output files.

## 7. Pipeline Outputs

| S3 Folder | Description |
|---|---|
| `processed/` | Contains customer records that passed validation |
| `quarantine/` | Contains rejected customer records and validation errors |
| `reports/` | Contains the JSON data quality report |

Example output files are included in the `outputs/` directory.

## 8. Testing and Verification

The project was tested using:

- A manual Lambda test with a simulated S3 event.
- Verification of the generated valid and invalid CSV files.
- Verification of the generated JSON quality report.
- An end-to-end test in which uploading a new CSV file to the S3 `raw/` folder automatically triggered Lambda.
- Verification of execution logs in Amazon CloudWatch.

## 9. Current Limitations

- The pipeline currently expects four CSV columns: `customer_id`, `name`, `age`, and `email`.
- Additional CSV columns are not yet supported by the output-writing logic.
- Email validation checks basic formatting only; it does not verify whether an email address exists.
- Duplicate event handling and advanced error recovery have not yet been implemented.

## 10. Future Improvements

- Support additional CSV columns dynamically.
- Improve handling of malformed CSV records.
- Implement idempotency to prevent duplicate event processing.
- Expand automated testing and error handling.
- Extend the pipeline to support larger datasets and additional data sources.

## 11. Project Status

**Core pipeline implemented and successfully tested on AWS.**
