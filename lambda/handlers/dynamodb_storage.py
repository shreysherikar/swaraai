"""
DynamoDB Storage Service
Handles storage and retrieval of StyleVectors in DynamoDB
"""
import json
import os
import boto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
import sys

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import StyleVector
from handlers.style_vector_service import StyleVectorService


class DynamoDBStorageService:
    """Service for storing and retrieving style vectors in DynamoDB"""
    
    def __init__(self):
        """Initialize DynamoDB client"""
        self.dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
        self.table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'swara-style-vectors')
        self.table = self.dynamodb.Table(self.table_name)
        self.style_vector_service = StyleVectorService()
    
    def store_style_vector(self, style_vector: StyleVector) -> Dict[str, Any]:
        """
        Store a style vector in DynamoDB
        
        Args:
            style_vector: The style vector to store
            
        Returns:
            Response with success status
            
        Raises:
            Exception: If storage fails after retries
        """
        try:
            # Convert style vector to dictionary
            item = self.style_vector_service.style_vector_to_dict(style_vector)
            
            # Store in DynamoDB with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.table.put_item(Item=item)
                    
                    return {
                        "success": True,
                        "user_id": style_vector.user_id,
                        "vector_id": style_vector.vector_id,
                        "version": style_vector.version,
                        "message": "Style vector stored successfully"
                    }
                    
                except ClientError as e:
                    if attempt == max_retries - 1:
                        raise
                    # Exponential backoff
                    import time
                    time.sleep(2 ** attempt)
                    
        except Exception as e:
            error_msg = f"Failed to store style vector: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def retrieve_style_vector(self, user_id: str) -> Optional[StyleVector]:
        """
        Retrieve a style vector from DynamoDB by user_id
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            StyleVector if found, None otherwise
            
        Raises:
            Exception: If retrieval fails
        """
        try:
            # Get item from DynamoDB with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.table.get_item(Key={'user_id': user_id})
                    
                    if 'Item' not in response:
                        return None
                    
                    # Convert dictionary to StyleVector
                    style_vector = self.style_vector_service.dict_to_style_vector(response['Item'])
                    return style_vector
                    
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceNotFoundException':
                        return None
                    if attempt == max_retries - 1:
                        raise
                    # Exponential backoff
                    import time
                    time.sleep(2 ** attempt)
                    
        except Exception as e:
            error_msg = f"Failed to retrieve style vector: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)
    
    def update_style_vector(self, style_vector: StyleVector) -> Dict[str, Any]:
        """
        Update an existing style vector (increments version)
        
        Args:
            style_vector: The updated style vector
            
        Returns:
            Response with success status
        """
        # Increment version
        style_vector.version += 1
        
        # Store updated vector
        return self.store_style_vector(style_vector)
    
    def delete_style_vector(self, user_id: str) -> Dict[str, Any]:
        """
        Delete a style vector from DynamoDB
        
        Args:
            user_id: The user ID to delete
            
        Returns:
            Response with success status
        """
        try:
            self.table.delete_item(Key={'user_id': user_id})
            
            return {
                "success": True,
                "user_id": user_id,
                "message": "Style vector deleted successfully"
            }
            
        except Exception as e:
            error_msg = f"Failed to delete style vector: {str(e)}"
            print(error_msg)
            raise Exception(error_msg)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for DynamoDB storage operations
    
    Supports operations: store, retrieve, update, delete
    
    Args:
        event: API Gateway event with operation and data
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Parse request
        body = json.loads(event.get("body", "{}"))
        operation = body.get("operation")
        
        if not operation:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Missing required field: operation"
                })
            }
        
        # Initialize storage service
        storage_service = DynamoDBStorageService()
        
        # Handle operations
        if operation == "retrieve":
            user_id = body.get("user_id")
            if not user_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": "Missing required field: user_id"
                    })
                }
            
            style_vector = storage_service.retrieve_style_vector(user_id)
            
            if not style_vector:
                return {
                    "statusCode": 404,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": f"Style vector not found for user_id: {user_id}"
                    })
                }
            
            # Convert to dict for response
            vector_dict = storage_service.style_vector_service.style_vector_to_dict(style_vector)
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "success": True,
                    "style_vector": vector_dict
                })
            }
        
        elif operation == "delete":
            user_id = body.get("user_id")
            if not user_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": "Missing required field: user_id"
                    })
                }
            
            result = storage_service.delete_style_vector(user_id)
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(result)
            }
        
        else:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": f"Unsupported operation: {operation}"
                })
            }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": f"Internal server error: {str(e)}"
            })
        }
