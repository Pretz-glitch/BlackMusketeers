import os
import json
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

# Configure the API key using the environment variable
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def classify_dress(image_path: str) -> dict:
    """
    Classifies a dress image into season, style, and color.
    Uses Gemini API to process the image and return a JSON match.
    """
    try:
        # Load the image
        img = Image.open(image_path)
        
        # We will use gemini-2.5-flash as it's the updated fast model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """
        Analyze this image of a dress/clothing item. 
        Extract the following information and output ONLY a JSON object:
        1. 'season': (e.g., Summer, Winter, Spring, Autumn, or All-season)
        2. 'style': (e.g., Formal, Casual, Party, Workwear, etc.)
        3. 'color': (dominant color(s) of the dress)
        
        Format the output purely as a valid JSON object like so:
        {
            "season": "Summer",
            "style": "Casual",
            "color": "Red"
        }
        """
        
        response = model.generate_content(
            [prompt, img],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        raw_text = response.text
        # Parse the JSON response
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        
        result = json.loads(raw_text)
        return {
            "season": result.get("season", "Unknown"),
            "style": result.get("style", "Unknown"),
            "color": result.get("color", "Unknown")
        }
        
    except Exception as e:
        print(f"Error classifying image: {e}")
        # Return the error message inside the object so we can debug it
        return {
            "season": "Unknown",
            "style": "Unknown",
            "color": "Unknown",
            "error_msg": str(e)
        }
