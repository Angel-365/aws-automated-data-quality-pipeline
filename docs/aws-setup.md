# AWS Setup and Configuration

## 1. Overview

The project uses four AWS services to implement an automated data quality pipeline:

- Amazon S3
- AWS Lambda
- AWS Identity and Access Management (IAM)
- Amazon CloudWatch

## 2. Amazon S3 Configuration

An S3 bucket was created to store incoming customer CSV files and the resulting processed data.

The bucket uses the following folder structure:

| Folder | Purpose |
|---|---|
| `raw/` | Stores newly uploaded CSV files awaiting validation |
| `processed/` | Stores records that pass validation |
| `quarantine/` | Stores invalid records and validation errors |
| `reports/` | Stores generated JSON quality reports |

An S3 event notification was configured with:

- Event type: All object create events (`s3:ObjectCreated:*`).
- Prefix filter: `raw/`.
- Suffix filter: `.csv`.
- Destination: `CustomerDataQualityProcessor` Lambda function.

This configuration ensures that qualifying CSV uploads to the raw folder automatically trigger the pipeline.

## 3. AWS Lambda Configuration

A Lambda function named `CustomerDataQualityProcessor` was created using:

- Runtime: Python 3.12.
- Architecture: x86_64.
- Memory: 128 MB.
- Timeout: 30 seconds.

The function uses Python and Boto3 to:

1. Retrieve uploaded CSV files from S3.
2. Read and validate customer records.
3. Separate valid and invalid records.
4. Generate a JSON quality report.
5. Save the outputs to their respective S3 folders.

## 4. IAM Configuration

An execution role named `DataQualityLambdaExecutionRole` was created and assigned to the Lambda function.

The role uses a trust relationship that allows the AWS Lambda service to assume it.

The following permissions were configured:

**AWS managed policy:**
- `AWSLambdaBasicExecutionRole` – allows Lambda to write execution logs to CloudWatch.

**Custom inline policy:**
- `s3:GetObject` – allows Lambda to retrieve files from the raw S3 folder.
- `s3:PutObject` – allows Lambda to write results to the processed, quarantine and reports folders.

These permissions follow the principle of least privilege by limiting access to the required S3 locations and actions.

## 5. Amazon CloudWatch Configuration

CloudWatch Logs was used to monitor Lambda execution.

The function writes processing information to its log stream, including:

- Source file processed.
- Total records.
- Valid records.
- Invalid records.
- Data quality percentage.

CloudWatch provides visibility into the pipeline's execution and helps identify processing issues.

## 6. End-to-End Event Flow

The services work together as follows:

1. A CSV file is uploaded to Amazon S3.
2. S3 detects the object creation event.
3. S3 invokes the configured Lambda function.
4. Lambda assumes its execution role to obtain the required permissions.
5. Lambda retrieves the file and performs data validation.
6. Lambda writes the output files to S3.
7. CloudWatch records execution logs.

## 7. Security Considerations

- Lambda uses an IAM execution role rather than hardcoded AWS credentials.
- S3 access is restricted through specific IAM actions and resource paths.
- The S3 event notification only listens for CSV uploads under `raw/`.
- Output folders are separate from the trigger folder, preventing the pipeline's own output files from triggering another execution.

## 8. Configuration Summary

| Component | Configuration |
|---|---|
| S3 bucket | Dedicated project bucket |
| Lambda function | CustomerDataQualityProcessor |
| Lambda runtime | Python 3.12 |
| Lambda execution role | DataQualityLambdaExecutionRole |
| Logging | Amazon CloudWatch |
| Trigger | S3 ObjectCreated event |
| Trigger filter | `raw/` prefix and `.csv` suffix |

Note: Resource names and configuration values are documented for this project. No AWS account IDs, access keys or secret credentials should be published in this repository.
