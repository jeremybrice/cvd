"""
Claude API Client with retry logic and token optimization
"""

import os
import time
import json
import logging
from typing import Optional, Dict, Any, List
from functools import wraps
import anthropic
from anthropic import Anthropic, RateLimitError as AnthropicRateLimitError

from .exceptions import AIServiceError, RateLimitError, TokenLimitError

logger = logging.getLogger(__name__)


def exponential_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for exponential backoff retry logic"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except AnthropicRateLimitError as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Rate limit hit, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        raise RateLimitError(f"Rate limit exceeded after {max_retries} attempts") from e
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"API error: {e}, retrying in {delay}s")
                        time.sleep(delay)
                    else:
                        raise AIServiceError(f"API call failed after {max_retries} attempts: {str(e)}") from e
            
            raise last_exception
        return wrapper
    return decorator


class AIClient:
    """
    Claude API client with optimizations for the CVD application
    """
    
    DEFAULT_MODEL = "claude-3-haiku-20240307"  # Fast, cost-effective for real-time scoring
    ADVANCED_MODEL = "claude-3-opus-20240229"  # More capable for complex analysis
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AI client
        
        Args:
            api_key: Optional API key (defaults to environment variable)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            logger.warning("No API key provided. AI features will use fallback mode.")
            self.client = None
            self.fallback_mode = True
        else:
            try:
                self.client = Anthropic(api_key=self.api_key)
                self.fallback_mode = False
                logger.info("Claude API client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
                self.client = None
                self.fallback_mode = True
        
        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.request_count = 0
    
    @exponential_backoff(max_retries=3)
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.3,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from Claude
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt for context
            model: Model to use (defaults to fast model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0-1)
            **kwargs: Additional parameters for the API
        
        Returns:
            Dictionary with response and metadata
        """
        if self.fallback_mode:
            return self._fallback_completion(prompt)
        
        model = model or self.DEFAULT_MODEL
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self.client.messages.create(
                model=model,
                messages=messages,
                system=system_prompt if system_prompt else None,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Track usage
            self.total_input_tokens += response.usage.input_tokens
            self.total_output_tokens += response.usage.output_tokens
            self.request_count += 1
            
            return {
                "content": response.content[0].text,
                "model": model,
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                "stop_reason": response.stop_reason
            }
            
        except AnthropicRateLimitError as e:
            raise RateLimitError(f"Rate limit exceeded: {str(e)}")
        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise AIServiceError(f"Failed to generate completion: {str(e)}")
    
    def _fallback_completion(self, prompt: str) -> Dict[str, Any]:
        """
        Fallback completion when API is not available
        Uses rule-based logic for basic functionality
        """
        logger.info("Using fallback mode for AI completion")
        
        # Simple rule-based responses for common operations
        if "score" in prompt.lower():
            return {
                "content": json.dumps({"score": 75, "confidence": "medium", "suggestions": []}),
                "model": "fallback",
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "stop_reason": "fallback"
            }
        elif "revenue" in prompt.lower():
            return {
                "content": json.dumps({"predicted_revenue": 1000, "confidence_interval": [900, 1100]}),
                "model": "fallback",
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "stop_reason": "fallback"
            }
        else:
            return {
                "content": json.dumps({"result": "success", "data": {}}),
                "model": "fallback",
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "stop_reason": "fallback"
            }
    
    def optimize_prompt(self, prompt: str, max_length: int = 4000) -> str:
        """
        Optimize prompt to reduce token usage
        
        Args:
            prompt: Original prompt
            max_length: Maximum character length
        
        Returns:
            Optimized prompt
        """
        # Remove excessive whitespace
        prompt = " ".join(prompt.split())
        
        # Truncate if too long
        if len(prompt) > max_length:
            prompt = prompt[:max_length] + "..."
            logger.warning(f"Prompt truncated to {max_length} characters")
        
        return prompt
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get token usage statistics
        
        Returns:
            Dictionary with usage stats
        """
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "request_count": self.request_count,
            "average_tokens_per_request": (
                (self.total_input_tokens + self.total_output_tokens) / self.request_count
                if self.request_count > 0 else 0
            ),
            "estimated_cost": self._estimate_cost()
        }
    
    def _estimate_cost(self) -> float:
        """
        Estimate API usage cost
        
        Returns:
            Estimated cost in USD
        """
        # Pricing as of 2024 (adjust as needed)
        HAIKU_INPUT_PRICE = 0.25 / 1_000_000  # per token
        HAIKU_OUTPUT_PRICE = 1.25 / 1_000_000  # per token
        
        cost = (
            self.total_input_tokens * HAIKU_INPUT_PRICE +
            self.total_output_tokens * HAIKU_OUTPUT_PRICE
        )
        
        return round(cost, 4)