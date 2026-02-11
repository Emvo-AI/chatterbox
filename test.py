import json
import os
import base64
from src.handler import handler

def run_test():
    # 1. Settings
    audio_file_path = "dipankar.wav"
    
    # 2. Check if the audio file exists
    if not os.path.exists(audio_file_path):
        print(f"❌ Error: '{audio_file_path}' not found!")
        return

    # 3. Read the file and convert to Base64
    print(f"Reading {audio_file_path}...")
    with open(audio_file_path, "rb") as audio_file:
        encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')

    # 4. Construct the input data with the Base64 string
    input_data = {
        "input": {
            "text": "अधूरी हसरतों का इल्जाम हर बार किस्मत पर लगाना ठीक नहीं,कुछ कसर तो हमारी कोशिशों में भी रही होगी। माँ की गोद में सिर रखते ही सारे दर्द मिट जाते हैं... काश! ये सुकून भरी घड़ियाँ कभी खत्म ही न होतीं।",
            "audio_b64": encoded_string,  # This is now populated
            "audio_prompt_path": "my_voice_sample.wav", # Optional, since b64 is present
            "language_id": "hi"
        }
    }

    # 5. Save the final JSON to test_input.json (so you can see it)
    with open("test_input.json", "w", encoding="utf-8") as f:
        json.dump(input_data, f, ensure_ascii=False, indent=4)
    print("✅ Created test_input.json with Base64 audio.")

    # 6. Call the handler logic
    print("🚀 Triggering handler.py...")
    response = handler(input_data)

    # 7. Process the response
    if "error" in response:
        print(f"❌ Handler Error: {response['error']}")
    else:
        print("✅ Success!")
        output_audio = base64.b64decode(response["audio_base64"])
        with open("output_result.wav", "wb") as f:
            f.write(output_audio)
        print("📁 Result saved as 'output_result.wav'")

if __name__ == "__main__":
    run_test()