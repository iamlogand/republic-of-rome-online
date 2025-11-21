import boto3
import os
import subprocess
import sys


ARCHIVE_NAME = "letsencrypt.tar.gz"
ARCHIVE_PATH = f"/tmp/{ARCHIVE_NAME}"
BUCKET_NAME = "api-roronline-com-ssl"

s3 = boto3.client("s3")


def create_archive():
    print(f"Creating tar.gz archive of /etc/letsencrypt")
    subprocess.run(
        ["tar", "-czf", ARCHIVE_PATH, "-C", "/etc", "letsencrypt"], check=True
    )
    print("Archive created")


def upload_archive():
    try:
        print(f"Uploading {ARCHIVE_PATH} to s3://{BUCKET_NAME}/{ARCHIVE_NAME}")
        s3.upload_file(ARCHIVE_PATH, BUCKET_NAME, ARCHIVE_NAME)
        print(f"Upload done")
    except Exception as e:
        print(f"Error uploading file: {str(e)}")


def download_archive():
    try:
        print(f"Downloading s3://{BUCKET_NAME}/{ARCHIVE_NAME} to {ARCHIVE_PATH}")
        os.makedirs(os.path.dirname(ARCHIVE_PATH), exist_ok=True)
        s3.download_file(BUCKET_NAME, ARCHIVE_NAME, ARCHIVE_PATH)
        print(f"Download done")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")


def extract_archive():
    print(f"Extracting {ARCHIVE_NAME} to /etc/")
    subprocess.run(["tar", "-xzf", ARCHIVE_PATH, "-C", "/etc/"], check=True)
    print("Extraction complete")


def clean_up():
    if os.path.exists(ARCHIVE_PATH):
        os.remove(ARCHIVE_PATH)
        print("Temporary archive deleted")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("upload", "download"):
        print("Incorrect args passed to s3_ssl_cert.py")

    mode = sys.argv[1]

    if mode == "upload":
        create_archive()
        upload_archive()
        clean_up()
    elif mode == "download":
        download_archive()
        extract_archive()
        clean_up()
