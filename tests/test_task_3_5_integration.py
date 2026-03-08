"""
Integration tests for Task 3 and Task 5 implementations
Tests style vector generation, DynamoDB storage, and content generation
"""
import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add lambda handlers to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'shared'))

from models import (
    LinguisticDNA,
    ProsodyVector,
    CulturalMarker,
    CadencePattern,
    ExpressionFrequency,
    ConfidenceMetrics,
    AudioMetadata,
    AudioFormat,
)
from style_vector_service import StyleVectorService
from context_injection import ContextInjectionEngine


class TestStyleVectorService:
    """Test style vector generation service"""
    
    def test_create_style_vector(self):
        """Test creating a style vector from linguistic DNA"""
        # Create sample linguistic DNA
        linguistic_dna = LinguisticDNA(
            user_id="test_user_123",
            prosody_vectors=[
                ProsodyVector(
                    speech_rate=120.0,
                    pause_frequency=15.0,
                    average_pause_duration=0.5,
                    pitch_variation=0.3,
                    energy_variation=0.4
                )
            ],
            cultural_markers=[
                CulturalMarker(
                    expression="actually",
                    frequency=5,
                    context="I actually think this is great",
                    confidence=0.9
                ),
                CulturalMarker(
                    expression="yaar",
                    frequency=3,
                    context="Come on yaar, let's go",
                    confidence=0.85
                )
            ],
            cadence_patterns=[
                CadencePattern(
                    rhythm_score=0.7,
                    emphasis_pattern=[0.5, 0.8, 0.6],
                    intonation_curve=[0.4, 0.6, 0.5]
                )
            ],
            expression_frequency=ExpressionFrequency(
                hinglish_terms={"yaar": 3, "na": 2},
                indian_english_phrases={"actually": 5, "basically": 4},
                total_expressions=14
            ),
            confidence_scores=ConfidenceMetrics(
                overall_confidence=0.85,
                prosody_confidence=0.8,
                cultural_marker_confidence=0.9,
                sample_quality_score=0.88
            ),
            extraction_timestamp=datetime.utcnow(),
            audio_sample_metadata=AudioMetadata(
                file_name="test_audio.mp3",
                format=AudioFormat.MP3,
                duration_seconds=120.0,
                file_size_bytes=2048000
            )
        )
        
        # Create style vector
        service = StyleVectorService()
        style_vector = service.create_style_vector(linguistic_dna, version=1)
        
        # Assertions
        assert style_vector.user_id == "test_user_123"
        assert style_vector.version == 1
        assert len(style_vector.embeddings) > 0
        assert len(style_vector.linguistic_features) > 0
        assert style_vector.cultural_context.primary_language == "Indian English"
        
        # Check specific features
        feature_names = [f.feature_name for f in style_vector.linguistic_features]
        assert "speech_rate" in feature_names
        assert "cultural_marker_count" in feature_names
        assert "overall_confidence" in feature_names
    
    def test_style_vector_to_dict_conversion(self):
        """Test bidirectional conversion between StyleVector and dict"""
        # Create sample linguistic DNA
        linguistic_dna = LinguisticDNA(
            user_id="test_user_456",
            prosody_vectors=[
                ProsodyVector(
                    speech_rate=100.0,
                    pause_frequency=10.0,
                    average_pause_duration=0.6,
                    pitch_variation=0.25,
                    energy_variation=0.35
                )
            ],
            cultural_markers=[],
            cadence_patterns=[],
            expression_frequency=ExpressionFrequency(
                hinglish_terms={},
                indian_english_phrases={},
                total_expressions=0
            ),
            confidence_scores=ConfidenceMetrics(
                overall_confidence=0.7,
                prosody_confidence=0.75,
                cultural_marker_confidence=0.65,
                sample_quality_score=0.72
            ),
            extraction_timestamp=datetime.utcnow(),
            audio_sample_metadata=AudioMetadata(
                file_name="test.wav",
                format=AudioFormat.WAV
            )
        )
        
        service = StyleVectorService()
        
        # Create style vector
        original_vector = service.create_style_vector(linguistic_dna)
        
        # Convert to dict
        vector_dict = service.style_vector_to_dict(original_vector)
        
        # Verify dict structure
        assert "user_id" in vector_dict
        assert "vector_id" in vector_dict
        assert "embeddings" in vector_dict
        assert "linguistic_features" in vector_dict
        assert "cultural_context" in vector_dict
        assert "version" in vector_dict
        
        # Convert back to StyleVector
        restored_vector = service.dict_to_style_vector(vector_dict)
        
        # Verify restoration
        assert restored_vector.user_id == original_vector.user_id
        assert restored_vector.vector_id == original_vector.vector_id
        assert len(restored_vector.embeddings) == len(original_vector.embeddings)
        assert len(restored_vector.linguistic_features) == len(original_vector.linguistic_features)


