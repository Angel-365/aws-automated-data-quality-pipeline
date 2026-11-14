import boto3 #boto3 is the software that establishes connection between Python and AWS services
import csv # is the library that allows Python to read, process, and write the csv data
import io # makes it possible to read the contents on the csv 
import json # allows python to generate the json files
from urllib.parse import unquote_plus # it decodes the unique s3 added contents from the event notification received

# Create an S3 client
s3 = boto3.client("s3") #tells the code which client to connect to

def lambda_handler(event, context):
    results = []

    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        # Extract the original filename from the S3 object key
        filename = key.rsplit("/", 1)[-1]
        # Remove the .csv extension from the filename
        base_name = filename.rsplit(".", 1)[0]

        valid_key = f"processed/{base_name}_valid.csv"
        invalid_key = f"quarantine/{base_name}_invalid.csv"
        report_key = f"reports/{base_name}_quality_report.json"

        response = s3.get_object(Bucket=bucket, Key=key) # This line asks Amazon S3 to retrieve the CSV file and return it to Lambda.
        csv_content = response["Body"].read().decode("utf-8") # This line extract the contents of the csv file and converts it to readable text

        csv_file = io.StringIO(csv_content) # This line converts the csv text to file-like object
        reader = csv.DictReader(csv_file) # This line uses the headings of the csv file to help organise the information into a python dictionary
        # EXAMPLE: customer_id,name,age,email; C001,John,25,john@example.com; C002,Mary,30,mary@example.com TO Json like represantation

        # Define the required CSV column headings
        required_columns = ["customer_id", "name", "age", "email"]

        # Check whether all required headings exist in the uploaded CSV
        if not reader.fieldnames or not all(
            column in reader.fieldnames for column in required_columns
        ):
            raise ValueError("CSV is missing one or more required columns")

        valid_records = [] # This creates an empty list where we will save all the valid records
        invalid_records = [] # This creates an empty list where we will save all the invalid records
        seen_ids = set() # This created python set, which is used to check if the customer ID has appeared or not. 

        for customer in reader:

            #This checks if every customer record has customer ID or not, if not then it rejects it given a reason of "Missing customer ID"
            customer_id = (customer.get("customer_id") or "").strip() #Extracts the customers ID and remove unnecessary extra spaces
            if not customer_id:
                invalid_records.append({
                    **customer,
                    "error_reason": "Missing customer ID"
                })
                continue

            #This checks that in the seen_ids set, customer ID are all unique and not duplicated and if duplicated the second ID is rejected given the reason of "duplicate customer ID"
            if customer_id in seen_ids:
                invalid_records.append({
                    **customer,
                    "error_reason": "Duplicate customer ID"
                })
                continue

            # Verifies if customer name is not missing, and that it cleans the customer name removing extra spaces. If customer name is missing then it rejects it given the reason of "missing customer name"                          
            name = (customer.get("name") or "").strip() #Extracts the customers name and remove unnecessary extra spaces
            if not name:
                invalid_records.append({
                    **customer,
                    "error_reason": "Missing customer name"
                })
                continue

            #Verifies the age if is within the accepted age range, if not it rejects it giving the reason "Age must be between 18 and 100"
            age = (customer.get("age") or "").strip() # Extracts the age and remove unnecessary extra spaces
            if not age.isdigit() or not 18 <= int(age) <= 100:
                invalid_records.append({
                    **customer,
                    "error_reason": "Age must be between 18 and 100"
                })
                continue

            # Verifies that the cutomer email is in an acceptable form, if not then it will be rejected with a reason of "Missing or invalid email"
            email = (customer.get("email") or "").strip() #This retrieves the customer's email and removes unnecessary spaces.
            if not email or "@" not in email or "." not in email.split("@")[-1]:
                invalid_records.append({
                    **customer,
                    "error_reason": "Missing or invalid email"
                })
                continue

            customer["customer_id"] = customer_id
            customer["name"] = name
            customer["age"] = age
            customer["email"] = email

            seen_ids.add(customer_id) # This adds the accepted customer's ID to our set
            valid_records.append(customer) # This accepts the customers information to valid records if all checks are passed

        # Create a file-like space in memory for our valid CSV records
        valid_output = io.StringIO()

        # Define the column headings for our CSV file
        fieldnames = ["customer_id", "name", "age", "email"]

        # Create a CSV writer that understands our dictionary records
        writer = csv.DictWriter(valid_output, fieldnames=fieldnames)

        # Write the column headings into the CSV
        writer.writeheader()

        # Write all valid customer records into the CSV
        writer.writerows(valid_records)

        # Create an empty file-like space for invalid records
        invalid_output = io.StringIO()

        # Define the columns, including the reason why each record failed
        invalid_fieldnames = fieldnames + ["error_reason"]

        # Create a CSV writer for the invalid records
        invalid_writer = csv.DictWriter(
            invalid_output,
            fieldnames=invalid_fieldnames
        )

        # Write the column headings
        invalid_writer.writeheader()

        # Write all invalid customer records
        invalid_writer.writerows(invalid_records)

        # Calculate the total number of customer records
        total_records = len(valid_records) + len(invalid_records)

        # Count the valid and invalid records
        valid_count = len(valid_records)
        invalid_count = len(invalid_records)

        # Calculate the percentage of valid records
        quality_percentage = (
            round((valid_count / total_records) * 100, 2)
            if total_records > 0 else 0
        )

        # Organise the calculated results into a dictionary
        quality_report = {
            "total_records": total_records,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "quality_percentage": quality_percentage
        }

# Display the data quality results in CloudWatch Logs
        print(f"File processed: {key}")
        print(f"Total records: {total_records}")
        print(f"Valid records: {valid_count}")
        print(f"Invalid records: {invalid_count}")
        print(f"Data quality percentage: {quality_percentage}%")

        # Convert the dictionary into JSON text
        report_json = json.dumps(quality_report, indent=4)

        # Upload the valid CSV file to the processed folder in S3
        s3.put_object(
            Bucket=bucket,
            Key=valid_key,
            Body=valid_output.getvalue(),
            ContentType="text/csv"
        )

        # Upload the invalid CSV file to the quarantine folder in S3
        s3.put_object(
            Bucket=bucket,
            Key=invalid_key,
            Body=invalid_output.getvalue(),
            ContentType="text/csv"
        )

        # Upload the JSON quality report to the reports folder in S3
        s3.put_object(
            Bucket=bucket,
            Key=report_key,
            Body=report_json,
            ContentType="application/json"
        )

        results.append({
            "status": "success",
            "processed_file": key,
            "total_records": total_records,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "quality_percentage": quality_percentage
        })

    return {
        "status": "completed",
        "results": results
    }
