# Implementation Plan: Swara AI Identity Layer MVP

## Overview

This implementation plan focuses on building a working MVP for the AWS AI Bharath hackathon. The approach prioritizes core functionality: voice calibration with AWS Transcribe, style vector storage in OpenSearch, content generation with AWS Bedrock (Claude 3 Haiku), and a basic Next.js frontend. The implementation uses Python for Lambda functions and leverages AWS managed services for backend infrastructure.

## MVP Scope

The MVP includes:
- Voice upload and processing via AWS Transcribe
- Basic linguistic pattern extraction and style vector creation
- OpenSearch integration for vector storage
- Content generation with Bedrock (Claude 3 Haiku)
- Simple Next.js frontend with API integration
- Essential security (IAM, KMS encryption)
- API Gateway for Lambda orchestration

## Tasks

- [x] 1. Set up AWS infrastructure and project foundation
  - Create AWS CDK or SAM project structure for infrastructure as code
  - Configure AWS credentials and region settings
  - Set up Python virtual environment with boto3, AWS SDK dependencies
  - Create basic project directory structure: `/lambda`, `/frontend`, `/infrastructure`
  - Initialize Git repository with .gitignore for AWS and Python
  - _Requirements: 4.4, 5.1_

- [x] 2. Implement voice calibration Lambda function
  - [x] 2.1 Create audio upload handler Lambda
    - Write Lambda function to receive audio files via API Gateway
    - Implement S3 upload for temporary audio storage
    - Add support for MP3, WAV, M4A format detection
    - Return upload confirmation with job ID
    - _Requirements: 1.1, 1.5_
  
  - [x] 2.2 Implement AWS Transcribe integration
    - Create Lambda function to trigger Transcribe jobs
    - Configure custom vocabulary for Hinglish terms (e.g., "yaar", "actually", "basically")
    - Set up S3 bucket for Transcribe output
    - Implement job status polling mechanism
    - _Requirements: 1.1, 1.2_
  
  - [x] 2.3 Build linguistic DNA extractor
    - Parse Transcribe JSON output for transcript text
    - Extract basic prosody features (word timing, pauses, speech rate)
    - Identify cultural markers using keyword matching for common Indian English patterns
    - Generate confidence scores based on audio duration and word count
    - Create LinguisticDNA data structure with extracted features
    - _Requirements: 1.2, 1.3_
  
  - [ ]* 2.4 Write property test for voice processing pipeline
    - **Property 1: Voice Processing Pipeline Integrity**
    - **Validates: Requirements 1.1, 1.2, 1.3**
    - Use Hypothesis to generate test audio file metadata
    - Verify pipeline produces valid LinguisticDNA for all supported formats

- [x] 3. Implement Identity Layer and OpenSearch integration
  - [x] 3.1 Set up Amazon OpenSearch cluster
    - Create OpenSearch domain using AWS CDK/SAM
    - Configure VPC settings and security groups
    - Set up index mapping for style vectors with k-NN plugin
    - Enable encryption at rest using AWS KMS
    - _Requirements: 2.2, 2.4_
  
  - [x] 3.2 Create style vector generation service
    - Implement vector embedding using sentence-transformers or AWS Titan Embeddings
    - Convert LinguisticDNA features to numerical embeddings
    - Create StyleVector data structure with user_id, embeddings, metadata
    - Add version numbering for style vector updates
    - _Requirements: 2.1, 2.5_
  
  - [x] 3.3 Build OpenSearch storage Lambda
    - Write Lambda function to store StyleVector in OpenSearch
    - Implement user-specific indexing with user_id as primary key
    - Add error handling for connection failures with retry logic
    - Create retrieval function to fetch StyleVector by user_id
    - _Requirements: 2.2, 2.3_
  
  - [ ]* 3.4 Write property test for style vector lifecycle
    - **Property 4: Style Vector Lifecycle Consistency**
    - **Validates: Requirements 2.1, 2.2, 2.3**
    - Verify round-trip consistency: LinguisticDNA → StyleVector → Storage → Retrieval

