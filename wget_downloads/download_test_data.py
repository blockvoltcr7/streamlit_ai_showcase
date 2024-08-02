import os
import requests

def download_file(url, filename):
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad responses
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded: {filename}")

# Create data directory if it doesn't exist
os.makedirs('testdata', exist_ok=True)

# List of files to download
files = [
    ("https://www.dropbox.com/scl/fi/t1soxfjdp0v44an6sdymd/drake_kendrick_beef.pdf?rlkey=u9546ymb7fj8lk2v64r6p5r5k&dl=1", "testdata/drake_kendrick_beef.pdf"),
    ("https://www.dropbox.com/scl/fi/nts3n64s6kymner2jppd6/drake.pdf?rlkey=hksirpqwzlzqoejn55zemk6ld&dl=1", "testdata/drake.pdf"),
    ("https://www.dropbox.com/scl/fi/8ax2vnoebhmy44bes2n1d/kendrick.pdf?rlkey=fhxvn94t5amdqcv9vshifd3hj&dl=1", "testdata/kendrick.pdf")
]

# Download each file
for url, filename in files:
    download_file(url, filename)

print("All files downloaded successfully.")