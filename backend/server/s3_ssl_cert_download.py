import boto3
import os

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
)


def download_file(bucket, key, filename):
    try:
        print(f"Downloading s3://{bucket}/{key} to {filename}")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        s3.download_file(bucket, key, filename)
        print(f"Download done")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")


bucket_name = "api-roronline-com-ssl"
ssl_dir = "/etc/letsencrypt/live/api.roronline.com,temp.roronline.com/"

download_file(bucket_name, "fullchain.pem", f"{ssl_dir}fullchain.pem")
download_file(bucket_name, "privkey.pem", f"{ssl_dir}privkey.pem")
