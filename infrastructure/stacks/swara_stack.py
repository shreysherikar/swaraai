"""
Swara AI Identity Layer - Main CDK Stack
Defines all AWS resources for the serverless architecture
"""
import os
from pathlib import Path
from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_kms as kms,
    aws_logs as logs,
    aws_dynamodb as dynamodb,
    aws_ec2 as ec2,
)
from constructs import Construct

# Load .env file
def load_env_file():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()


class SwaraStack(Stack):
    """Main stack for Swara AI Identity Layer infrastructure"""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # KMS Key for encryption
        self.kms_key = kms.Key(
            self,
            "SwaraEncryptionKey",
            description="Swara AI Identity Layer encryption key",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY,  # For dev/hackathon
        )

        # S3 Bucket for audio files and Transcribe output
        self.audio_bucket = s3.Bucket(
            self,
            "SwaraAudioBucket",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.kms_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,  # For dev/hackathon
            auto_delete_objects=True,  # For dev/hackathon
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldAudioFiles",
                    expiration=Duration.days(7),  # Clean up after 7 days
                )
            ],
        )

        # VPC for Lambda functions (optional for MVP)
        # Removed OpenSearch VPC requirement for DynamoDB-based solution
        
        # DynamoDB Table for style vectors (replaces OpenSearch)
        self.style_vectors_table = dynamodb.Table(
            self,
            "SwaraStyleVectorsTable",
            table_name="swara-style-vectors",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
            encryption_key=self.kms_key,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # On-demand for MVP
            removal_policy=RemovalPolicy.DESTROY,  # For dev/hackathon
            point_in_time_recovery=False,  # Disabled for MVP
        )

        # Lambda execution role with necessary permissions
        lambda_role = iam.Role(
            self,
            "SwaraLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # Grant permissions to Lambda role
        self.audio_bucket.grant_read_write(lambda_role)
        self.kms_key.grant_encrypt_decrypt(lambda_role)
        self.style_vectors_table.grant_read_write_data(lambda_role)

        # Add Transcribe permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "transcribe:StartTranscriptionJob",
                    "transcribe:GetTranscriptionJob",
                    "transcribe:DeleteTranscriptionJob",
                ],
                resources=["*"],
            )
        )

        # Add Bedrock permissions
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream",
                ],
                resources=["*"],
            )
        )

        # Lambda Layer for shared dependencies
        lambda_layer = lambda_.LayerVersion(
            self,
            "SwaraDependenciesLayer",
            code=lambda_.Code.from_asset("../lambda/layers/dependencies"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_11],
            description="Shared dependencies for Swara Lambda functions",
        )

        # Lambda function for audio upload
        self.upload_handler = lambda_.Function(
            self,
            "AudioUploadHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.upload_handler.handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "AUDIO_BUCKET": self.audio_bucket.bucket_name,
                "KMS_KEY_ID": self.kms_key.key_id,
            },
            layers=[lambda_layer],
        )

        # Lambda function for voice processing
        self.voice_processor = lambda_.Function(
            self,
            "VoiceProcessor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.voice_processor.handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "AUDIO_BUCKET": self.audio_bucket.bucket_name,
                "DYNAMODB_TABLE_NAME": self.style_vectors_table.table_name,
                "KMS_KEY_ID": self.kms_key.key_id,
            },
            layers=[lambda_layer],
        )

        # Lambda function for content generation
        self.content_generator = lambda_.Function(
            self,
            "ContentGenerator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.content_generator.handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=1024,
            environment={
                "DYNAMODB_TABLE_NAME": self.style_vectors_table.table_name,
                "GROQ_API_KEY": os.environ.get("GROQ_API_KEY", ""),
            },
            layers=[lambda_layer],
        )

        # Lambda function for profile retrieval
        self.profile_handler = lambda_.Function(
            self,
            "ProfileHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.profile_handler.handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.seconds(10),
            memory_size=512,
            environment={
                "DYNAMODB_TABLE_NAME": self.style_vectors_table.table_name,
            },
            layers=[lambda_layer],
        )

        # Lambda function for Transcribe completion (triggered by S3)
        self.transcribe_completion_handler = lambda_.Function(
            self,
            "TranscribeCompletionHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.transcribe_completion_handler.handler",
            code=lambda_.Code.from_asset("../lambda"),
            role=lambda_role,
            timeout=Duration.minutes(2),
            memory_size=1024,
            environment={
                "DYNAMODB_TABLE_NAME": self.style_vectors_table.table_name,
            },
            layers=[lambda_layer],
        )

        # S3 event notification to trigger Lambda when Transcribe output is ready
        from aws_cdk import aws_s3_notifications as s3n
        
        self.audio_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(self.transcribe_completion_handler),
            s3.NotificationKeyFilter(
                prefix="transcribe-output/",
                suffix=".json"
            )
        )

        # API Gateway
        api = apigateway.RestApi(
            self,
            "SwaraAPI",
            rest_api_name="Swara AI Identity Layer API",
            description="API for Swara AI Identity Layer",
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200,
                # Disable logging to avoid CloudWatch Logs role requirement
                logging_level=apigateway.MethodLoggingLevel.OFF,
                data_trace_enabled=False,
                metrics_enabled=True,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Api-Key", "Authorization"],
            ),
        )

        # API Key for authentication
        api_key = api.add_api_key(
            "SwaraAPIKey",
            api_key_name="swara-api-key",
        )

        usage_plan = api.add_usage_plan(
            "SwaraUsagePlan",
            name="Swara Standard Usage Plan",
            throttle=apigateway.ThrottleSettings(
                rate_limit=100,
                burst_limit=200,
            ),
            quota=apigateway.QuotaSettings(
                limit=10000,
                period=apigateway.Period.DAY,
            ),
        )

        usage_plan.add_api_key(api_key)
        usage_plan.add_api_stage(stage=api.deployment_stage)

        # API Resources and Methods
        voice_resource = api.root.add_resource("voice")
        voice_upload = voice_resource.add_resource("upload")
        voice_status = voice_resource.add_resource("status")

        content_resource = api.root.add_resource("content")
        content_generate = content_resource.add_resource("generate")

        profile_resource = api.root.add_resource("profile")

        # POST /voice/upload
        voice_upload.add_method(
            "POST",
            apigateway.LambdaIntegration(self.upload_handler),
            api_key_required=True,
        )

        # GET /voice/status
        voice_status.add_method(
            "GET",
            apigateway.LambdaIntegration(self.voice_processor),
            api_key_required=True,
        )

        # POST /content/generate
        content_generate.add_method(
            "POST",
            apigateway.LambdaIntegration(self.content_generator),
            api_key_required=True,
        )

        # GET /profile
        profile_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.profile_handler),
            api_key_required=True,
        )

        # CloudWatch Log Groups
        logs.LogGroup(
            self,
            "UploadHandlerLogs",
            log_group_name=f"/aws/lambda/{self.upload_handler.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        logs.LogGroup(
            self,
            "VoiceProcessorLogs",
            log_group_name=f"/aws/lambda/{self.voice_processor.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        logs.LogGroup(
            self,
            "ContentGeneratorLogs",
            log_group_name=f"/aws/lambda/{self.content_generator.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        logs.LogGroup(
            self,
            "ProfileHandlerLogs",
            log_group_name=f"/aws/lambda/{self.profile_handler.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )

        logs.LogGroup(
            self,
            "TranscribeCompletionHandlerLogs",
            log_group_name=f"/aws/lambda/{self.transcribe_completion_handler.function_name}",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )
