import json
import time
from typing import Any, Dict, Optional

import requests
import streamlit as st

# Configure page settings
st.set_page_config(page_title="S3 Bucket Manager", page_icon="🪣", layout="wide")

# Constants
API_BASE_URL = "http://127.0.0.1:8000"  # Update with your actual API base URL

"""
S3 Bucket Manager Application

This application provides a user interface for managing Amazon S3 buckets. 
It allows users to perform various operations such as listing buckets, 
creating new buckets, viewing bucket details, and creating buckets with folders.

Modules:
- json: For formatting JSON data.
- time: For handling time-related functions (currently unused).
- typing: For type hinting in function signatures.
- requests: For making HTTP requests to the API.
- streamlit: For creating the web application interface.

Functions:
1. make_api_request(endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
   Makes API requests to the specified endpoint using the given HTTP method and parameters.
   Returns the JSON response as a dictionary.

2. format_json(data: Dict[str, Any]) -> str:
   Formats the given dictionary into a pretty-printed JSON string.

3. check_api_status() -> bool:
   Checks if the API is accessible by sending a GET request to the /buckets/ endpoint.
   Returns True if the API is reachable, otherwise returns False.

4. render_sidebar():
   Renders the sidebar of the application, displaying the API status and additional information.

5. list_buckets_tab():
   Renders the tab for listing all S3 buckets. 
   Provides a button to refresh the bucket list and displays the retrieved buckets.

6. create_bucket_tab():
   Renders the tab for creating a new S3 bucket. 
   Allows users to input a bucket name and select a region, then submits the data to create the bucket.

7. bucket_details_tab():
   Renders the tab for viewing details of a specific S3 bucket. 
   Users can input a bucket name to retrieve and display its details.

8. create_bucket_with_folder_tab():
   Renders the tab for creating a new S3 bucket along with a folder. 
   Users can input a bucket name, select a region, and specify a folder name.

9. main():
   The main function that initializes the Streamlit application, 
   renders the sidebar, and sets up the main content tabs.

Usage:
Run this script to start the S3 Bucket Manager application. 
Ensure that the API is running and accessible at the specified API_BASE_URL.
"""

# Helper functions
def make_api_request(
    endpoint: str, method: str = "GET", params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Makes API requests and handles responses."""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        with st.spinner("Processing request..."):
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                response = requests.post(url, params=params)

            response.raise_for_status()
            return response.json()
    except requests.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {}


def format_json(data: Dict[str, Any]) -> str:
    """Formats JSON data for display."""
    return json.dumps(data, indent=2)


def check_api_status() -> bool:
    """Checks if the API is accessible."""
    try:
        requests.get(API_BASE_URL + "/buckets/")
        return True
    except requests.RequestException:
        return False


# Sidebar content
def render_sidebar():
    st.sidebar.title("S3 Bucket Manager")
    st.sidebar.markdown("---")

    # API Status
    api_status = check_api_status()
    status_color = "🟢" if api_status else "🔴"
    st.sidebar.write(f"API Status: {status_color}")

    # Additional sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
    This application allows you to:
    - List all S3 buckets
    - Create new buckets
    - View bucket details
    - Create buckets with folders
    """
    )


# Main content sections
def list_buckets_tab():
    st.header("List Buckets")

    if st.button("Refresh Bucket List"):
        response = make_api_request("/buckets/")
        if response:
            st.success("Successfully retrieved buckets!")
            st.json(response)
        else:
            st.warning("No buckets found or unable to retrieve bucket list.")


def create_bucket_tab():
    st.header("Create Bucket")

    with st.form("create_bucket_form"):
        bucket_name = st.text_input("Bucket Name (optional)")
        region = st.selectbox(
            "Region",
            ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1"],
            index=0,
        )

        submit_button = st.form_submit_button("Create Bucket")

        if submit_button:
            params = {"region": region}
            if bucket_name:
                params["bucket_name"] = bucket_name

            response = make_api_request("/buckets/create", method="POST", params=params)
            if response:
                st.success("Bucket created successfully!")
                st.json(response)


def bucket_details_tab():
    st.header("Bucket Details")

    bucket_name = st.text_input("Enter Bucket Name")
    if bucket_name and st.button("Get Details"):
        response = make_api_request(f"/buckets/{bucket_name}")
        if response:
            st.success(f"Retrieved details for bucket: {bucket_name}")
            st.json(response)


def create_bucket_with_folder_tab():
    st.header("Create Bucket with Folder")

    with st.form("create_bucket_with_folder_form"):
        bucket_name = st.text_input("Bucket Name (optional)")
        region = st.selectbox(
            "Region",
            ["us-east-1", "us-west-1", "us-west-2", "eu-west-1", "eu-central-1"],
            index=0,
        )
        folder_name = st.text_input("Folder Name", value="new-folder/")

        submit_button = st.form_submit_button("Create Bucket with Folder")

        if submit_button:
            params = {"region": region, "folder_name": folder_name}
            if bucket_name:
                params["bucket_name"] = bucket_name

            response = make_api_request(
                "/buckets/create-with-folder", method="POST", params=params
            )
            if response:
                st.success("Bucket and folder created successfully!")
                st.json(response)


def main():
    st.title("S3 Bucket Management")

    # Render sidebar
    render_sidebar()

    # Main content tabs
    tabs = st.tabs(
        ["List Buckets", "Create Bucket", "Bucket Details", "Create with Folder"]
    )

    with tabs[0]:
        list_buckets_tab()

    with tabs[1]:
        create_bucket_tab()

    with tabs[2]:
        bucket_details_tab()

    with tabs[3]:
        create_bucket_with_folder_tab()


if __name__ == "__main__":
    main()