- [x] 4. Checkpoint - Verify voice and storage pipeline
  - Test end-to-end: audio upload → Transcribe → linguistic extraction → OpenSearch storage
  - Verify OpenSearch contains valid style vectors
  - Ensure all tests pass, ask the user if questions arise

- [x] 5. Implement content generation with AWS Bedrock
  - [x] 5.1 Create context injection engine
    - Build function to combine user prompt with StyleVector
    - Format enhanced prompt with linguistic instructions
    - Include cultural guidelines (preserve Indian English expressions)
    - Add authenticity targets based on cultural markers
    - _Requirements: 2.3, 3.1_
  
  - [x] 5.2 Implement Bedrock integration Lambda
    - Set up AWS Bedrock client with Claude 3 Haiku model
    - Configure model parameters (temperature, max_tokens, top_p)
    - Send enhanced prompt to Bedrock API
    - Parse and validate Bedrock response
    - _Requirements: 3.2_
  
  - [x] 5.3 Build content generation orchestrator
    - Create Lambda to orchestrate: retrieve StyleVector → inject context → call Bedrock
    - Implement response formatting for text, HTML, Markdown
    - Add basic cultural authenticity validation (check for preserved markers)
    - Return GeneratedContent with metadata
    - _Requirements: 3.3, 3.4, 3.5_
  
  - [ ]* 5.4 Write property test for content generation
    - **Property 7: Cultural Content Generation Authenticity**
    - **Validates: Requirements 3.1, 3.3, 3.4**
    - Verify generated content includes cultural markers from StyleVector

- [x] 6. Set up API Gateway and Lambda orchestration
  - [x] 6.1 Create API Gateway REST API
    - Define API endpoints: POST /voice/upload, GET /voice/status, POST /content/generate
    - Configure Lambda proxy integrations
    - Set up CORS for frontend access
    - Add request validation schemas
    - _Requirements: 8.1_
  
  - [x] 6.2 Implement authentication and authorization
    - Set up API Gateway API keys for MVP
    - Create IAM roles for Lambda execution
    - Configure Lambda permissions for S3, Transcribe, OpenSearch, Bedrock
    - Add basic rate limiting (100 requests per minute)
    - _Requirements: 5.1, 8.2_
  
  - [ ]* 6.3 Write unit tests for API endpoints
    - Test authentication failures
    - Test request validation
    - Test error responses

- [x] 7. Build Next.js frontend
  - [x] 7.1 Initialize Next.js 14 project
    - Create Next.js app with TypeScript
    - Set up Tailwind CSS for styling
    - Configure environment variables for API Gateway URL
    - Create basic layout with navigation
    - _Requirements: 4.1_
  
  - [x] 7.2 Implement voice calibration UI
    - Create audio upload component with drag-and-drop
    - Add file format validation (MP3, WAV, M4A)
    - Implement upload progress indicator
    - Show processing status with polling
    - Display success/error messages
    - _Requirements: 1.5, 4.5_
  
  - [x] 7.3 Build content generation interface
    - Create text input for user prompts
    - Add content type selector (email, LinkedIn post, presentation)
    - Implement generate button with loading state
    - Display generated content with formatting options
    - Add copy-to-clipboard functionality
    - _Requirements: 3.5, 6.2_
  
  - [x] 7.4 Add basic user profile page
    - Show user's linguistic profile summary
    - Display confidence scores and cultural markers
    - Add option to re-calibrate voice
    - _Requirements: 1.3, 7.1_

- [x] 8. Checkpoint - Test full MVP workflow
  - Test complete user journey: sign up → upload voice → generate content
  - Verify all AWS services are properly connected
  - Ensure all tests pass, ask the user if questions arise

