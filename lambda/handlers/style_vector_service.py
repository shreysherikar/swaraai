"""
Style Vector Service
Converts LinguisticDNA to StyleVector for storage in DynamoDB
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import (
    LinguisticDNA,
    StyleVector,
    LinguisticFeature,
    CulturalContext,
    PerformanceMetrics,
)


class StyleVectorService:
    """Service for generating and managing style vectors"""
    
    def __init__(self):
        """Initialize the style vector service"""
        pass
    
    def create_style_vector(self, linguistic_dna: LinguisticDNA, version: int = 1) -> StyleVector:
        """
        Convert LinguisticDNA to StyleVector
        
        For MVP, we create a simple JSON-based representation without complex embeddings.
        The style vector captures key linguistic features in a structured format.
        
        Args:
            linguistic_dna: The linguistic DNA extracted from voice
            version: Version number for this style vector
            
        Returns:
            StyleVector with features and metadata
        """
        # Generate unique vector ID
        vector_id = str(uuid.uuid4())
        
        # Extract linguistic features from DNA
        linguistic_features = self._extract_linguistic_features(linguistic_dna)
        
        # Create simple embeddings (normalized feature values)
        embeddings = self._create_simple_embeddings(linguistic_features)
        
        # Extract cultural context
        cultural_context = self._extract_cultural_context(linguistic_dna)
        
        # Create style vector
        style_vector = StyleVector(
            vector_id=vector_id,
            user_id=linguistic_dna.user_id,
            embeddings=embeddings,
            linguistic_features=linguistic_features,
            cultural_context=cultural_context,
            version=version,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
            performance_metrics=PerformanceMetrics(
                usage_count=0,
                average_authenticity_score=0.0,
                last_used=None
            )
        )
        
        return style_vector
    
    def _extract_linguistic_features(self, linguistic_dna: LinguisticDNA) -> List[LinguisticFeature]:
        """
        Extract linguistic features from DNA
        
        Args:
            linguistic_dna: The linguistic DNA
            
        Returns:
            List of linguistic features
        """
        features = []
        
        # Extract prosody features
        if linguistic_dna.prosody_vectors:
            avg_prosody = linguistic_dna.prosody_vectors[0]  # Use first vector for MVP
            
            features.append(LinguisticFeature(
                feature_name="speech_rate",
                feature_value=avg_prosody.speech_rate,
                importance=0.8
            ))
            
            features.append(LinguisticFeature(
                feature_name="pause_frequency",
                feature_value=avg_prosody.pause_frequency,
                importance=0.6
            ))
            
            features.append(LinguisticFeature(
                feature_name="pitch_variation",
                feature_value=avg_prosody.pitch_variation,
                importance=0.7
            ))
        
        # Extract cultural marker features
        if linguistic_dna.cultural_markers:
            total_markers = len(linguistic_dna.cultural_markers)
            avg_confidence = sum(m.confidence for m in linguistic_dna.cultural_markers) / total_markers
            
            features.append(LinguisticFeature(
                feature_name="cultural_marker_count",
                feature_value=float(total_markers),
                importance=0.9
            ))
            
            features.append(LinguisticFeature(
                feature_name="cultural_marker_confidence",
                feature_value=avg_confidence,
                importance=0.85
            ))
        
        # Extract expression frequency features
        if linguistic_dna.expression_frequency:
            features.append(LinguisticFeature(
                feature_name="hinglish_term_count",
                feature_value=float(len(linguistic_dna.expression_frequency.hinglish_terms)),
                importance=0.9
            ))
            
            features.append(LinguisticFeature(
                feature_name="indian_english_phrase_count",
                feature_value=float(len(linguistic_dna.expression_frequency.indian_english_phrases)),
                importance=0.85
            ))
        
        # Add confidence scores as features
        features.append(LinguisticFeature(
            feature_name="overall_confidence",
            feature_value=linguistic_dna.confidence_scores.overall_confidence,
            importance=1.0
        ))
        
        return features
    
    def _create_simple_embeddings(self, features: List[LinguisticFeature]) -> List[float]:
        """
        Create simple embeddings from features
        
        For MVP, we normalize feature values to create a simple vector representation.
        In production, this would use a proper embedding model.
        
        Args:
            features: List of linguistic features
            
        Returns:
            List of normalized feature values
        """
        # Extract feature values and normalize
        embeddings = []
        for feature in features:
            # Simple normalization: scale to 0-1 range
            normalized_value = min(1.0, max(0.0, feature.feature_value / 100.0))
            embeddings.append(normalized_value)
        
        return embeddings
    
    def _extract_cultural_context(self, linguistic_dna: LinguisticDNA) -> CulturalContext:
        """
        Extract cultural context from linguistic DNA
        
        Args:
            linguistic_dna: The linguistic DNA
            
        Returns:
            Cultural context information
        """
        regional_influences = []
        
        # Extract regional influences from cultural markers
        if linguistic_dna.cultural_markers:
            for marker in linguistic_dna.cultural_markers:
                if marker.context and marker.context not in regional_influences:
                    regional_influences.append(marker.context)
        
        return CulturalContext(
            primary_language="Indian English",
            regional_influences=regional_influences[:5],  # Limit to top 5
            professional_domain=None  # Can be added later
        )
    
    def style_vector_to_dict(self, style_vector: StyleVector) -> Dict[str, Any]:
        """
        Convert StyleVector to dictionary for DynamoDB storage
        
        Args:
            style_vector: The style vector to convert
            
        Returns:
            Dictionary representation
        """
        return {
            "user_id": style_vector.user_id,
            "vector_id": style_vector.vector_id,
            "embeddings": style_vector.embeddings,
            "linguistic_features": [
                {
                    "feature_name": f.feature_name,
                    "feature_value": f.feature_value,
                    "importance": f.importance
                }
                for f in style_vector.linguistic_features
            ],
            "cultural_context": {
                "primary_language": style_vector.cultural_context.primary_language,
                "regional_influences": style_vector.cultural_context.regional_influences,
                "professional_domain": style_vector.cultural_context.professional_domain
            },
            "version": style_vector.version,
            "created_at": style_vector.created_at.isoformat(),
            "last_updated": style_vector.last_updated.isoformat(),
            "performance_metrics": {
                "usage_count": style_vector.performance_metrics.usage_count,
                "average_authenticity_score": style_vector.performance_metrics.average_authenticity_score,
                "last_used": style_vector.performance_metrics.last_used.isoformat() if style_vector.performance_metrics.last_used else None
            }
        }
    
    def dict_to_style_vector(self, data: Dict[str, Any]) -> StyleVector:
        """
        Convert dictionary from DynamoDB to StyleVector
        
        Args:
            data: Dictionary from DynamoDB
            
        Returns:
            StyleVector object
        """
        from decimal import Decimal
        
        def convert_decimal(obj):
            """Convert Decimal to float recursively"""
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, list):
                return [convert_decimal(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_decimal(value) for key, value in obj.items()}
            return obj
        
        # Convert all Decimals to floats
        data = convert_decimal(data)
        
        # Parse linguistic features
        linguistic_features = [
            LinguisticFeature(
                feature_name=f["feature_name"],
                feature_value=float(f["feature_value"]),
                importance=float(f["importance"])
            )
            for f in data.get("linguistic_features", [])
        ]
        
        # Parse cultural context
        cultural_context_data = data.get("cultural_context", {})
        cultural_context = CulturalContext(
            primary_language=cultural_context_data.get("primary_language", "Indian English"),
            regional_influences=cultural_context_data.get("regional_influences", []),
            professional_domain=cultural_context_data.get("professional_domain")
        )
        
        # Parse performance metrics
        perf_data = data.get("performance_metrics", {})
        performance_metrics = PerformanceMetrics(
            usage_count=int(perf_data.get("usage_count", 0)),
            average_authenticity_score=float(perf_data.get("average_authenticity_score", 0.0)),
            last_used=datetime.fromisoformat(perf_data["last_used"]) if perf_data.get("last_used") else None
        )
        
        # Create style vector
        return StyleVector(
            vector_id=data["vector_id"],
            user_id=data["user_id"],
            embeddings=[float(e) for e in data.get("embeddings", [])],
            linguistic_features=linguistic_features,
            cultural_context=cultural_context,
            version=int(data.get("version", 1)),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
            performance_metrics=performance_metrics
        )
