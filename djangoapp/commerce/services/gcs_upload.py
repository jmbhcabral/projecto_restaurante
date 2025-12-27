# djangoapp/commerce/services/gcs_upload.py
import uuid
from dataclasses import dataclass
from typing import Optional

from django.conf import settings
from google.cloud import storage


@dataclass(frozen=True)
class GcsUploadResult:
    gcs_path: str
    public_url: Optional[str]


def upload_file_to_gcs(*, file_obj, content_type: str, folder: str) -> GcsUploadResult:
    bucket_name = getattr(settings, "GCS_BUCKET_NAME", "")
    if not bucket_name:
        raise ValueError("GCS_BUCKET_NAME is not configured")

    client = storage.Client()
    bucket = client.bucket(bucket_name)

    ext = "bin"
    if getattr(file_obj, "name", None) and "." in file_obj.name:
        ext = file_obj.name.rsplit(".", 1)[-1].lower()

    filename = f"{uuid.uuid4().hex}.{ext}"
    gcs_path = f"{folder}/{filename}"

    blob = bucket.blob(gcs_path)

    try:
        file_obj.seek(0)
    except Exception:
        pass

    blob.upload_from_file(file_obj, content_type=content_type)

    base = getattr(settings, "GCS_PUBLIC_BASE_URL", "")
    public_url = f"{base}/{gcs_path}" if base else None

    return GcsUploadResult(gcs_path=gcs_path, public_url=public_url)