class TestContextInjectionEngine:
    """Test context injection engine"""
    
    def test_create_enhanced_prompt(self):
        """Test creating enhanced prompt from user prompt and style vector"""
        # Create sample style vector
        linguistic_dna = LinguisticDNA(
            user_id="test_user_789",
            prosody_vectors=[
                ProsodyVector(
                    speech_rate=140.0,
                    pause_frequency=12.0,
                    average_pause_duration=0.4,
                    pitch_variation=0.35,
                    energy_variation=0.45
                )
            ],
            cultural_markers=[
                CulturalMarker(
                    expression="basically",
                    frequency=4,
                    context="Basically, we need to finish this",
                    confidence=0.88
                )
            ],
            cadence_patterns=[],
            expression_frequency=ExpressionFrequency(
                hinglish_terms={"yaar": 2},
                indian_english_phrases={"basically": 4, "actually": 3},
                total_expressions=9
            ),
            confidence_scores=ConfidenceMetrics(
                overall_confidence=0.82,
                prosody_confidence=0.8,
                cultural_marker_confidence=0.85,
                sample_quality_score=0.81
            ),
            extraction_timestamp=datetime.utcnow(),
            audio_sample_metadata=AudioMetadata(
                file_name="test.mp3",
                format=AudioFormat.MP3
            )
        )
        
        service = StyleVectorService()
        style_vector = service.create_style_vector(linguistic_dna)
        
        # Create enhanced prompt
        engine = ContextInjectionEngine()
        enhanced_prompt = engine.create_enhanced_prompt(
            user_prompt="Write a LinkedIn post about my new AI project",
            style_vector=style_vector,
            content_type="linkedin_post"
        )
        
        # Assertions
        assert enhanced_prompt.original_prompt == "Write a LinkedIn post about my new AI project"
        assert enhanced_prompt.style_vector == style_vector
        assert len(enhanced_prompt.contextual_instructions) > 0
        assert len(enhanced_prompt.cultural_guidelines) > 0
        assert enhanced_prompt.generation_parameters.model_id == "llama-3.1-70b-versatile"
        
        # Check for LinkedIn-specific instruction
        instructions_text = " ".join(enhanced_prompt.contextual_instructions)
        assert "LinkedIn" in instructions_text or "linkedin" in instructions_text.lower()
    
    def test_format_prompt_for_llm(self):
        """Test formatting enhanced prompt for LLM"""
        # Create minimal style vector
        linguistic_dna = LinguisticDNA(
            user_id="test_user_999",
            prosody_vectors=[
                ProsodyVector(
                    speech_rate=110.0,
                    pause_frequency=14.0,
                    average_pause_duration=0.5,
                    pitch_variation=0.3,
                    energy_variation=0.4
                )
            ],
            cultural_markers=[],
            cadence_patterns=[],
            expression_frequency=ExpressionFrequency(
                hinglish_terms={},
                indian_english_phrases={},
                total_expressions=0
            ),
            confidence_scores=ConfidenceMetrics(
                overall_confidence=0.75,
                prosody_confidence=0.7,
                cultural_marker_confidence=0.8,
                sample_quality_score=0.75
            ),
            extraction_timestamp=datetime.utcnow(),
            audio_sample_metadata=AudioMetadata(
                file_name="test.mp3",
                format=AudioFormat.MP3
            )
        )
        
        service = StyleVectorService()
        style_vector = service.create_style_vector(linguistic_dna)
        
        engine = ContextInjectionEngine()
        enhanced_prompt = engine.create_enhanced_prompt(
            user_prompt="Write an email to my team",
            style_vector=style_vector,
            content_type="email"
        )
        
        # Format for LLM
        formatted_prompt = engine.format_prompt_for_llm(enhanced_prompt)
        
        # Assertions
        assert isinstance(formatted_prompt, str)
        assert len(formatted_prompt) > 0
        assert "User's Communication Style" in formatted_prompt
        assert "Cultural Context" in formatted_prompt
        assert "Instructions" in formatted_prompt
        assert "User Request" in formatted_prompt
        assert "Write an email to my team" in formatted_prompt


class TestGroqIntegration:
    """Test Groq API integration (with mocking)"""
    
    @patch('groq_integration.requests.post')
    def test_generate_content_success(self, mock_post):
        """Test successful content generation with Groq"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response with Indian English expressions, actually."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "total_tokens": 50,
                "prompt_tokens": 30,
                "completion_tokens": 20
            }
        }
        mock_post.return_value = mock_response
        
        # Import after mocking
        from groq_integration import GroqIntegrationService
        
        # Set environment variable
        os.environ['GROQ_API_KEY'] = 'test_key_123'
        
        service = GroqIntegrationService()
        result = service.generate_content(
            prompt="Test prompt",
            temperature=0.7,
            max_tokens=100
        )
        
        # Assertions
        assert result["success"] is True
        assert "generated_text" in result
        assert result["model_used"] == "llama-3.1-70b-versatile"
        assert result["tokens_used"] == 50
        
        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.groq.com/openai/v1/chat/completions"
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_key_123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
