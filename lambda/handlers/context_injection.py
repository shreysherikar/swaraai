"""
Context Injection Engine
Combines user prompts with StyleVector to create enhanced prompts
"""
import json
from typing import Dict, Any, List
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from shared.models import (
    StyleVector,
    EnhancedPrompt,
    AuthenticityTarget,
    GenerationConfig,
    ContentType,
)


class ContextInjectionEngine:
    """Engine for injecting style context into user prompts"""
    
    def __init__(self):
        """Initialize the context injection engine"""
        pass
    
    def create_enhanced_prompt(
        self,
        user_prompt: str,
        style_vector: StyleVector,
        content_type: str = "general"
    ) -> EnhancedPrompt:
        """
        Combine user prompt with style vector to create enhanced prompt
        
        Args:
            user_prompt: The original user prompt
            style_vector: The user's style vector
            content_type: Type of content (email, linkedin_post, etc.)
            
        Returns:
            EnhancedPrompt with context and instructions
        """
        # Generate contextual instructions
        contextual_instructions = self._generate_contextual_instructions(
            style_vector,
            content_type
        )
        
        # Generate cultural guidelines
        cultural_guidelines = self._generate_cultural_guidelines(style_vector)
        
        # Generate authenticity targets
        authenticity_targets = self._generate_authenticity_targets(style_vector)
        
        # Create generation config
        generation_config = GenerationConfig(
            temperature=0.7,
            max_tokens=1000,
            top_p=0.9,
            model_id="llama-3.3-70b-versatile"  # Updated Groq model
        )
        
        return EnhancedPrompt(
            original_prompt=user_prompt,
            style_vector=style_vector,
            contextual_instructions=contextual_instructions,
            cultural_guidelines=cultural_guidelines,
            authenticity_targets=authenticity_targets,
            generation_parameters=generation_config
        )
    
    def _generate_contextual_instructions(
        self,
        style_vector: StyleVector,
        content_type: str
    ) -> List[str]:
        """
        Generate contextual instructions based on style vector
        
        Args:
            style_vector: The user's style vector
            content_type: Type of content
            
        Returns:
            List of contextual instructions
        """
        instructions = []
        
        # Add speech rate instruction
        speech_rate_feature = next(
            (f for f in style_vector.linguistic_features if f.feature_name == "speech_rate"),
            None
        )
        if speech_rate_feature:
            if speech_rate_feature.feature_value > 150:
                instructions.append("Write in a dynamic, energetic style with shorter sentences.")
            elif speech_rate_feature.feature_value < 100:
                instructions.append("Write in a thoughtful, deliberate style with well-paced sentences.")
            else:
                instructions.append("Write in a balanced, conversational style.")
        
        # Add cultural marker instruction
        cultural_marker_count = next(
            (f for f in style_vector.linguistic_features if f.feature_name == "cultural_marker_count"),
            None
        )
        if cultural_marker_count and cultural_marker_count.feature_value > 0:
            instructions.append("Incorporate Indian English expressions naturally where appropriate.")
        
        # Add content-type specific instructions
        if content_type == "email":
            instructions.append("Format as a professional email with appropriate greeting and closing.")
        elif content_type == "linkedin_post":
            instructions.append("Format as an engaging LinkedIn post with a hook and call-to-action.")
        elif content_type == "presentation":
            instructions.append("Format as presentation content with clear structure and bullet points.")
        
        return instructions
    
    def _generate_cultural_guidelines(self, style_vector: StyleVector) -> List[str]:
        """
        Generate cultural guidelines for content generation
        
        Args:
            style_vector: The user's style vector
            
        Returns:
            List of cultural guidelines
        """
        guidelines = [
            "Preserve Indian English expressions and idioms naturally.",
            "Maintain authenticity while ensuring professional tone.",
            "Use culturally relevant examples and references when appropriate.",
        ]
        
        # Add regional influence guidelines
        if style_vector.cultural_context.regional_influences:
            regional_text = ", ".join(style_vector.cultural_context.regional_influences[:3])
            guidelines.append(f"Consider regional influences: {regional_text}")
        
        return guidelines
    
    def _generate_authenticity_targets(self, style_vector: StyleVector) -> List[AuthenticityTarget]:
        """
        Generate authenticity targets based on style vector
        
        Args:
            style_vector: The user's style vector
            
        Returns:
            List of authenticity targets
        """
        targets = []
        
        # Target for cultural markers
        cultural_marker_count = next(
            (f for f in style_vector.linguistic_features if f.feature_name == "cultural_marker_count"),
            None
        )
        if cultural_marker_count:
            targets.append(AuthenticityTarget(
                marker_type="cultural_expressions",
                target_frequency=cultural_marker_count.feature_value / 100.0,  # Normalize
                tolerance=0.2
            ))
        
        # Target for Hinglish terms
        hinglish_count = next(
            (f for f in style_vector.linguistic_features if f.feature_name == "hinglish_term_count"),
            None
        )
        if hinglish_count:
            targets.append(AuthenticityTarget(
                marker_type="hinglish_terms",
                target_frequency=hinglish_count.feature_value / 50.0,  # Normalize
                tolerance=0.3
            ))
        
        return targets
    
    def format_prompt_for_llm(self, enhanced_prompt: EnhancedPrompt) -> str:
        """
        Format the enhanced prompt for LLM consumption
        
        Args:
            enhanced_prompt: The enhanced prompt
            
        Returns:
            Formatted prompt string for LLM
        """
        # Build the system prompt with style context
        system_parts = [
            "You are a culturally aware AI writing assistant that helps Indian professionals communicate authentically.",
            "",
            "# User's Communication Style:",
        ]
        
        # Add linguistic features
        for feature in enhanced_prompt.style_vector.linguistic_features[:5]:  # Top 5 features
            system_parts.append(f"- {feature.feature_name}: {feature.feature_value:.2f}")
        
        system_parts.append("")
        system_parts.append("# Cultural Context:")
        system_parts.append(f"- Primary Language: {enhanced_prompt.style_vector.cultural_context.primary_language}")
        
        if enhanced_prompt.style_vector.cultural_context.regional_influences:
            influences = ", ".join(enhanced_prompt.style_vector.cultural_context.regional_influences[:3])
            system_parts.append(f"- Regional Influences: {influences}")
        
        system_parts.append("")
        system_parts.append("# Instructions:")
        for instruction in enhanced_prompt.contextual_instructions:
            system_parts.append(f"- {instruction}")
        
        system_parts.append("")
        system_parts.append("# Cultural Guidelines:")
        for guideline in enhanced_prompt.cultural_guidelines:
            system_parts.append(f"- {guideline}")
        
        system_parts.append("")
        system_parts.append("# User Request:")
        system_parts.append(enhanced_prompt.original_prompt)
        
        return "\n".join(system_parts)
