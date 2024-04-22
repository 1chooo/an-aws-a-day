# -*- coding: utf-8 -*-
"""
Date: 2024/04/22
Author: @1chooo(Hugo ChunHo Lin)
E-mail: hugo970217@gmail.com
Version: v0.0.1
"""


import json
import os

import boto3
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

aws_access_key_id = os.environ["AWS_CLIENT_ACCESS_KEY_ID"]
aws_secret_access_key = os.environ["AWS_CLIENT_SECRET_ACCESS_KEY"]
aws_bucket_arn = os.environ["AWS_CLIENT_BUCKET_ARN"]
aws_region_name = os.environ["AWS_CLIENT_REGION_NAME"]
aws_bucket_name = os.environ["AWS_CLIENT_BUCKET_NAME"]

s3_client = boto3.client(
    "s3",
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key,
    region_name=aws_region_name
)

response = s3_client.list_buckets()
bucket_name_list=[]
for bucket in response["Buckets"]:
    bucket_name_list.append(bucket["Name"])

print(bucket_name_list)

if aws_bucket_name not in bucket_name_list:
    s3_client.create_bucket(Bucket=aws_bucket_name)

    # Create a bucket policy
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [{
            "Sid": "AddPerm",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [
                f"arn:aws:s3:::{aws_bucket_name}",
                f"arn:aws:s3:::{aws_bucket_name}/*"]
        }]
    }
    # Convert the policy from JSON dict to string
    bucket_policy = json.dumps(bucket_policy)
    s3_client.put_bucket_policy(
        Bucket=aws_region_name, Policy=bucket_policy)
else:
    print("Bucket already exists!")

# Upload a file to S3
local_file_path = "./demo.txt"
file_name = "demo.txt"
s3_client.upload_file(
    local_file_path, aws_bucket_name, file_name)

# Add Line to the file
lambda_tmp_file_file = "./tmp/demo.txt"
s3_client.download_file(
    aws_bucket_name, file_name, lambda_tmp_file_file)
print("Downloaded file to ./tmp/demo.txt")

with open(lambda_tmp_file_file, "a") as f:
    f.write("\nHello World!2")
print("Added a line to the file")

# Upload the updated file to S3
s3_client.upload_file(
    lambda_tmp_file_file, aws_bucket_name, file_name)

# Delete the local file
os.remove('./tmp/demo.txt')
