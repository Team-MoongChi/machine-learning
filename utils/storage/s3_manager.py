import boto3
import json
import logging

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self, bucket: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
    
    def upload(self, key: str, data: dict) -> None:
        json_data = json.dumps(data)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json_data,
            ContentType='application/json'
        )
        logger.info(f"Uploaded data to s3://{self.bucket}/{key}")