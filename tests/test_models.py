"""
Unit tests for data models
"""
import pytest
from datetime import datetime
from lambda.shared.models import (
    AudioFormat,
    AudioMetadata,
    ProsodyVector,
    CulturalMarker,
    LinguisticDNA,
    StyleVector,
    ConfidenceMetrics,
    ExpressionFrequency,
    CadencePattern,
    LinguisticFeature,
    CulturalContext,
    PerformanceMetrics,
)


def test_audio_metadata_creation():
    """Test AudioMetadata dataclass creation"""
    metadata = AudioMetadata(
        file_name="test_audio.mp3",
        format=AudioFormat.MP3,
        duration_seconds=120.5,
        file_size_bytes=1024000,
    )
    
    assert metadata.file_name == "test_audio.mp3"
    assert metadata.format == AudioFormat.MP3
    assert metadata.duration_seconds == 120.5
    assert isinstance(metadata.upload_timestamp, datetime)


def test_prosody_vector_creation():
    """Test ProsodyVector dataclass creation"""
    prosody = ProsodyVector(
        speech_rate=150.0,
        pause_frequency=10.0,
        average_pause_duration=0.5,
        pitch_variation=0.3,
        energy_variation=0.4,
    )
    
    assert prosody.speech_rate == 150.0
    assert prosody.pause_frequency == 10.0


def test_cultural_marker_creation():
    """Test CulturalMarker dataclass creation"""
    marker = CulturalMarker(
        expression="actually",
        frequency=15,
        context="sentence_starter",
        confidence=0.85,
    )
    
    assert marker.expression == "actually"
    assert marker.frequency == 15
    assert marker.confidence == 0.85


def test_linguistic_dna_creation():
    """Test LinguisticDNA dataclass creation"""
    prosody = ProsodyVector(150.0, 10.0, 0.5, 0.3, 0.4)
    marker = CulturalMarker("actually", 15, "sentence_starter", 0.85)
    cadence = CadencePattern(0.8, [0.5, 0.7], [0.6, 0.8])
    expression_freq = ExpressionFrequency(
        hinglish_terms={"yaar": 5},
        indian_english_phrases={"do the needful": 3},
        total_expressions=8,
    )
    confidence = ConfidenceMetrics(0.85, 0.9, 0.8, 0.87)
    audio_meta = AudioMetadata("test.mp3", AudioFormat.MP3)
    
    dna = LinguisticDNA(
        user_id="user123",
        prosody_vectors=[prosody],
        cultural_markers=[marker],
        cadence_patterns=[cadence],
        expression_frequency=expression_freq,
        confidence_scores=confidence,
        extraction_timestamp=datetime.utcnow(),
        audio_sample_metadata=audio_meta,
    )
    
    assert dna.user_id == "user123"
    assert len(dna.prosody_vectors) == 1
    assert len(dna.cultural_markers) == 1
    assert dna.confidence_scores.overall_confidence == 0.85


def test_style_vector_creation():
    """Test StyleVector dataclass creation"""
    feature = LinguisticFeature("speech_rate", 150.0, 0.8)
    context = CulturalContext(
        primary_language="Indian English",
        regional_influences=["Hindi", "Tamil"],
    )
    metrics = PerformanceMetrics(usage_count=10, average_authenticity_score=0.85)
    
    vector = StyleVector(
        vector_id="vec123",
        user_id="user123",
        embeddings=[0.1, 0.2, 0.3],
        linguistic_features=[feature],
        cultural_context=context,
        version=1,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        performance_metrics=metrics,
    )
    
    assert vector.vector_id == "vec123"
    assert vector.user_id == "user123"
    assert len(vector.embeddings) == 3
    assert vector.version == 1
