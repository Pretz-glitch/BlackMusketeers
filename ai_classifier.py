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
        Analyze this image of a clothing item.
        Extract the following information and output ONLY a JSON object:
        1. 'season': (e.g., Summer, Winter, Spring, Autumn, or All-season)
        2. 'clothing_type': (must be exactly one of: Top, Bottom, Full, Footwear, Accessory)
        3. 'style': (e.g., Formal, Casual, Party, Loungewear, Workwear, Athletic, etc.)
        4. 'aesthetic': (e.g., Flashy, Minimalist, Vintage, Streetwear, Elegant)
        5. 'color_theme': (e.g., Dark, Light, Vibrant, Pastel, Neutral)
        6. 'color_hue': (e.g., Navy Blue, Crimson Red, Olive Green, Black, White)
        7. 'fabric': (e.g., Cotton, Denim, Silk, Leather, Synthetics, Wool)
        
        Format the output purely as a valid JSON object like so:
        {
            "season": "Summer",
            "clothing_type": "Top",
            "style": "Casual",
            "aesthetic": "Minimalist",
            "color_theme": "Light",
            "color_hue": "White",
            "fabric": "Cotton"
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
            "clothing_type": result.get("clothing_type", "Unknown"),
            "style": result.get("style", "Unknown"),
            "aesthetic": result.get("aesthetic", "Unknown"),
            "color_theme": result.get("color_theme", "Unknown"),
            "color_hue": result.get("color_hue", "Unknown"),
            "fabric": result.get("fabric", "Unknown")
        }
        
    except Exception as e:
        print(f"Error classifying image: {e}")
        # Return the error message inside the object so we can debug it
        return {
            "season": "Unknown",
            "clothing_type": "Unknown",
            "style": "Unknown",
            "aesthetic": "Unknown",
            "color_theme": "Unknown",
            "color_hue": "Unknown",
            "fabric": "Unknown",
            "error_msg": str(e)
        }
