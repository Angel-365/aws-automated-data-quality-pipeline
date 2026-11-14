
import csv
import json

# File locations
input_file = "data/customers.csv"
valid_file = "processed/customers_valid.csv"
invalid_file = "quarantine/customers_invalid.csv"
report_file = "reports/quality_report.json"

# Containers for our results
seen_ids = set()
valid_records = []
invalid_records = []

# Read the customer CSV
with open(input_file, "r", newline="") as file:
    reader = csv.DictReader(file)

    # Check that the required columns exist
    required_columns = {"customer_id", "name", "age", "email"}

    if not required_columns.issubset(reader.fieldnames or []):
        raise ValueError("CSV is missing required columns")

    # Validate each customer
    for row_number, row in enumerate(reader, start=2):

        errors = []

        customer_id = row["customer_id"].strip()
        name = row["name"].strip()
        age = row["age"].strip()
        email = row["email"].strip()

        # Check customer ID
        if not customer_id:
            errors.append("Missing customer ID")
        elif customer_id in seen_ids:
            errors.append("Duplicate customer ID")

        # Check customer name
        if not name:
            errors.append("Missing customer name")

        # Check age
        try:
            age_number = int(age)

            if age_number < 18 or age_number > 100:
                errors.append("Age must be between 18 and 100")

        except ValueError:
            errors.append("Age must be a whole number")

        # Check email
        if not email:
            errors.append("Missing email")

        elif email.count("@") != 1:
            errors.append("Invalid email format")

        else:
            email_parts = email.split("@")
            domain = email_parts[1]

            if (
                not email_parts[0]
                or "." not in domain
                or domain.startswith(".")
                or domain.endswith(".")
                or " " in email
            ):
                errors.append("Invalid email format")

        # Classify the record
        if errors:
            row["errors"] = "; ".join(errors)
            invalid_records.append(row)

            print(f"Row {row_number}: INVALID - {row['errors']}")

        else:
            valid_records.append(row)
            seen_ids.add(customer_id)

            print(f"Row {row_number}: VALID")

# Save valid records
with open(valid_file, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["customer_id", "name", "age", "email"]
    )
    writer.writeheader()
    writer.writerows(valid_records)

# Save invalid records
with open(invalid_file, "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["customer_id", "name", "age", "email", "errors"]
    )
    writer.writeheader()
    writer.writerows(invalid_records)

# Create quality report
report = {
    "total_records": len(valid_records) + len(invalid_records),
    "valid_records": len(valid_records),
    "invalid_records": len(invalid_records),
    "quality_percentage": round(
        len(valid_records) /
        (len(valid_records) + len(invalid_records)) * 100, 2
    )
}

with open(report_file, "w") as file:
    json.dump(report, file, indent=4)

# Display summary
print("\n--- DATA QUALITY SUMMARY ---")
print(f"Valid records: {len(valid_records)}")
print(f"Invalid records: {len(invalid_records)}")
print(f"Total records: {len(valid_records) + len(invalid_records)}")
print(f"Quality percentage: {report['quality_percentage']}%")

print("\nOutput files created successfully!")
