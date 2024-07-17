import unittest
from unittest.mock import patch, MagicMock
from azure.storage.blob import BlobServiceClient
from app.utils.azure_storage import AzureStorageManager

class TestAzureStorageManager(unittest.TestCase):

    @patch('app.utils.azure_storage.BlobServiceClient')
    def setUp(self, mock_blob_service_client):
        self.mock_blob_service_client = mock_blob_service_client
        self.storage_manager = AzureStorageManager("fake_connection_string")

    def test_upload_file(self):
        mock_blob_client = MagicMock()
        self.storage_manager.container_client.get_blob_client.return_value = mock_blob_client

        result = self.storage_manager.upload_file("test_file.txt", b"file content")

        self.assertTrue(result)
        mock_blob_client.upload_blob.assert_called_once_with(b"file content", overwrite=True)

    def test_download_file(self):
        mock_blob_client = MagicMock()
        self.storage_manager.container_client.get_blob_client.return_value = mock_blob_client
        mock_blob_client.download_blob.return_value.readall.return_value = b"file content"

        content = self.storage_manager.download_file("test_file.txt")

        self.assertEqual(content, b"file content")

    def test_list_files(self):
        mock_blob1 = MagicMock()
        mock_blob1.name = "file1.txt"
        mock_blob2 = MagicMock()
        mock_blob2.name = "file2.txt"
        self.storage_manager.container_client.list_blobs.return_value = [mock_blob1, mock_blob2]

        files = self.storage_manager.list_files()

        self.assertEqual(files, ["file1.txt", "file2.txt"])

    def test_delete_file(self):
        mock_blob_client = MagicMock()
        self.storage_manager.container_client.get_blob_client.return_value = mock_blob_client

        result = self.storage_manager.delete_file("test_file.txt")

        self.assertTrue(result)
        mock_blob_client.delete_blob.assert_called_once()

if __name__ == '__main__':
    unittest.main()
