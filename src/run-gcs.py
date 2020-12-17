import gcs

# Example Upload
bucket_name='stage-3992'
source_file_name='1.txt'
destination_blob_name='1.txt'
#gcs.upload_blob(bucket_name, source_file_name, destination_blob_name)

# Example Download
source_blob_name='1.txt'
destination_file_name='2.txt'
gcs.download_blob(bucket_name, source_blob_name, destination_file_name)