import boto3
import os

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)


def upload_file(bucket, filename, key):
    try:
        print(f"Uploading {filename} to s3://{bucket}/{key}")
        s3.upload_file(filename, bucket, key)
        print(f"Upload done")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")


bucket_name = "api-roronline-com-ssl"
ssl_dir = "/etc/letsencrypt/live/api.roronline.com/"

upload_file(bucket_name, f"{ssl_dir}fullchain.pem", "fullchain.pem")
upload_file(bucket_name, f"{ssl_dir}privkey.pem", "privkey.pem")
