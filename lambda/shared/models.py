"""
Data Models for Swara AI Identity Layer
Defines core data structures used across Lambda functions
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class AudioFormat(Enum):
    """Supported audio formats"""
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"


class ContentType(Enum):
    """Supported content types"""
    EMAIL = "email"
    LINKEDIN_POST = "linkedin_post"
    PRESENTATION = "presentation"
    GENERAL = "general"


@dataclass
class AudioMetadata:
    """Metadata for audio files"""
    file_name: str
    format: AudioFormat
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    upload_timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProsodyVector:
    """Prosodic pattern representation"""
    speech_rate: float  # Words per minute
    pause_frequency: float  # Pauses per minute
    average_pause_duration: float  # Seconds
    pitch_variation: float  # Standard deviation
    energy_variation: float  # Standard deviation


@dataclass
class CulturalMarker:
    """Indian English linguistic marker"""
    expression: str
    frequency: int
    context: str
    confidence: float


@dataclass
class CadencePattern:
    """Speech cadence pattern"""
    rhythm_score: float
    emphasis_pattern: List[float]
    intonation_curve: List[float]


@dataclass
class ExpressionFrequency:
    """Frequency of cultural expressions"""
    hinglish_terms: Dict[str, int]
    indian_english_phrases: Dict[str, int]
    total_expressions: int


@dataclass
class ConfidenceMetrics:
    """Confidence scores for analysis"""
    overall_confidence: float
    prosody_confidence: float
    cultural_marker_confidence: float
    sample_quality_score: float


@dataclass
class LinguisticDNA:
    """Complete linguistic profile extracted from voice"""
    user_id: str
    prosody_vectors: List[ProsodyVector]
    cultural_markers: List[CulturalMarker]
    cadence_patterns: List[CadencePattern]
    expression_frequency: ExpressionFrequency
    confidence_scores: ConfidenceMetrics
    extraction_timestamp: datetime
    audio_sample_metadata: AudioMetadata


@dataclass
class LinguisticFeature:
    """Individual linguistic feature"""
    feature_name: str
    feature_value: float
    importance: float


@dataclass
class CulturalContext:
    """Cultural context information"""
    primary_language: str = "Indian English"
    regional_influences: List[str] = field(default_factory=list)
    professional_domain: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """Performance metrics for style vectors"""
    usage_count: int = 0
    average_authenticity_score: float = 0.0
    last_used: Optional[datetime] = None


@dataclass
class StyleVector:
    """Mathematical representation of linguistic patterns"""
    vector_id: str
    user_id: str
    embeddings: List[float]
    linguistic_features: List[LinguisticFeature]
    cultural_context: CulturalContext
    version: int
    created_at: datetime
    last_updated: datetime
    performance_metrics: PerformanceMetrics


@dataclass
class AuthenticityTarget:
    """Target for authenticity validation"""
    marker_type: str
    target_frequency: float
    tolerance: float


@dataclass
class GenerationConfig:
    """Configuration for content generation"""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"


@dataclass
class EnhancedPrompt:
    """User prompt enhanced with style vector"""
    original_prompt: str
    style_vector: StyleVector
    contextual_instructions: List[str]
    cultural_guidelines: List[str]
    authenticity_targets: List[AuthenticityTarget]
    generation_parameters: GenerationConfig


@dataclass
class EngagementMetrics:
    """Predicted engagement metrics"""
    authenticity_score: float
    predicted_engagement_rate: float
    cultural_relevance_score: float


@dataclass
class GenerationMetadata:
    """Metadata for generated content"""
    generation_timestamp: datetime
    model_used: str
    processing_time_ms: float
    tokens_used: int


@dataclass
class GeneratedContent:
    """AI-generated content with metadata"""
    content_id: str
    user_id: str
    original_prompt: str
    generated_text: str
    authenticity_score: float
    cultural_markers: List[CulturalMarker]
    engagement_prediction: EngagementMetrics
    generation_metadata: GenerationMetadata
