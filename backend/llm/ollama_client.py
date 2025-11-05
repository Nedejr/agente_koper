"""
Cliente Ollama
Interface para comunicação com servidor Ollama
"""

from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.config import settings
from backend.utils.logger import log


class OllamaClient:
    """
    Cliente para interação com Ollama API
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = timeout or settings.ollama_timeout
        
        log.info(f"🤖 Ollama Client inicializado - Model: {self.model} | URL: {self.base_url}")
    
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
        **kwargs
    ) -> str:
        """
        Gera resposta usando Ollama
        
        Args:
            prompt: Prompt do usuário
            system: Prompt do sistema (opcional)
            temperature: Temperatura (0-1)
            max_tokens: Máximo de tokens
            **kwargs: Outros parâmetros do Ollama
            
        Returns:
            Resposta gerada
        """
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature or settings.ollama_temperature,
                "num_ctx": settings.ollama_num_ctx,
            }
        }
        
        if system:
            payload["system"] = system
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        # Adiciona kwargs extras
        payload["options"].update(kwargs)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                log.debug(f"📤 Ollama request - Model: {self.model}")
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                generated_text = result.get("response", "")
                
                log.debug(f"📥 Ollama response - Tokens: {result.get('eval_count', 0)}")
                
                return generated_text
                
        except httpx.TimeoutException as e:
            log.error(f"⏱️  Timeout na requisição ao Ollama: {str(e)}")
            raise Exception(f"Timeout ao gerar resposta: {str(e)}")
        except httpx.HTTPStatusError as e:
            log.error(f"❌ Erro HTTP do Ollama: {e.response.status_code}")
            raise Exception(f"Erro ao gerar resposta: {str(e)}")
        except Exception as e:
            log.error(f"❌ Erro ao chamar Ollama: {str(e)}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """
        Chat usando formato de mensagens
        
        Args:
            messages: Lista de mensagens [{"role": "user/assistant/system", "content": "..."}]
            temperature: Temperatura
            **kwargs: Outros parâmetros
            
        Returns:
            Resposta do assistente
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature or settings.ollama_temperature,
                "num_ctx": settings.ollama_num_ctx,
            }
        }
        
        payload["options"].update(kwargs)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                log.debug(f"💬 Ollama chat request - Messages: {len(messages)}")
                
                response = await client.post(url, json=payload)
                response.raise_for_status()
                
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "")
                
                log.debug(f"💬 Ollama chat response received")
                
                return assistant_message
                
        except Exception as e:
            log.error(f"❌ Erro no chat com Ollama: {str(e)}")
            raise
    
    async def check_connection(self) -> bool:
        """
        Verifica se Ollama está disponível
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/version")
                return response.status_code == 200
        except Exception as e:
            log.warning(f"Ollama não disponível: {str(e)}")
            return False
    
    async def list_models(self) -> List[str]:
        """
        Lista modelos disponíveis no Ollama
        
        Returns:
            Lista de nomes de modelos
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                
                result = response.json()
                models = [model["name"] for model in result.get("models", [])]
                
                log.info(f"📋 Modelos disponíveis: {', '.join(models)}")
                
                return models
                
        except Exception as e:
            log.error(f"❌ Erro ao listar modelos: {str(e)}")
            return []


# Instância global (singleton)
ollama_client = OllamaClient()

