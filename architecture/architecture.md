flowchart TD
    A["1. CSV File Uploaded"] --> B["2. Amazon S3 - raw/"]
    B -->|"3. S3 ObjectCreated Event"| C["4. AWS Lambda Triggered"]
    C -->|"5. Retrieve CSV File"| D["6. Python Data Validation"]

    D --> E["7. Valid Records"]
    D --> F["8. Invalid Records + Error Reasons"]
    D --> G["9. JSON Quality Report"]

    E --> H["10. Amazon S3 - processed/"]
    F --> I["11. Amazon S3 - quarantine/"]
    G --> J["12. Amazon S3 - reports/"]

    C --> K["13. Amazon CloudWatch - Execution Logs"]

    L["AWS IAM Execution Role"] -.->|"Permissions"| C
