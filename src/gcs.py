from google.cloud import storage
import logging


# Upload Blob to GCS
def upload_blob(bucket_name, source_file_name, destination_blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file_name)

        logging.info(f'File {source_file_name} uploaded to {destination_blob_name}')
        
    except Exception as ex:
        logging.error(ex)
#END upload_blob()

# Download Blob to GCS
def download_blob(bucket_name, source_blob_name, destination_file_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)

        blob.download_to_filename(destination_file_name)

        logging.info(f'File {source_blob_name} downloaded to {destination_file_name}')
        
    except Exception as ex:
        logging.error(ex)
#END download_blob()

def main():
    bucket_name='stage-3992'
    source_file_name='1.txt'
    destination_blob_name='1.txt'
    #upload_blob(bucket_name, source_file_name, destination_blob_name)

    source_blob_name='1.txt'
    destination_file_name='2.txt'
    download_blob(bucket_name, source_blob_name, destination_file_name)


if __name__ == "__main__":
    main()