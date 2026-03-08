"""
Content Generator Lambda Function
Generates culturally aware content using Groq and user style vectors
Orchestrates: retrieve StyleVector → inject context → call Groq → format response
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List
import sys

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import (
    GeneratedContent,
    CulturalMarker,
    EngagementMetrics,
    GenerationMetadata,
)
from handlers.dynamodb_storage import DynamoDBStorageService
from handlers.context_injection import ContextInjectionEngine
from handlers.groq_integration import GroqIntegrationService


class ContentGenerationOrchestrator:
    """Orchestrates the content generation pipeline"""
    
    def __init__(self):
        """Initialize services"""
        self.storage_service = DynamoDBStorageService()
        self.context_engine = ContextInjectionEngine()
        self.groq_service = GroqIntegrationService()
    
    def generate_content(
        self,
        user_id: str,
        user_prompt: str,
        content_type: str = "general"
    ) -> GeneratedContent:
        """
        Generate content with cultural awareness
        
        Args:
            user_id: The user ID
            user_prompt: The user's content request
            content_type: Type of content to generate
            
        Returns:
            GeneratedContent with text and metadata
        """
        start_time = datetime.utcnow()
        
        # Step 1: Retrieve style vector from DynamoDB
        style_vector = self.storage_service.retrieve_style_vector(user_id)
        
        if not style_vector:
            raise Exception(f"Style vector not found for user_id: {user_id}. Please complete voice calibration first.")
        
        # Step 2: Inject context to create enhanced prompt
        enhanced_prompt = self.context_engine.create_enhanced_prompt(
            user_prompt=user_prompt,
            style_vector=style_vector,
            content_type=content_type
        )
        
        # Step 3: Format prompt for LLM
        formatted_prompt = self.context_engine.format_prompt_for_llm(enhanced_prompt)
        
        # Step 4: Call Groq API
        groq_result = self.groq_service.generate_content(
            prompt=formatted_prompt,
            temperature=enhanced_prompt.generation_parameters.temperature,
            max_tokens=enhanced_prompt.generation_parameters.max_tokens,
            top_p=enhanced_prompt.generation_parameters.top_p
        )
        
        generated_text = groq_result["generated_text"]
        
        # Step 5: Validate cultural authenticity
        cultural_markers = self._extract_cultural_markers(
            generated_text,
            style_vector.cultural_context.regional_influences
        )
        
        authenticity_score = self._calculate_authenticity_score(
            cultural_markers,
            enhanced_prompt.authenticity_targets
        )
        
        # Step 6: Format response
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Create engagement prediction
        engagement_prediction = EngagementMetrics(
            authenticity_score=authenticity_score,
            predicted_engagement_rate=self._predict_engagement(authenticity_score),
            cultural_relevance_score=self._calculate_cultural_relevance(cultural_markers)
        )
        
        # Create generation metadata
        generation_metadata = GenerationMetadata(
            generation_timestamp=end_time,
            model_used=groq_result["model_used"],
            processing_time_ms=processing_time_ms,
            tokens_used=groq_result["tokens_used"]
        )
        
        # Create generated content
        generated_content = GeneratedContent(
            content_id=str(uuid.uuid4()),
            user_id=user_id,
            original_prompt=user_prompt,
            generated_text=generated_text,
            authenticity_score=authenticity_score,
            cultural_markers=cultural_markers,
            engagement_prediction=engagement_prediction,
            generation_metadata=generation_metadata
        )
        
        return generated_content
    
    def _extract_cultural_markers(
        self,
        text: str,
        regional_influences: List[str]
    ) -> List[CulturalMarker]:
        """
        Extract cultural markers from generated text
        
        Args:
            text: The generated text
            regional_influences: Regional influences to look for
            
        Returns:
            List of cultural markers found
        """
        markers = []
        
        # Common Indian English expressions
        indian_english_expressions = [
            "actually", "basically", "only", "itself", "yaar", "na",
            "prepone", "do the needful", "revert back", "out of station",
            "good name", "what is your good name", "pass out", "cousin brother",
            "cousin sister", "timepass", "updation"
        ]
        
        text_lower = text.lower()
        
        for expression in indian_english_expressions:
            if expression in text_lower:
                # Count occurrences
                count = text_lower.count(expression)
                
                # Find context (surrounding words)
                index = text_lower.find(expression)
                start = max(0, index - 20)
                end = min(len(text), index + len(expression) + 20)
                context = text[start:end].strip()
                
                markers.append(CulturalMarker(
                    expression=expression,
                    frequency=count,
                    context=context,
                    confidence=0.8
                ))
        
        return markers
    
    def _calculate_authenticity_score(
        self,
        cultural_markers: List[CulturalMarker],
        authenticity_targets: List
    ) -> float:
        """
        Calculate authenticity score based on cultural markers
        
        Args:
            cultural_markers: Extracted cultural markers
            authenticity_targets: Target authenticity metrics
            
        Returns:
            Authenticity score (0-1)
        """
        if not authenticity_targets:
            # Base score on presence of cultural markers
            return min(1.0, len(cultural_markers) * 0.2 + 0.5)
        
        # Calculate based on targets
        total_score = 0.0
        for target in authenticity_targets:
            if target.marker_type == "cultural_expressions":
                actual_frequency = len(cultural_markers) / 100.0
                target_frequency = target.target_frequency
                
                # Score based on how close we are to target
                diff = abs(actual_frequency - target_frequency)
                if diff <= target.tolerance:
                    total_score += 1.0
                else:
                    total_score += max(0.0, 1.0 - (diff / target.tolerance))
        
        # Average score
        if len(authenticity_targets) > 0:
            return total_score / len(authenticity_targets)
        
        return 0.7  # Default score
    
    def _predict_engagement(self, authenticity_score: float) -> float:
        """
        Predict engagement rate based on authenticity
        
        Args:
            authenticity_score: The authenticity score
            
        Returns:
            Predicted engagement rate
        """
        # Simple linear model: higher authenticity = higher engagement
        base_engagement = 0.05  # 5% base engagement
        authenticity_boost = authenticity_score * 0.20  # Up to 20% boost
        
        return min(1.0, base_engagement + authenticity_boost)
    
    def _calculate_cultural_relevance(self, cultural_markers: List[CulturalMarker]) -> float:
        """
        Calculate cultural relevance score
        
        Args:
            cultural_markers: List of cultural markers
            
        Returns:
            Cultural relevance score (0-1)
        """
        if not cultural_markers:
            return 0.5  # Neutral score
        
        # Score based on number and confidence of markers
        total_confidence = sum(m.confidence for m in cultural_markers)
        avg_confidence = total_confidence / len(cultural_markers)
        
        # Combine count and confidence
        count_score = min(1.0, len(cultural_markers) / 5.0)  # Max at 5 markers
        
        return (count_score * 0.6) + (avg_confidence * 0.4)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for content generation with cultural awareness
    
    Args:
        event: API Gateway event with user prompt and user_id
        context: Lambda context
        
    Returns:
        API Gateway response with generated content
    """
    # CORS headers
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Api-Key,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    }
    
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        
        # Validate required fields
        if "prompt" not in body or "user_id" not in body:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Missing required fields: prompt, user_id"
                })
            }
        
        user_prompt = body["prompt"]
        user_id = body["user_id"]
        content_type = body.get("content_type", "general")
        
        # Initialize orchestrator
        orchestrator = ContentGenerationOrchestrator()
        
        # Generate content
        generated_content = orchestrator.generate_content(
            user_id=user_id,
            user_prompt=user_prompt,
            content_type=content_type
        )
        
        # Format response
        response_data = {
            "success": True,
            "content_id": generated_content.content_id,
            "generated_text": generated_content.generated_text,
            "authenticity_score": generated_content.authenticity_score,
            "cultural_markers": [
                {
                    "expression": m.expression,
                    "frequency": m.frequency,
                    "context": m.context,
                    "confidence": m.confidence
                }
                for m in generated_content.cultural_markers
            ],
            "engagement_prediction": {
                "authenticity_score": generated_content.engagement_prediction.authenticity_score,
                "predicted_engagement_rate": generated_content.engagement_prediction.predicted_engagement_rate,
                "cultural_relevance_score": generated_content.engagement_prediction.cultural_relevance_score
            },
            "metadata": {
                "model_used": generated_content.generation_metadata.model_used,
                "processing_time_ms": generated_content.generation_metadata.processing_time_ms,
                "tokens_used": generated_content.generation_metadata.tokens_used
            }
        }
        
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(response_data)
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({
                "error": f"Internal server error: {str(e)}"
            })
        }

