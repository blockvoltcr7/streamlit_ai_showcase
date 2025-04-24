import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your API key from environment variable
# Ensure GEMINI_API_KEY is set in your .env file or environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")
genai.configure(api_key=api_key)

def transcribe_audio_bytes(audio_bytes: bytes, mime_type: str = "audio/mpeg"):
    """Transcribes audio file bytes using the Gemini API.

    Args:
        audio_bytes: The bytes of the audio file.
        mime_type: The mime type of the audio file (e.g., "audio/mpeg", "audio/wav").
                   Defaults to "audio/mpeg".

    Returns:
        The transcription as a string, or None if there's an error.
    """
    try:
        # Use the recommended stable model
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

        # Prepare the audio data part for the API request
        audio_file_part = {
            "mime_type": mime_type,
            "data": audio_bytes,
        }

        # Prepare the full request content
        prompt = "Transcribe the audio." # Simple transcription prompt
        contents = [
           {"parts": [audio_file_part, {"text": prompt}]}
        ]

        # Generate the transcription
        response = model.generate_content(contents=contents)

        # Check if response contains text
        if hasattr(response, 'text') and response.text:
            return response.text
        else:
            # Log potential issues if response structure is unexpected or text is empty
            print(f"Warning: Transcription successful but returned empty text or unexpected response format.")
            # Attempt to access text via parts if direct access fails (though less common for text-only responses)
            try:
                return response.parts[0].text if response.parts else "Transcription result empty."
            except (AttributeError, IndexError):
                 print(f"Error: Could not extract text from response parts.")
                 return None


    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        return None

if __name__ == '__main__':
    # --- Configuration ---
    # Replace with the actual path to YOUR audio file
    audio_file_path = '../audio/kratos_1.mp3'
    # Ensure this matches the actual format of your audio file!
    # Common types: "audio/mpeg" (MP3), "audio/wav", "audio/ogg", "audio/flac", "audio/aac"
    mime_type_of_audio = "audio/mpeg"
    # --- End Configuration ---

    print(f"Attempting to transcribe: {audio_file_path} (MIME Type: {mime_type_of_audio})")

    try:
        with open(audio_file_path, "rb") as audio_file:
            audio_data = audio_file.read()
        print(f"Successfully read {len(audio_data)} bytes from the audio file.")
    except FileNotFoundError:
        print(f"Error: Audio file not found at '{audio_file_path}'. Please check the path.")
        exit()
    except Exception as e:
        print(f"Error reading audio file: {e}")
        exit()

    # Perform the transcription
    transcription = transcribe_audio_bytes(audio_data, mime_type=mime_type_of_audio)

    # Output the result
    if transcription:
        print("\n--- Transcription ---")
        print(transcription)
        print("--- End Transcription ---")
    else:
        print("\nTranscription failed.")