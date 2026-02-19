"""
Cloudflare R2 — Free object storage (10GB, S3-compatible)
Used for: screenshots, output files, deployed sites
"""

import boto3
import os
import base64
from typing import Optional

class Storage:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f"https://{os.getenv('R2_ACCOUNT_ID')}.r2.cloudflarestorage.com",
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            region_name='auto',
        )
        self.bucket = os.getenv('R2_BUCKET_NAME', 'luxor9-files')
        self.public_url = os.getenv('R2_PUBLIC_URL', '')

    def upload_file(self, key: str, data: bytes, content_type: str = 'application/octet-stream') -> str:
        """Upload a file and return its public URL."""
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"{self.public_url}/{key}"

    def upload_screenshot(self, task_id: str, turn: int, screenshot_b64: str) -> str:
        """Upload a browser screenshot."""
        data = base64.b64decode(screenshot_b64)
        key = f"screenshots/{task_id}/{turn}.png"
        return self.upload_file(key, data, 'image/png')

    def upload_task_file(self, task_id: str, filename: str, data: bytes, content_type: str = None) -> str:
        """Upload a task output file."""
        key = f"files/{task_id}/{filename}"
        ct = content_type or self._guess_content_type(filename)
        return self.upload_file(key, data, ct)

    def get_download_url(self, key: str, expires: int = 3600) -> str:
        """Generate a pre-signed download URL."""
        return self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=expires,
        )

    def _guess_content_type(self, filename: str) -> str:
        ext_map = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.pdf': 'application/pdf',
            '.md': 'text/markdown',
        }
        for ext, ct in ext_map.items():
            if filename.endswith(ext):
                return ct
        return 'application/octet-stream'

storage = Storage()
