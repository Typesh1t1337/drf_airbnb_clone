from storages.backends.s3boto3 import S3Boto3Storage

class PFPStorage(S3Boto3Storage):
    bucket_name = "pfp"
    custom_domain = f"http://airbnb_minio:9000/{bucket_name}"
    file_overwrite = False