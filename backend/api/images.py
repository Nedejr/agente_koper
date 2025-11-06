"""
Images API
Endpoints for serving documentation images
"""

import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from backend.config import settings
from backend.utils.logger import log

router = APIRouter()


def get_docs_base_path() -> Path:
    """
    Get the base path for documentation files
    
    Returns:
        Path to docs directory
    """
    # Get project root (where backend/ is located)
    backend_dir = Path(__file__).parent.parent
    project_root = backend_dir.parent
    docs_dir = project_root / "docs"
    
    return docs_dir


@router.get(
    "/images/{section}/{filename}",
    status_code=status.HTTP_200_OK,
    summary="Get documentation image",
    description="Retrieve an image from the documentation"
)
async def get_image(section: str, filename: str):
    """
    Get documentation image
    
    Args:
        section: Documentation section (e.g., 'gestao-epi')
        filename: Image filename
        
    Returns:
        Image file
    """
    try:
        # Build path to image
        docs_path = get_docs_base_path()
        image_path = docs_path / section / "images" / filename
        
        # Security check: ensure path is within docs directory
        try:
            image_path = image_path.resolve()
            docs_path = docs_path.resolve()
            
            if not str(image_path).startswith(str(docs_path)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid path"
            )
        
        # Check if file exists
        if not image_path.exists() or not image_path.is_file():
            log.warning(f"⚠️  Image not found: {image_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image not found: {filename}"
            )
        
        # Check file extension
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
        if image_path.suffix.lower() not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type"
            )
        
        log.info(f"📸 Serving image: {section}/{filename}")
        
        # Return image file
        return FileResponse(
            path=str(image_path),
            media_type=f"image/{image_path.suffix[1:]}",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"❌ Error serving image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving image"
        )


@router.get(
    "/images",
    status_code=status.HTTP_200_OK,
    summary="List available documentation sections",
    description="List all documentation sections with images"
)
async def list_sections():
    """
    List available documentation sections
    
    Returns:
        List of sections with image counts
    """
    try:
        docs_path = get_docs_base_path()
        
        if not docs_path.exists():
            return {"sections": []}
        
        sections = []
        
        # Iterate through docs directories
        for section_dir in docs_path.iterdir():
            if section_dir.is_dir():
                images_dir = section_dir / "images"
                
                if images_dir.exists() and images_dir.is_dir():
                    # Count images
                    image_count = len([
                        f for f in images_dir.iterdir()
                        if f.is_file() and f.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
                    ])
                    
                    sections.append({
                        "name": section_dir.name,
                        "image_count": image_count,
                    })
        
        return {
            "sections": sections,
            "total_sections": len(sections)
        }
        
    except Exception as e:
        log.error(f"❌ Error listing sections: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing sections"
        )

