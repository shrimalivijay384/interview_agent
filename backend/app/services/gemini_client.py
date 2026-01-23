"""
Google Gemini API client for LLM operations.
"""
import google.generativeai as genai
from typing import Optional, List, Dict, Any
import json
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self):
        """Initialize Gemini client with API key and configuration."""
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        self.temperature = settings.gemini_temperature
        self.max_tokens = settings.gemini_max_tokens
        
        # Generation config
        self.generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )
        
        logger.info(f"Gemini client initialized with model: {self.model_name}")
    
    async def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Send a chat request to Gemini.
        
        Args:
            system_prompt: System/context prompt
            user_prompt: User's actual prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Whether to request JSON output
            
        Returns:
            Model's response as string
        """
        try:
            # Combine system and user prompts
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            if json_mode:
                full_prompt += "\n\nPlease respond with valid JSON only, no additional text."
            
            # Override config if specified
            config = self.generation_config.copy()
            if temperature is not None:
                config["temperature"] = temperature
            if max_tokens is not None:
                config["max_output_tokens"] = max_tokens
            
            # Create model with custom config if needed
            if temperature is not None or max_tokens is not None:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config=config
                )
            else:
                model = self.model
            
            # Generate response
            response = model.generate_content(full_prompt)
            
            result = response.text.strip()
            
            logger.debug(f"Gemini response received (length: {len(result)})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini chat: {str(e)}")
            raise
    
    async def chat_with_json_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Send a chat request expecting JSON response.
        
        Args:
            system_prompt: System/context prompt
            user_prompt: User's actual prompt
            temperature: Override default temperature
            
        Returns:
            Parsed JSON response as dictionary
        """
        try:
            response_text = await self.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                json_mode=True
            )
            
            # Try to extract JSON from response
            # Sometimes the model wraps JSON in ```json ... ```
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Gemini response: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Error in Gemini JSON chat: {str(e)}")
            raise
    
    async def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None
    ) -> str:
        """
        Send a chat request with conversation history.
        
        Args:
            messages: List of messages with 'role' and 'content'
            temperature: Override default temperature
            
        Returns:
            Model's response as string
        """
        try:
            # Build conversation
            chat = self.model.start_chat(history=[])
            
            # Send messages
            for msg in messages[:-1]:  # All but last
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
            
            # Send final message and get response
            response = chat.send_message(messages[-1]["content"])
            
            result = response.text.strip()
            logger.debug(f"Gemini response received (length: {len(result)})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini chat with history: {str(e)}")
            raise


# Global instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create global Gemini client instance."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
