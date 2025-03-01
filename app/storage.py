from storages.backends.s3boto3 import S3Boto3Storage
class HousingStorage(S3Boto3Storage):
    bucket_name = 'housing'
    file_overwrite = False
    custom_domain = f"http://airbnb_minio:9000/{bucket_name}"