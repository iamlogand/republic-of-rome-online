import boto3
import os

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_DEFAULT_REGION')
)

def download_file(bucket, key, filename):
    try:
        s3.download_file(bucket, key, filename)
        print(f"Downloaded {key} to {filename}")
    except Exception as e:
        print(f"Error downloading {key}: {str(e)}")

download_file('api-roronline-com-ssl', 'api_roronline_com.crt', '/etc/nginx/ssl/api_roronline_com.crt')
download_file('api-roronline-com-ssl', 'certificate.key', '/etc/nginx/ssl/certificate.key')
download_file('api-roronline-com-ssl', 'ca_bundle.crt', '/etc/nginx/ssl/ca_bundle.crt')
