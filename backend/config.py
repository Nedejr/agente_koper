"""
Configurações centralizadas do sistema
Utiliza Pydantic Settings para validação e gerenciamento de variáveis de ambiente
"""

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente
    """

    # ============================================
    # Application Settings
    # ============================================
    app_name: str = "Agente Koper"
    app_version: str = "2.0.0"
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True)
    
    # Server
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    
    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # ============================================
    # Ollama Settings
    # ============================================
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=120)  # segundos
    ollama_temperature: float = Field(default=0.7)
    ollama_num_ctx: int = Field(default=4096)  # context window
    
    # ============================================
    # Qdrant Settings
    # ============================================
    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    qdrant_collection_name: str = Field(default="koper_knowledge", alias="QDRANT_COLLECTION_NAME")
    qdrant_vector_size: int = Field(default=384)  # all-MiniLM-L6-v2
    qdrant_distance: str = Field(default="Cosine")  # Cosine, Euclid, Dot
    
    # ============================================
    # Embeddings Settings
    # ============================================
    embeddings_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        alias="EMBEDDINGS_MODEL"
    )
    embeddings_device: str = Field(default="cpu")  # cpu ou cuda
    embeddings_batch_size: int = Field(default=32)
    
    # ============================================
    # RAG Settings
    # ============================================
    chunk_size: int = Field(default=1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, alias="CHUNK_OVERLAP")
    top_k_results: int = Field(default=5, alias="TOP_K_RESULTS")
    min_similarity_score: float = Field(default=0.7, alias="MIN_SIMILARITY_SCORE")
    
    # ============================================
    # Agent Settings
    # ============================================
    classifier_threshold: float = Field(default=0.6, alias="CLASSIFIER_THRESHOLD")
    evaluator_min_confidence: float = Field(default=0.7, alias="EVALUATOR_MIN_CONFIDENCE")
    max_chat_history: int = Field(default=20)
    agent_max_iterations: int = Field(default=10)
    
    # ============================================
    # Document Processing
    # ============================================
    max_file_size_mb: int = Field(default=50)
    allowed_extensions: list[str] = Field(default=["pdf", "txt", "md", "markdown"])
    documents_dir: str = Field(default="/app/documents")
    
    # ============================================
    # API Settings
    # ============================================
    api_prefix: str = "/api"
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:8000"])
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(default=["*"])
    cors_allow_headers: list[str] = Field(default=["*"])
    
    # ============================================
    # Security (para produção)
    # ============================================
    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    jwt_secret: Optional[str] = Field(default=None, alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24  # 24 horas
    
    # ============================================
    # Performance & Limits
    # ============================================
    request_timeout: int = Field(default=60)  # segundos
    max_concurrent_requests: int = Field(default=100)
    rate_limit_per_minute: int = Field(default=60)
    
    # ============================================
    # Pydantic Settings Config
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ============================================
    # Computed Properties
    # ============================================
    @property
    def qdrant_url(self) -> str:
        """URL completa do Qdrant"""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"
    
    @property
    def is_production(self) -> bool:
        """Verifica se está em produção"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em desenvolvimento"""
        return self.environment.lower() == "development"
    
    @property
    def max_file_size_bytes(self) -> int:
        """Tamanho máximo de arquivo em bytes"""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações
    Usa cache para evitar recarregar em cada chamada
    """
    return Settings()


# Instância global (para facilitar importação)
settings = get_settings()


# ============================================
# Validação na inicialização
# ============================================
if __name__ == "__main__":
    import json
    
    config = get_settings()
    print("=" * 60)
    print("CONFIGURAÇÕES DO AGENTE KOPER")
    print("=" * 60)
    print(json.dumps(config.model_dump(), indent=2, default=str))
    print("=" * 60)
