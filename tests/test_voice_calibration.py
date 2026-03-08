"""
Unit tests for voice calibration Lambda functions
"""
import json
import base64
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# Mock AWS environment
@pytest.fixture(autouse=True)
def mock_aws_env(monkeypatch):
    """Set up mock AWS environment variables"""
    monkeypatch.setenv('AUDIO_BUCKET', 'test-bucket')
    monkeypatch.setenv('KMS_KEY_ID', 'test-key-id')


@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    with patch('boto3.client') as mock_client:
        s3_mock = MagicMock()
        mock_client.return_value = s3_mock
        yield s3_mock


class TestAudioUploadHandler:
    """Tests for audio upload handler"""
    
    def test_detect_audio_format_from_extension(self):
        """Test audio format detection from file extension"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import detect_audio_format
        
        assert detect_audio_format("test.mp3") == "mp3"
        assert detect_audio_format("test.wav") == "wav"
        assert detect_audio_format("test.m4a") == "m4a"
        assert detect_audio_format("test.MP3") == "mp3"  # Case insensitive
    
    def test_detect_audio_format_from_content_type(self):
        """Test audio format detection from content type"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import detect_audio_format
        
        assert detect_audio_format("test.unknown", "audio/mpeg") == "mp3"
        assert detect_audio_format("test.unknown", "audio/wav") == "wav"
        assert detect_audio_format("test.unknown", "audio/mp4") == "m4a"
    
    def test_detect_audio_format_unsupported(self):
        """Test unsupported audio format returns None"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import detect_audio_format
        
        assert detect_audio_format("test.txt") is None
        assert detect_audio_format("test.unknown", "text/plain") is None
    
    def test_upload_handler_missing_fields(self):
        """Test upload handler with missing required fields"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import handler
        
        event = {
            "body": json.dumps({})
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "error" in body
        assert "Missing required fields" in body["error"]
    
    def test_upload_handler_unsupported_format(self):
        """Test upload handler with unsupported audio format"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import handler
        
        event = {
            "body": json.dumps({
                "audio_data": base64.b64encode(b"test audio data").decode('utf-8'),
                "file_name": "test.txt"
            })
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Unsupported audio format" in body["error"]
    
    def test_upload_handler_invalid_base64(self):
        """Test upload handler with invalid base64 data"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import handler
        
        event = {
            "body": json.dumps({
                "audio_data": "not-valid-base64!!!",
                "file_name": "test.mp3"
            })
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Invalid base64" in body["error"]
    
    @patch('upload_handler.s3_client')
    def test_upload_handler_success(self, mock_s3):
        """Test successful audio upload"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from upload_handler import handler
        
        # Mock S3 put_object
        mock_s3.put_object.return_value = {}
        
        audio_data = b"fake audio data"
        event = {
            "body": json.dumps({
                "audio_data": base64.b64encode(audio_data).decode('utf-8'),
                "file_name": "test.mp3",
                "user_id": "user123"
            })
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "job_id" in body
        assert body["format"] == "mp3"
        assert body["user_id"] == "user123"
        assert body["status"] == "uploaded"
        
        # Verify S3 was called
        mock_s3.put_object.assert_called_once()


class TestLinguisticDNAExtractor:
    """Tests for linguistic DNA extractor"""
    
    def test_identify_hinglish_terms(self):
        """Test identification of Hinglish terms"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from linguistic_dna_extractor import identify_cultural_markers
        
        text = "Hey yaar, how are you? Actually, I'm doing theek hai. Yaar, let's meet."
        markers, freq = identify_cultural_markers(text)
        
        # Should find "yaar" (appears twice), "theek", "hai"
        expressions = [m.expression for m in markers]
        assert "yaar" in expressions
        assert "theek" in expressions or "hai" in expressions  # At least one should be found
    
    def test_identify_indian_english_phrases(self):
        """Test identification of Indian English phrases"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from linguistic_dna_extractor import identify_cultural_markers
        
        text = "Please do the needful and revert back. I need to prepone the meeting."
        markers, freq = identify_cultural_markers(text)
        
        expressions = [m.expression for m in markers]
        assert "do the needful" in expressions
        assert "revert back" in expressions
        assert "prepone" in expressions
    
    def test_prosody_extraction_empty_items(self):
        """Test prosody extraction with empty transcript"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from linguistic_dna_extractor import extract_prosody_features
        
        transcript_data = {"results": {"items": []}}
        prosody = extract_prosody_features(transcript_data)
        
        assert prosody.speech_rate == 0.0
        assert prosody.pause_frequency == 0.0
    
    def test_prosody_extraction_with_data(self):
        """Test prosody extraction with sample data"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from linguistic_dna_extractor import extract_prosody_features
        
        transcript_data = {
            "results": {
                "items": [
                    {
                        "type": "pronunciation",
                        "start_time": "0.0",
                        "end_time": "0.5",
                        "alternatives": [{"confidence": "0.95"}]
                    },
                    {
                        "type": "pronunciation",
                        "start_time": "0.8",
                        "end_time": "1.2",
                        "alternatives": [{"confidence": "0.90"}]
                    },
                    {
                        "type": "pronunciation",
                        "start_time": "1.5",
                        "end_time": "2.0",
                        "alternatives": [{"confidence": "0.92"}]
                    }
                ]
            }
        }
        
        prosody = extract_prosody_features(transcript_data)
        
        assert prosody.speech_rate > 0
        assert prosody.pause_frequency >= 0
        assert prosody.average_pause_duration >= 0
    
    def test_confidence_score_calculation(self):
        """Test confidence score generation"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from linguistic_dna_extractor import generate_confidence_scores
        
        transcript_data = {"results": {"items": []}}
        cultural_markers = [Mock() for _ in range(5)]
        
        scores = generate_confidence_scores(
            transcript_data=transcript_data,
            cultural_markers=cultural_markers,
            audio_duration=60.0,
            word_count=100
        )
        
        assert 0.0 <= scores.overall_confidence <= 1.0
        assert 0.0 <= scores.prosody_confidence <= 1.0
        assert 0.0 <= scores.cultural_marker_confidence <= 1.0
        assert 0.0 <= scores.sample_quality_score <= 1.0


class TestVoiceProcessor:
    """Tests for voice processor orchestration"""
    
    @patch('voice_processor.transcribe_client')
    def test_get_transcription_status_completed(self, mock_transcribe):
        """Test getting status of completed transcription"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from voice_processor import get_transcription_status
        
        mock_transcribe.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'COMPLETED',
                'CreationTime': datetime.utcnow(),
                'Transcript': {
                    'TranscriptFileUri': 's3://bucket/path/to/transcript.json'
                }
            }
        }
        
        status = get_transcription_status("test-job")
        
        assert status['status'] == 'COMPLETED'
        assert 'transcript_uri' in status
        assert status['transcript_bucket'] == 'bucket'
        assert status['transcript_key'] == 'path/to/transcript.json'
    
    @patch('voice_processor.transcribe_client')
    def test_get_transcription_status_failed(self, mock_transcribe):
        """Test getting status of failed transcription"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from voice_processor import get_transcription_status
        
        mock_transcribe.get_transcription_job.return_value = {
            'TranscriptionJob': {
                'TranscriptionJobStatus': 'FAILED',
                'CreationTime': datetime.utcnow(),
                'FailureReason': 'Invalid audio format'
            }
        }
        
        status = get_transcription_status("test-job")
        
        assert status['status'] == 'FAILED'
        assert 'failure_reason' in status
        assert status['failure_reason'] == 'Invalid audio format'
    
    def test_voice_processor_missing_job_id(self):
        """Test voice processor with missing job_id"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'handlers'))
        from voice_processor import handler
        
        event = {
            "queryStringParameters": {}
        }
        
        response = handler(event, None)
        
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "Missing required parameter" in body["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
