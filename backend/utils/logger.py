"""
Configuração de logging usando Loguru
"""

import sys
from pathlib import Path

from loguru import logger

from backend.config import settings


def setup_logger():
    """
    Configura o logger da aplicação
    """
    # Remove handlers padrão
    logger.remove()
    
    # Console handler (colorido)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True,
    )
    
    # File handler (para produção)
    if settings.is_production:
        log_path = Path("/app/logs")
        log_path.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            log_path / "app.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=settings.log_level,
            rotation="500 MB",  # Rotaciona quando atinge 500MB
            retention="10 days",  # Mantém logs por 10 dias
            compression="zip",  # Comprime logs antigos
        )
        
        # Arquivo separado para erros
        logger.add(
            log_path / "errors.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
        )
    
    return logger


# Inicializa logger
log = setup_logger()

