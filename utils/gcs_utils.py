from google.cloud import storage

def upload_to_gcs(
        local_path: str,
        bucket_name: str = "whisper-sync-audiofiles",
        gcs_path: str = "uploads/audio.wav"
    )->str:
    """ Upload audio to GCS and return URI """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} to GCS: gs://{bucket_name}/{gcs_path}")
    return f"gs://{bucket_name}/{gcs_path}"