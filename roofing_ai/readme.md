# Document Vector Store Manager

The Document Vector Store Manager is a Python-based application that allows users to upload, manage, and search documents using Pinecone and OpenAI's embeddings. This tool is designed to facilitate efficient document management and retrieval through a user-friendly interface.

## Prerequisites

Before you begin, ensure you have met the following requirements:

1. **Python**: Make sure you have Python 3.8 or later installed on your system.
2. **OpenAI Account**: Create an account on [OpenAI](https://openai.com/) and obtain an API key.
3. **Pinecone Account**: Create an account on [Pinecone](https://www.pinecone.io/) and obtain an API key.

## Setup Instructions

Follow these steps to set up and run the project:

1. **Open the project**:
   ```bash
   cd project directory
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory and add your API keys:
     ```
     OPENAI_API_KEY=your_openai_api_key
     PINECONE_API_KEY=your_pinecone_api_key
     ```

6. **Run the Application**:
   - Navigate to the `streamlit` directory:
     ```bash
     cd streamlit
     ```
   - Start the Streamlit application:
     ```bash
     streamlit run home.py
     ```

## Usage

- **Upload Documents**: Use the "Upload Documents" page to upload documents and manage their metadata.
- **View and Manage Indexes**: Use the "View & Manage Indexes" page to search documents and manage namespaces.
- **Chat Interface**: Use the "Chat with Documents" page to interact with the document store using natural language queries.

## Additional Suggestions

- **Testing**: Consider running the test scripts located in the `tests` directory to ensure everything is set up correctly.
- **Documentation**: Add more detailed documentation for each module and function to help new developers understand the codebase.
- **Error Handling**: Review and enhance error handling to provide more informative messages to users.
- **Security**: Ensure that sensitive information, such as API keys, is securely managed and not exposed in the codebase.

## Contributing

If you would like to contribute to this project, please fork the repository and submit a pull request. We welcome all contributions that improve the functionality and usability of the application.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

---

This README provides a comprehensive guide to setting up and using the Document Vector Store Manager, along with suggestions for further improvements.
