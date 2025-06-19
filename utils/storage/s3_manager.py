import boto3
import json
import logging

logger = logging.getLogger(__name__)

class S3Manager:
    def __init__(self, bucket: str):
        self.s3 = boto3.client('s3')
        self.bucket = bucket
    
    def upload(self, key: str, data: dict) -> None:
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json_data,
            ContentType='application/json'
        )
        logger.info(f"Uploaded data to s3://{self.bucket}/{key}")
    
    def delete_prefix(self, prefix: str) -> int:
        """주어진 prefix로 시작하는 모든 S3 객체 삭제"""
        deleted_count = 0
        try:
            objects = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    self.s3.delete_object(
                        Bucket=self.bucket,
                        Key=obj['Key']
                    )
                    deleted_count += 1
                    logger.info(f"Deleted s3://{self.bucket}/{obj['Key']}")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete objects with prefix {prefix}: {str(e)}")
            raise e