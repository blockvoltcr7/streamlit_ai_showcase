import requests
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

##exmaple doc: https://docs.eraser.io/docs/entity-relationship-diagrams


# Fetch the API key from environment variables
api_key = os.getenv("ERASER_IO_API_KEY")
if api_key is None:
    raise ValueError("ERASER_IO_API_KEY environment variable is not set")


url = "https://app.eraser.io/api/render/prompt"

text = """
// SQL schema creation script

CREATE TABLE CART
(
  ID INTEGER PRIMARY KEY NOT NULL,
  CUSTOMER_ID INTEGER NOT NULL,
  NAME VARCHAR(50) NOT NULL
);
CREATE TABLE CART_ITEM
(
  CART_ID INTEGER NOT NULL,
  PRODUCT_ID INTEGER NOT NULL,
  ITEM_QTY INTEGER NOT NULL,
  LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP() NOT NULL,
  PRIMARY KEY ( CART_ID, PRODUCT_ID )
);
CREATE TABLE CATEGORY
(
  ID INTEGER PRIMARY KEY NOT NULL,
  NAME VARCHAR(50) NOT NULL,
  DESCRIPTION CLOB
);
CREATE TABLE CUSTOMER
(
  ID INTEGER PRIMARY KEY NOT NULL,
  NAME VARCHAR(100) NOT NULL,
  PASSWORD VARCHAR(20) NOT NULL,
  LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP() NOT NULL,
  REGISTRATION_DATE DATE DEFAULT CURRENT_DATE() NOT NULL
);
CREATE TABLE PRODUCT
(
  ID INTEGER PRIMARY KEY NOT NULL,
  NAME VARCHAR(50) NOT NULL,
  DESCRIPTION CLOB NOT NULL,
  PRICE DECIMAL(5,2) NOT NULL,
  STOCK_QTY INTEGER NOT NULL,
  LAST_UPDATED TIMESTAMP DEFAULT CURRENT_TIMESTAMP() NOT NULL,
  CATEGORY_ID INTEGER NOT NULL
);
ALTER TABLE CART ADD FOREIGN KEY ( CUSTOMER_ID ) REFERENCES CUSTOMER ( ID );
CREATE INDEX FK_CUSTOMERCART_INDEX_1 ON CART ( CUSTOMER_ID );
ALTER TABLE CART_ITEM ADD FOREIGN KEY ( CART_ID ) REFERENCES CART ( ID );
ALTER TABLE CART_ITEM ADD FOREIGN KEY ( PRODUCT_ID ) REFERENCES PRODUCT ( ID );
CREATE INDEX FK_CARTITEMPRODUCT_INDEX_B ON CART_ITEM ( PRODUCT_ID );
CREATE UNIQUE INDEX UNIQUE_NAME_INDEX_F ON CATEGORY ( NAME );
ALTER TABLE PRODUCT ADD FOREIGN KEY ( CATEGORY_ID ) REFERENCES CATEGORY ( ID );
CREATE INDEX FK_PRODUCTCATEGORY_INDEX_1 ON PRODUCT ( CATEGORY_ID );
"""

payload = {
    "text": text, 
    "diagramType": "entity-relationship-diagram",
    "background": True,
    "theme": "light",
    "scale": "3",
    "returnFile": True
}

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {api_key}"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for bad status codes

    #print status code
    print(f"Status code: {response.status_code}")

    # Print the response text
    print("Response:")
    print(response.content)
    
    # Print response headers
    print("Response Headers:")
    print(response.headers)

    # Create the output directory if it doesn't exist
    output_dir = os.path.join("output", "entity-relationship-diagram")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a random file name
    random_file_name = f"entity-relationship-diagram{uuid.uuid4().hex}.png"
    output_path = os.path.join(output_dir, random_file_name)
    
    print(f"Image saved successfully at: {output_path}")

except requests.RequestException as e:
    print(f"Error making request: {e}")
except IOError as e:
    print(f"Error saving file: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")