"""
OpenRouter Client
Interface for communication with OpenRouter API
"""

import asyncio
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import settings
from backend.utils.logger import log


class OpenRouterClient:
    """
    Client for interaction with OpenRouter API
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url or settings.openrouter_base_url
        self.model = model or settings.openrouter_default_model
        self.timeout = timeout or settings.openrouter_timeout
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required! Set OPENROUTER_API_KEY environment variable.")
        
        log.info(f"🤖 OpenRouter Client initialized - Model: {self.model}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://agente-koper.app",  # Optional but recommended
            "X-Title": "Agente Koper",  # Optional but recommended
            "Content-Type": "application/json",
        }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate response using OpenRouter
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            temperature: Temperature (0-1)
            max_tokens: Maximum tokens
            model: Model to use (optional, uses default)
            **kwargs: Other OpenRouter parameters
            
        Returns:
            Generated response
        """
        url = f"{self.base_url}/chat/completions"
        model_to_use = model or self.model
        
        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature or settings.openrouter_temperature,
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Add extra kwargs
        payload.update(kwargs)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                log.debug(f"📤 OpenRouter request - Model: {model_to_use}")
                
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                generated_text = result["choices"][0]["message"]["content"]
                
                log.debug(f"📥 OpenRouter response received")
                
                return generated_text
                
        except httpx.TimeoutException as e:
            log.error(f"⏱️  Timeout on OpenRouter request: {str(e)}")
            raise Exception(f"Timeout generating response: {str(e)}")
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            
            # Se for 429 (rate limit), tenta com retry
            if status_code == 429:
                log.warning(f"⚠️ Rate limit (429) - Tentando retry...")
                # Tenta mais 2 vezes com backoff exponencial
                for attempt in range(1, 3):
                    wait_time = 2 ** attempt  # 2s, 4s
                    log.info(f"⏳ Aguardando {wait_time}s antes de retry {attempt}/2...")
                    await asyncio.sleep(wait_time)
                    
                    try:
                        async with httpx.AsyncClient(timeout=self.timeout) as retry_client:
                            response = await retry_client.post(
                                url,
                                headers=self._get_headers(),
                                json=payload
                            )
                            response.raise_for_status()
                            result = response.json()
                            generated_text = result["choices"][0]["message"]["content"]
                            log.info(f"✅ Retry {attempt} bem-sucedido!")
                            return generated_text
                    except httpx.HTTPStatusError as retry_error:
                        if retry_error.response.status_code == 429:
                            continue  # Tenta próximo retry
                        raise
                    except Exception:
                        continue
            
            log.error(f"❌ HTTP error from OpenRouter: {status_code}")
            error_detail = e.response.json() if e.response.content else str(e)
            raise Exception(f"Error generating response: {error_detail}")
        except Exception as e:
            log.error(f"❌ Error calling OpenRouter: {str(e)}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Chat using message format
        
        Args:
            messages: List of messages [{"role": "user/assistant/system", "content": "..."}]
            temperature: Temperature
            model: Model to use
            **kwargs: Other parameters
            
        Returns:
            Assistant response
        """
        url = f"{self.base_url}/chat/completions"
        model_to_use = model or self.model
        
        payload = {
            "model": model_to_use,
            "messages": messages,
            "temperature": temperature or settings.openrouter_temperature,
        }
        
        payload.update(kwargs)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                log.debug(f"💬 OpenRouter chat request - Messages: {len(messages)}")
                
                response = await client.post(
                    url,
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                assistant_message = result["choices"][0]["message"]["content"]
                
                log.debug(f"💬 OpenRouter chat response received")
                
                return assistant_message
                
        except Exception as e:
            log.error(f"❌ Error on chat with OpenRouter: {str(e)}")
            raise
    
    async def check_connection(self) -> bool:
        """
        Check if OpenRouter is available
        
        Returns:
            True if connected, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers()
                )
                return response.status_code == 200
        except Exception as e:
            log.warning(f"OpenRouter not available: {str(e)}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available models on OpenRouter
        
        Returns:
            List of models
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                result = response.json()
                models = result.get("data", [])
                
                log.info(f"📋 Available models: {len(models)}")
                
                return models
                
        except Exception as e:
            log.error(f"❌ Error listing models: {str(e)}")
            return []
    
    def get_free_models(self) -> List[str]:
        """
        Get list of free models
        
        Returns:
            List of free model IDs
        """
        return settings.openrouter_free_models


# Global instance (singleton)
openrouter_client = OpenRouterClient()

