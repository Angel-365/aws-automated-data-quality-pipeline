# Testing and Results – AWS Automated Data Quality Pipeline

## 1. Testing Overview

The automated data quality pipeline was tested on AWS to verify that CSV files could be uploaded, processed, validated and stored in the correct S3 folders.

Two testing approaches were used:

- Manual Lambda testing using a simulated S3 event.
- End-to-end testing using an actual CSV file upload to the S3 bucket.

## 2. Test Dataset

A sample customer dataset containing 20 records was used.

The dataset included deliberately introduced data quality issues to test the validation logic.

Examples included:

- Duplicate customer IDs.
- Missing customer names.
- Missing email addresses.
- Invalid email formatting.
- Customer ages below 18 or above 100.

## 3. Test Results

| Metric | Expected Result | Actual Result |
|---|---:|---:|
| Total records | 20 | 20 |
| Valid records | 13 | 13 |
| Invalid records | 7 | 7 |
| Data quality percentage | 65% | 65% |

The results confirmed that the pipeline correctly classified the sample records according to the implemented validation rules.

## 4. AWS Testing Procedures

### Test 1: Manual Lambda Invocation

A simulated S3 event was submitted through the AWS Lambda console.

**Expected behaviour:**
- Lambda retrieves the specified CSV file from S3.
- Customer records are validated.
- Valid and invalid records are separated.
- A JSON quality report is generated.

**Actual result:** The Lambda function completed successfully and returned the expected processing summary.

### Test 2: Automatic S3 Event Trigger

A newly named CSV file was uploaded to the S3 `raw/` folder.

**Expected behaviour:**
- S3 detects the new object.
- The configured event notification invokes Lambda automatically.
- Lambda processes the uploaded file.
- Output files are generated in their respective S3 folders.

**Actual result:** The automatic trigger worked successfully. Lambda executed without requiring a manual invocation.

### Test 3: Output Verification

The generated files were inspected in Amazon S3.

The following outputs were verified:

- Valid customer records in `processed/`.
- Invalid customer records and rejection reasons in `quarantine/`.
- JSON quality report in `reports/`.

### Test 4: CloudWatch Log Verification

Amazon CloudWatch Logs was used to inspect the Lambda execution.

The logs confirmed:
- File processing information.
- Total record count.
- Valid record count.
- Invalid record count.
- Data quality percentage.
- Successful Lambda execution.

## 5. Conclusion

The tests confirmed that the core serverless pipeline successfully automates customer CSV validation using Amazon S3 and AWS Lambda.

The project demonstrates event-driven processing, Python-based data validation, S3 object management, IAM permissions and CloudWatch monitoring.
