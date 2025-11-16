from google import genai
from django.conf import settings
import json
import re
import time
import logging

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def ask_gemini(prompt: str) -> str:
    """Basic text response from Gemini"""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise


def ask_gemini_json(prompt: str, model="gemini-2.5-flash", attempts=3, backoff=1.5) -> dict:
    """
    Request JSON-formatted response from Gemini with retries.
    
    Args:
        prompt: Question to ask (should explicitly request JSON output)
        model: Gemini model to use
        attempts: Number of retry attempts
        backoff: Exponential backoff multiplier between retries
    
    Returns:
        Parsed JSON dict
    
    Raises:
        ValueError: If no valid JSON is found after all attempts
    """
    last_exc = None
    
    for attempt in range(1, attempts + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            
            text = response.text if hasattr(response, 'text') else str(response)
            
            # Extract JSON object from response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if not json_match:
                raise ValueError("No JSON object found in response")
            
            # Parse and validate JSON
            data = json.loads(json_match.group())
            logger.info(f"✓ Gemini JSON received on attempt {attempt}")
            return data
        
        except json.JSONDecodeError as e:
            last_exc = e
            logger.warning(f"JSON decode error (attempt {attempt}/{attempts}): {e}")
        except Exception as e:
            last_exc = e
            logger.warning(f"Gemini error (attempt {attempt}/{attempts}): {e}")
        
        # Wait before retry with exponential backoff
        if attempt < attempts:
            wait_time = backoff ** attempt
            time.sleep(wait_time)
    
    # All attempts failed
    logger.error(f"Failed to get valid JSON from Gemini after {attempts} attempts")
    raise ValueError(f"Gemini JSON parsing failed: {last_exc}")