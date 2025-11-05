"""
Embeddings Generator
Gera embeddings usando Sentence Transformers (local)
"""

from typing import List

from sentence_transformers import SentenceTransformer

from backend.config import settings
from backend.utils.logger import log


class EmbeddingsGenerator:
    """
    Gerador de embeddings usando Sentence Transformers
    """
    
    def __init__(
        self,
        model_name: str = None,
        device: str = None,
    ):
        self.model_name = model_name or settings.embeddings_model
        self.device = device or settings.embeddings_device
        
        log.info(f"🧠 Carregando modelo de embeddings: {self.model_name}")
        
        # Carrega modelo
        self.model = SentenceTransformer(self.model_name, device=self.device)
        
        # Obtém dimensão dos vetores
        self.vector_size = self.model.get_sentence_embedding_dimension()
        
        log.info(
            f"✅ Modelo carregado - "
            f"Dimensão: {self.vector_size} | "
            f"Device: {self.device}"
        )
    
    def generate(self, texts: List[str], batch_size: int = None) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos
        
        Args:
            texts: Lista de textos
            batch_size: Tamanho do batch (opcional)
            
        Returns:
            Lista de vetores (embeddings)
        """
        batch_size = batch_size or settings.embeddings_batch_size
        
        try:
            log.debug(f"🔄 Gerando embeddings para {len(texts)} textos")
            
            # Gera embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            
            # Converte para lista de listas
            embeddings_list = embeddings.tolist()
            
            log.debug(f"✅ Embeddings gerados - Shape: {len(embeddings_list)}x{self.vector_size}")
            
            return embeddings_list
            
        except Exception as e:
            log.error(f"❌ Erro ao gerar embeddings: {str(e)}")
            raise
    
    def generate_single(self, text: str) -> List[float]:
        """
        Gera embedding para um único texto
        
        Args:
            text: Texto
            
        Returns:
            Vetor (embedding)
        """
        return self.generate([text])[0]


# Instância global (singleton)
embeddings_generator = EmbeddingsGenerator()

