import boto3
import csv
import os
import json
from datetime import datetime

s3_client = boto3.client('s3', endpoint_url='http://localhost:4566')
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:4566')
table_name = os.environ.get('DYNAMODB_TABLE', 'csv_metadata')

def lambda_handler(event, context):
    # Retrieve S3 bucket and file details from the event
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        # Download file
        file_path = f"/tmp/{object_key}"
        s3_client.download_file(bucket_name, object_key, file_path)

        # Process the CSV file
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            columns = next(reader)
            row_count = sum(1 for row in reader)

        # Extract metadata
        metadata = {
            'filename': object_key,
            'upload_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_size_bytes': os.path.getsize(file_path),
            'row_count': row_count,
            'column_count': len(columns),
            'column_names': columns
        }

        # Store metadata in DynamoDB
        table = dynamodb.Table(table_name)
        table.put_item(Item=metadata)

        # Optional: Log completion
        print(f"Processed {object_key}: {metadata}")

    return {'status': 'success'}
