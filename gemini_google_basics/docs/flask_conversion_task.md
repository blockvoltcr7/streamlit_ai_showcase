# Task: Convert Video Analysis Script to Secure Flask Application

**Goal:** Transform the Python script `gemini_google_basics/gemini_video_analysis_url_loop.py` into a robust and secure Flask application.

**Current Script Functionality:**
- Takes a hardcoded list of video URLs.
- Downloads each video locally to a temporary file.
- Uploads the temporary file to the Gemini API.
- Waits for the file status to become `ACTIVE`.
- Sends the file URI and a predefined prompt to the Gemini `gemini-1.5-flash` model for analysis.
- Prints the streaming response chunks to the console.
- Collects results (attempting JSON parsing) or errors for each URL.
- Writes the collected results to a local JSON file.
- Cleans up temporary files.

**Flask Application Requirements:**

1.  **Framework:** Use Flask.
2.  **Endpoint:**
    *   Create a POST route (e.g., `/analyze_videos`) using `@app.route('/analyze_videos', methods=['POST'])`.
    *   This endpoint should accept a JSON request body containing a list of video URLs. Access it via `request.get_json()`, which should look like: `{"urls": ["url1", "url2", ...]}`.
3.  **Security:**
    *   Implement header-based authentication.
    *   The API should expect a specific header (e.g., `X-API-Secret`) in `request.headers`.
    *   Define a secret key (configurable, perhaps via environment variable).
    *   Requests without the correct secret header value should return an appropriate response with a `403 Forbidden` or `401 Unauthorized` status code (e.g., using `jsonify` and returning a tuple `(response, status_code)`).
4.  **Core Logic (Refactor from script):**
    *   Integrate the video downloading, uploading, status checking, and Gemini API call logic within the route function.
    *   **Crucially:** Modify the Gemini API interaction to **aggregate the complete response** for each video, rather than just printing chunks. The goal is to capture the full JSON output from the model for each analysis.
    *   Handle potential errors during download, upload, or analysis for each URL gracefully.
5.  **Response:**
    *   Collect the full analysis results (ideally parsed JSON objects) for each successfully processed URL. Include the original URL alongside its analysis or any error message.
    *   Combine these individual results into a single JSON array structure.
    *   Return this combined JSON array as the response body using Flask's `jsonify()` function with a `200 OK` status. Example structure:
        ```json
        [
          {
            "url": "url1",
            "status": "success",
            "analysis": { ... parsed JSON analysis ... }
          },
          {
            "url": "url2",
            "status": "error",
            "error_message": "Failed to download video."
          },
          {
            "url": "url3",
            "status": "success",
            "analysis": { ... parsed JSON analysis ... }
           }
        ]
        ```
    *   Ensure the response is pure JSON.
6.  **Dependencies:**
    *   Create a `requirements.txt` file listing all necessary dependencies (Flask, google-generativeai, requests, python-dotenv, a production WSGI server like Gunicorn or Waitress, etc.).
7.  **Configuration:**
    *   Manage sensitive information like the `GEMINI_API_KEY` and the `X-API-Secret` value using environment variables (e.g., using `python-dotenv` and `os.environ.get`).
8.  **Error Handling:** Implement robust error handling for API requests, network issues, Gemini API errors, and file operations. Return appropriate JSON error responses and HTTP status codes using Flask's error handling mechanisms (e.g., `abort` or custom error handlers).
9.  **Asynchronous Processing (Optional but Recommended):** Flask supports `async/await` routes. Consider making the video processing asynchronous (`async def` route) to handle multiple requests efficiently and avoid blocking the server during long I/O operations (downloads, API calls). Use an async-capable library like `aiohttp` or `httpx` for external requests.
10. **Documentation (Optional):** While Flask doesn't have built-in automatic documentation like FastAPI, consider using extensions like Flask-RESTx or Flasgger if API documentation is desired. Otherwise, provide clear manual documentation (e.g., in a README) explaining endpoint usage, headers, and formats.

**Deliverables:**
- A functional Flask application (`app.py` or similar).
- A `requirements.txt` file.
- Clear instructions on how to run the application (including WSGI server command) and configure environment variables. 