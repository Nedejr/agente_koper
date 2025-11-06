"""
Image Processor
Handles documents with associated images using image-map.json
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from langchain_core.documents import Document

from backend.utils.logger import log


class ImageProcessor:
    """
    Processes documents with image references
    Enriches document chunks with image metadata
    """
    
    def __init__(self):
        log.info("🖼️  ImageProcessor initialized")
    
    def load_image_map(self, image_map_path: str) -> List[Dict]:
        """
        Load image mapping from JSON file
        
        Args:
            image_map_path: Path to images-map.json file
            
        Returns:
            List of image mapping dictionaries
        """
        try:
            with open(image_map_path, 'r', encoding='utf-8') as f:
                image_map = json.load(f)
            
            log.info(f"✅ Loaded {len(image_map)} image mappings")
            return image_map
            
        except Exception as e:
            log.error(f"❌ Error loading image map: {str(e)}")
            return []
    
    def enrich_chunks_with_images(
        self,
        chunks: List[Document],
        image_map: List[Dict],
        base_image_dir: str
    ) -> List[Document]:
        """
        Enrich document chunks with image metadata
        
        Args:
            chunks: List of document chunks
            image_map: List of image mappings
            base_image_dir: Base directory containing images
            
        Returns:
            List of enriched chunks with image metadata
        """
        log.info("🎨 Enriching chunks with image metadata")
        
        enriched_chunks = []
        
        for chunk in chunks:
            # Find relevant images for this chunk
            relevant_images = self._find_relevant_images(
                chunk.page_content,
                image_map
            )
            
            # Add image metadata
            chunk.metadata["images"] = []
            
            for img_info in relevant_images:
                # Build absolute path for image
                image_path = os.path.join(
                    base_image_dir,
                    img_info["image"]
                )
                
                chunk.metadata["images"].append({
                    "section": img_info["section"],
                    "filename": img_info["image"],
                    "path": image_path,
                    "caption": img_info["caption"],
                    "alt": img_info["alt"],
                })
            
            enriched_chunks.append(chunk)
        
        # Log statistics
        chunks_with_images = sum(1 for c in enriched_chunks if c.metadata.get("images"))
        total_images = sum(len(c.metadata.get("images", [])) for c in enriched_chunks)
        
        log.info(
            f"✅ Enrichment complete - "
            f"{chunks_with_images}/{len(enriched_chunks)} chunks have images "
            f"(total: {total_images} image references)"
        )
        
        return enriched_chunks
    
    def _find_relevant_images(
        self,
        chunk_content: str,
        image_map: List[Dict]
    ) -> List[Dict]:
        """
        Find images relevant to a chunk based on content matching
        
        Args:
            chunk_content: Content of the chunk
            image_map: List of image mappings
            
        Returns:
            List of relevant image info dictionaries
        """
        relevant_images = []
        
        for img_info in image_map:
            section_name = img_info.get("section", "")
            caption = img_info.get("caption", "")
            
            # Check if section name or key terms appear in chunk
            # Also check for image references in markdown format
            if (
                section_name.lower() in chunk_content.lower()
                or img_info["image"] in chunk_content
                or self._check_semantic_relevance(chunk_content, caption)
            ):
                relevant_images.append(img_info)
        
        return relevant_images
    
    def _check_semantic_relevance(
        self,
        chunk_content: str,
        caption: str
    ) -> bool:
        """
        Check if image caption is semantically relevant to chunk
        Uses keyword matching for now (can be enhanced with embeddings)
        
        Args:
            chunk_content: Content of the chunk
            caption: Image caption
            
        Returns:
            True if relevant, False otherwise
        """
        # Extract key terms from caption
        key_terms = self._extract_key_terms(caption)
        
        # Check if at least 2 key terms appear in chunk
        matches = sum(1 for term in key_terms if term in chunk_content.lower())
        
        return matches >= 2
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text (simple keyword extraction)
        
        Args:
            text: Input text
            
        Returns:
            List of key terms
        """
        # Remove common words and extract meaningful terms
        stopwords = {
            'o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das',
            'em', 'no', 'na', 'nos', 'nas', 'para', 'com', 'por',
            'e', 'ou', 'que', 'se', 'um', 'uma', 'uns', 'umas',
            'este', 'esta', 'isto', 'esse', 'essa', 'isso',
        }
        
        # Simple tokenization
        words = text.lower().split()
        
        # Filter stopwords and short words
        key_terms = [
            w.strip('.,!?:;()[]{}') 
            for w in words 
            if len(w) > 3 and w.lower() not in stopwords
        ]
        
        return key_terms
    
    def process_document_with_images(
        self,
        chunks: List[Document],
        doc_dir: str
    ) -> List[Document]:
        """
        Main method to process document chunks with images
        
        Args:
            chunks: Document chunks from markdown file
            doc_dir: Directory containing the document (should have images-map.json)
            
        Returns:
            Enriched chunks with image metadata
        """
        # Look for images-map.json in the document directory
        image_map_path = os.path.join(doc_dir, "images-map.json")
        
        if not os.path.exists(image_map_path):
            log.warning(f"⚠️  No images-map.json found at {image_map_path}")
            return chunks
        
        # Load image map
        image_map = self.load_image_map(image_map_path)
        
        if not image_map:
            log.warning("⚠️  Empty or invalid image map")
            return chunks
        
        # Determine base image directory
        base_image_dir = os.path.join(doc_dir, "images")
        
        # Enrich chunks with image metadata
        enriched_chunks = self.enrich_chunks_with_images(
            chunks,
            image_map,
            base_image_dir
        )
        
        return enriched_chunks


# Singleton instance
image_processor = ImageProcessor()

