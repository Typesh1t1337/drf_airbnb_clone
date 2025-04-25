from storages.backends.s3boto3 import S3Boto3Storage


class PFPStorage(S3Boto3Storage):
    bucket_name = "pfp"
    custom_domain = f"127.0.0.1:9000/{bucket_name}"
    file_overwrite = False

    def url(self, name):
        url = super().url(name)
        return url.replace("https://", "http://")