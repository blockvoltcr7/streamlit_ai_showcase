import pytest
import os
from azure.storage.blob import BlobServiceClient
from app.utils.azure_storage import AzureStorageManager

@pytest.fixture
def azure_storage_manager():
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not connection_string:
        pytest.skip("Azure Storage connection string not found in environment variables")
    return AzureStorageManager(connection_string)

def test_upload_file(azure_storage_manager):
    # Create a temporary file for testing
    test_file_name = "test_upload.txt"
    test_file_content = b"This is a test file for Azure Blob Storage upload"
    
    with open(test_file_name, "wb") as f:
        f.write(test_file_content)
    
    try:
        # Upload the file
        result = azure_storage_manager.upload_file(test_file_name, test_file_content)
        
        # Assert that the upload was successful
        assert result == True
        
        # Verify that the file exists in the blob storage
        blob_client = azure_storage_manager.container_client.get_blob_client(test_file_name)
        assert blob_client.exists()
        
        # Download and check the content
        downloaded_content = azure_storage_manager.download_file(test_file_name)
        assert downloaded_content == test_file_content
        
    finally:
        # Clean up: delete the local file and the uploaded blob
        os.remove(test_file_name)
        azure_storage_manager.delete_file(test_file_name)
