"""
Vector Store Client (Qdrant)
Interface para gerenciamento do banco de dados vetorial
"""

from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from backend.config import settings
from backend.utils.logger import log


class VectorStoreClient:
    """
    Cliente para interação com Qdrant
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        collection_name: Optional[str] = None,
    ):
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.collection_name = collection_name or settings.qdrant_collection_name
        
        # Inicializa cliente
        self.client = QdrantClient(host=self.host, port=self.port)
        
        log.info(
            f"🗄️  Qdrant Client inicializado - "
            f"Host: {self.host}:{self.port} | "
            f"Collection: {self.collection_name}"
        )
    
    async def create_collection(
        self,
        vector_size: Optional[int] = None,
        distance: Optional[str] = None,
    ) -> bool:
        """
        Cria collection no Qdrant
        
        Args:
            vector_size: Dimensão dos vetores
            distance: Métrica de distância (Cosine, Euclid, Dot)
            
        Returns:
            True se criada com sucesso
        """
        vector_size = vector_size or settings.qdrant_vector_size
        distance = distance or settings.qdrant_distance
        
        try:
            # Verifica se collection já existe
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name in collection_names:
                log.info(f"✅ Collection '{self.collection_name}' já existe")
                return True
            
            # Cria collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=getattr(models.Distance, distance.upper()),
                ),
            )
            
            log.info(
                f"✅ Collection '{self.collection_name}' criada - "
                f"Size: {vector_size} | Distance: {distance}"
            )
            
            return True
            
        except Exception as e:
            log.error(f"❌ Erro ao criar collection: {str(e)}")
            raise
    
    async def upsert_points(
        self,
        points: List[Dict[str, Any]],
    ) -> bool:
        """
        Insere ou atualiza pontos na collection
        
        Args:
            points: Lista de pontos com id, vector e payload
            
        Returns:
            True se inserido com sucesso
        """
        try:
            qdrant_points = [
                models.PointStruct(
                    id=point["id"],
                    vector=point["vector"],
                    payload=point.get("payload", {}),
                )
                for point in points
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=qdrant_points,
            )
            
            log.info(f"✅ {len(points)} pontos inseridos na collection '{self.collection_name}'")
            
            return True
            
        except Exception as e:
            log.error(f"❌ Erro ao inserir pontos: {str(e)}")
            raise
    
    async def search(
        self,
        query_vector: List[float],
        limit: Optional[int] = None,
        score_threshold: Optional[float] = None,
        filter_conditions: Optional[Dict] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca pontos similares
        
        Args:
            query_vector: Vetor da query
            limit: Número máximo de resultados
            score_threshold: Score mínimo de similaridade
            filter_conditions: Filtros adicionais
            
        Returns:
            Lista de resultados com score e payload
        """
        limit = limit or settings.top_k_results
        score_threshold = score_threshold or settings.min_similarity_score
        
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=filter_conditions,
            )
            
            formatted_results = [
                {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                }
                for result in results
            ]
            
            log.debug(f"🔍 Busca retornou {len(formatted_results)} resultados")
            
            return formatted_results
            
        except Exception as e:
            log.error(f"❌ Erro na busca: {str(e)}")
            raise
    
    async def delete_points(
        self,
        point_ids: List[str],
    ) -> bool:
        """
        Deleta pontos da collection
        
        Args:
            point_ids: IDs dos pontos a deletar
            
        Returns:
            True se deletado com sucesso
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=point_ids,
                ),
            )
            
            log.info(f"🗑️  {len(point_ids)} pontos deletados")
            
            return True
            
        except Exception as e:
            log.error(f"❌ Erro ao deletar pontos: {str(e)}")
            raise
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """
        Obtém informações da collection
        
        Returns:
            Dict com informações da collection
        """
        try:
            info = self.client.get_collection(collection_name=self.collection_name)
            
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status,
            }
            
        except UnexpectedResponse:
            log.warning(f"Collection '{self.collection_name}' não existe")
            return {
                "name": self.collection_name,
                "vectors_count": 0,
                "points_count": 0,
                "status": "not_found",
            }
        except Exception as e:
            log.error(f"❌ Erro ao obter informações da collection: {str(e)}")
            raise
    
    async def check_connection(self) -> bool:
        """
        Verifica se Qdrant está disponível
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            self.client.get_collections()
            return True
        except Exception as e:
            log.warning(f"Qdrant não disponível: {str(e)}")
            return False


# Instância global (singleton)
vector_store_client = VectorStoreClient()

