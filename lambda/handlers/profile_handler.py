"""
Profile Handler Lambda Function
Retrieves user profile and linguistic DNA information
"""
import json
import os
from typing import Dict, Any
from datetime import datetime

from handlers.dynamodb_storage import DynamoDBStorageService


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for retrieving user profile
    
    Args:
        event: API Gateway event with user_id
        context: Lambda context
        
    Returns:
        API Gateway response with user profile
    """
    # CORS headers
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Api-Key,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    }
    
    try:
        # Get user_id from query parameters or path parameters
        user_id = None
        
        if event.get("queryStringParameters"):
            user_id = event["queryStringParameters"].get("user_id")
        
        if not user_id and event.get("pathParameters"):
            user_id = event["pathParameters"].get("user_id")
        
        # Default to test user if not provided
        if not user_id:
            user_id = "test_user_123"
        
        # Initialize storage service
        storage_service = DynamoDBStorageService()
        
        # Retrieve style vector
        style_vector = storage_service.retrieve_style_vector(user_id)
        
        if not style_vector:
            return {
                "statusCode": 404,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Profile not found. Please complete voice calibration first."
                })
            }
        
        # Format response
        response_data = {
            "userId": user_id,
            "confidence": getattr(style_vector, 'confidence_score', getattr(style_vector, 'confidence', 0.85)),
            "lastCalibrated": style_vector.created_at.isoformat() if hasattr(style_vector.created_at, 'isoformat') else str(style_vector.created_at),
            "prosodyFeatures": {
                "speechRate": int(style_vector.prosody_features.speech_rate),
                "pausePatterns": style_vector.prosody_features.pause_patterns,
                "tonalVariation": style_vector.prosody_features.tonal_variation
            },
            "culturalMarkers": style_vector.cultural_context.regional_influences[:10],  # Top 10
            "hinglishPatterns": style_vector.cultural_context.code_mixing_patterns[:8]  # Top 8
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
