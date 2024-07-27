import os
import random
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from dotenv import load_dotenv

load_dotenv()

# Azure configuration
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")

# Azure configuration
RESOURCE_GROUP = "dev_env_learning"
LOCATION = "eastus"
STORAGE_ACCOUNT_BASE = "devenvstreamlitappsai"

def generate_random_sequence(length):
    return ''.join(random.choices('0123456789', k=length))

def main():
    # Create credential object
    credential = AzureCliCredential()

    # Create clients
    resource_client = ResourceManagementClient(credential, AZURE_SUBSCRIPTION_ID)
    storage_client = StorageManagementClient(credential, AZURE_SUBSCRIPTION_ID)

    # Create resource group
    print(f"Creating resource group {RESOURCE_GROUP}...")
    resource_client.resource_groups.create_or_update(
        RESOURCE_GROUP,
        {"location": LOCATION}
    )

    # Generate a unique storage account name
    random_sequence = generate_random_sequence(3)
    storage_account_name = f"{STORAGE_ACCOUNT_BASE}{random_sequence}"

    # Create storage account
    print(f"Creating storage account {storage_account_name}...")
    poller = storage_client.storage_accounts.begin_create(
        RESOURCE_GROUP,
        storage_account_name,
        {
            "location": LOCATION,
            "kind": "StorageV2",
            "sku": {"name": "Standard_LRS"}
        }
    )
    account_result = poller.result()
    print(f"Storage account {account_result.name} created.")

    print("Script execution completed successfully!")

if __name__ == "__main__":
    main()