- [x] 9. Implement security and compliance essentials
  - [x] 9.1 Configure AWS KMS encryption
    - Create customer-managed KMS key
    - Enable encryption for S3 buckets
    - Configure OpenSearch encryption at rest
    - Add encryption in transit for all API calls
    - _Requirements: 2.4, 5.2_
  
  - [x] 9.2 Set up CloudTrail logging
    - Enable CloudTrail for all API calls
    - Configure S3 bucket for audit logs
    - Set up log retention policy
    - _Requirements: 5.4_
  
  - [x] 9.3 Implement stateless processing
    - Ensure Lambda functions don't persist PII to disk
    - Use environment variables for configuration
    - Implement proper cleanup in Lambda handlers
    - _Requirements: 5.1_
  
  - [ ]* 9.4 Write property test for security measures
    - **Property 13: Stateless Processing Security**
    - **Validates: Requirements 5.1**
    - Verify no PII is written to persistent storage during processing

- [x] 10. Add error handling and monitoring
  - [x] 10.1 Implement comprehensive error handling
    - Add try-catch blocks in all Lambda functions
    - Return structured error responses with error codes
    - Implement fallback for Transcribe failures
    - Add retry logic for OpenSearch and Bedrock calls
    - _Requirements: 8.4_
  
  - [x] 10.2 Set up CloudWatch monitoring
    - Create CloudWatch dashboards for Lambda metrics
    - Set up alarms for error rates and latency
    - Configure log groups for all Lambda functions
    - Add custom metrics for voice processing and content generation
    - _Requirements: 4.1, 4.3_

- [x] 11. Deploy and test MVP
  - [x] 11.1 Deploy infrastructure to AWS
    - Deploy CDK/SAM stack to AWS account
    - Verify all resources are created correctly
    - Test API Gateway endpoints with Postman/curl
    - _Requirements: 4.4_
  
  - [x] 11.2 Deploy Next.js frontend
    - Build Next.js production bundle
    - Deploy to Vercel or AWS Amplify
    - Configure environment variables for production API
    - Test frontend-backend integration
    - _Requirements: 4.1_
  
  - [x] 11.3 Perform end-to-end testing
    - Test with real audio samples
    - Verify content generation quality
    - Check performance metrics (response times)
    - Validate error handling scenarios
    - _Requirements: 4.1, 4.3_

- [x] 12. Final checkpoint and hackathon preparation
  - Ensure all core features are working
  - Prepare demo script and test data
  - Document API endpoints and architecture
  - Create presentation materials
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property tests that can be skipped for faster MVP delivery
- Focus on getting a working demo with real AWS services integration
- Use AWS Free Tier where possible to minimize costs
- Prioritize functionality over polish for hackathon timeline
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback

## AWS Services Connection Guide

### Backend Architecture
- **API Gateway** → triggers Lambda functions
- **Lambda (Python)** → orchestrates all services
- **S3** → temporary audio storage
- **Transcribe** → voice-to-text conversion
- **OpenSearch** → vector storage and retrieval
- **Bedrock** → content generation with Claude 3 Haiku
- **KMS** → encryption key management
- **CloudTrail** → audit logging
- **CloudWatch** → monitoring and logs

### Data Flow
1. Frontend uploads audio → API Gateway → Lambda → S3
2. Lambda triggers Transcribe job → Transcribe processes audio → outputs to S3
3. Lambda reads Transcribe output → extracts linguistic DNA → creates style vector
4. Lambda stores style vector → OpenSearch
5. User requests content → Lambda retrieves style vector from OpenSearch
6. Lambda injects context → calls Bedrock → returns generated content
7. Frontend displays content to user

### Infrastructure as Code
Use AWS CDK (Python) or SAM to define all resources:
- API Gateway with Lambda integrations
- Lambda functions with proper IAM roles
- S3 buckets with encryption
- OpenSearch domain with VPC configuration
- KMS keys for encryption
- CloudWatch log groups and alarms
