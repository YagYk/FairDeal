"""
LLM service for metadata extraction and text generation.
Uses Google Gemini Flash for fast and cost-effective processing.
"""
import json
import time
from typing import Dict, Any, Optional, List
from loguru import logger

from app.config import settings
from app.models.contract_schema import ContractMetadata


class LLMService:
    """
    Service for interacting with Google Gemini Flash LLM.
    
    Design choices:
    1. Gemini Flash: Fast, cost-effective, and high-quality for structured extraction
    2. Structured output: Uses JSON mode for reliable metadata extraction
    3. Error handling: Graceful fallbacks and retries
    4. Type safety: Returns validated Pydantic models
    """
    
    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model
        
        # Initialize Gemini client
        if self.provider == "gemini":
            try:
                import google.generativeai as genai
                if not settings.google_api_key:
                    raise ValueError("GOOGLE_API_KEY not set")
                genai.configure(api_key=settings.google_api_key)
                
                # List available models and find the best one
                try:
                    available_models = genai.list_models()
                    working_models = [
                        m.name for m in available_models
                        if 'generateContent' in m.supported_generation_methods
                        and ('flash' in m.name.lower() or 'pro' in m.name.lower())
                    ]
                    logger.info(f"Found {len(working_models)} available Gemini models")
                except Exception as e:
                    logger.warning(f"Could not list models: {e}")
                    working_models = []
                
                # Try different model names in order of preference
                model_names_to_try = []
                
                # Add user-specified model first (with and without models/ prefix)
                if self.model:
                    model_names_to_try.append(self.model)
                    if not self.model.startswith('models/'):
                        model_names_to_try.append(f'models/{self.model}')
                
                # Add working models from API (prefer latest flash models)
                if working_models:
                    # Sort: prefer 2.5, then 2.0, then others; prefer flash over pro
                    def model_priority(name):
                        priority = 1000
                        if '2.5' in name:
                            priority -= 100
                        elif '2.0' in name:
                            priority -= 50
                        if 'flash' in name.lower():
                            priority -= 10
                        elif 'pro' in name.lower():
                            priority -= 5
                        # Prefer non-exp, non-preview versions
                        if 'exp' in name.lower() or 'preview' in name.lower():
                            priority += 5
                        return priority
                    
                    sorted_models = sorted(working_models, key=model_priority)
                    model_names_to_try.extend(sorted_models)
                
                # Fallback to common names (try both with and without models/ prefix)
                fallback_models = [
                    "gemini-2.5-flash",
                    "models/gemini-2.5-flash",
                    "gemini-2.0-flash",
                    "models/gemini-2.0-flash",
                    "gemini-1.5-flash",
                    "models/gemini-1.5-flash",
                    "gemini-pro",
                    "models/gemini-pro",
                ]
                model_names_to_try.extend(fallback_models)
                
                # Remove duplicates while preserving order
                seen = set()
                model_names_to_try = [m for m in model_names_to_try if not (m in seen or seen.add(m))]
                
                client_initialized = False
                last_error = None
                for model_name in model_names_to_try:
                    try:
                        # Remove 'models/' prefix if present (GenerativeModel expects name without prefix)
                        clean_name = model_name.replace('models/', '')
                        self.client = genai.GenerativeModel(clean_name)
                        self.model = clean_name
                        logger.info(f"Successfully initialized Gemini client with model: {clean_name}")
                        client_initialized = True
                        break
                    except Exception as e:
                        last_error = str(e)
                        logger.debug(f"Failed to initialize model {model_name}: {e}")
                        continue
                
                if not client_initialized:
                    error_msg = f"Could not initialize any Gemini model. Last error: {last_error}"
                    if working_models:
                        error_msg += f"\nAvailable models: {working_models[:5]}"
                    raise ValueError(error_msg)
            except ImportError:
                raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}. Expected 'gemini'")
    
    def extract_contract_metadata(self, contract_text: str) -> ContractMetadata:
        """
        Extract structured metadata from contract text using LLM.
        
        Args:
            contract_text: Full contract text
            
        Returns:
            Validated ContractMetadata object
            
        Raises:
            ValueError: If extraction fails or output is invalid
        """
        logger.info("Extracting contract metadata using LLM")
        
        # Truncate text for faster processing (first 3000 chars is usually enough for metadata)
        truncated_text = contract_text[:3000] if len(contract_text) > 3000 else contract_text
        prompt = self._build_metadata_extraction_prompt(truncated_text)
        
        max_retries = 3
        last_response = None
        for attempt in range(max_retries):
            try:
                response = self._call_llm(prompt, response_format="json_object", max_tokens=2000)
                last_response = response
                
                # Clean and parse JSON response
                if isinstance(response, str):
                    cleaned_response = self._clean_json_response(response)
                    metadata_dict = json.loads(cleaned_response)
                else:
                    metadata_dict = response
                
                # Validate with Pydantic - use model_validate for proper handling
                metadata = ContractMetadata.model_validate(metadata_dict)
                logger.info(f"Successfully extracted metadata: {metadata.contract_type.value if hasattr(metadata.contract_type, 'value') else metadata.contract_type}, {metadata.industry.value if hasattr(metadata.industry, 'value') else metadata.industry}")
                
                return metadata
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info("Retrying with adjusted prompt...")
                    # Add more explicit JSON instruction on retry
                    prompt = prompt + "\n\nCRITICAL: Return ONLY valid, complete JSON. Ensure all strings are properly closed with quotes and escaped. Do not truncate the response."
                    continue
                else:
                    logger.error(f"Failed to parse LLM JSON response after {max_retries} attempts: {e}")
                    if last_response:
                        logger.error(f"Response preview (first 1000 chars): {str(last_response)[:1000]}")
                    raise ValueError(f"Invalid JSON from LLM after {max_retries} attempts: {e}")
            except Exception as e:
                logger.error(f"Metadata extraction failed: {e}")
                if attempt < max_retries - 1:
                    continue
                raise ValueError(f"Metadata extraction failed: {e}")
    
    def _build_metadata_extraction_prompt(self, contract_text: str) -> str:
        """
        Build prompt for metadata extraction.
        """
        # Truncate if too long (already truncated to 3000 in extract_contract_metadata, but keep this as safety)
        truncated_text = contract_text[:3000] if len(contract_text) > 3000 else contract_text
        
        schema_example = ContractMetadata.schema()
        
        prompt = f"""You are a strict legal auditor. Your job is to extract data from a contract with 100% evidential proof.

Contract Text:
{truncated_text}

Rules:
1. For every field, return a JSON object with:
   - "value": The extracted data (or null if not explicitly stated)
   - "confidence": A score 0.0-1.0 (1.0 = explicit match, <0.7 = ambiguous)
   - "source_text": The EXACT substring from the text that proves the value. Copy-paste it.
   - "explanation": Brief reason.

2. **Anti-Hallucination**: If the contract does not explicitly state a value (e.g. Salary), set "value": null. Do NOT infer or guess.
3. **Strictness**: Inferring "Standard Industry Practice" is FORBIDDEN. Only what is written.

Extract the following structure:
{json.dumps(schema_example, indent=2)}

Return ONLY valid JSON.
"""
        return prompt
    
    def generate_analysis_insights(
        self,
        contract_text: str,
        metadata: ContractMetadata,
        percentile_rankings: Dict[str, float],
        similar_contracts: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate analysis insights, red flags, and negotiation scripts.
        
        Args:
            contract_text: Full contract text
            metadata: Extracted contract metadata
            percentile_rankings: Percentile rankings for numeric fields
            similar_contracts: List of similar contracts from RAG
            
        Returns:
            Dictionary with:
            - red_flags: List of red flag descriptions
            - favorable_terms: List of favorable terms
            - negotiation_priorities: List of priority items to negotiate
            - negotiation_scripts: List of negotiation script objects
        """
        logger.info("Generating analysis insights using LLM")
        
        prompt = self._build_insights_prompt(
            contract_text=contract_text,
            metadata=metadata,
            percentile_rankings=percentile_rankings,
            similar_contracts=similar_contracts,
        )
        
        try:
            response = self._call_llm(prompt, response_format="json_object", max_tokens=2000)
            
            if isinstance(response, str):
                insights_dict = json.loads(response)
            else:
                insights_dict = response
            
            # Validate structure
            result = {
                "red_flags": insights_dict.get("red_flags", []),
                "favorable_terms": insights_dict.get("favorable_terms", []),
                "negotiation_priorities": insights_dict.get("negotiation_priorities", []),
                "negotiation_scripts": insights_dict.get("negotiation_scripts", []),
            }
            
            logger.info(f"Generated {len(result['red_flags'])} red flags, {len(result['favorable_terms'])} favorable terms")
            return result
            
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            # Return empty structure on error
            return {
                "red_flags": [],
                "favorable_terms": [],
                "negotiation_priorities": [],
                "negotiation_scripts": [],
            }
    
    def _clean_json_response(self, response_text: str) -> str:
        """
        Clean and fix common JSON issues in LLM responses.
        
        Args:
            response_text: Raw LLM response text
            
        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Find the JSON object boundaries
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
            raise ValueError("No valid JSON object found in response")
        
        # Extract just the JSON part
        json_text = response_text[start_idx:end_idx + 1]
        
        # Try to fix common issues
        # Fix unterminated strings by finding and closing them
        try:
            # First, try to parse as-is
            json.loads(json_text)
            return json_text
        except json.JSONDecodeError as e:
            logger.debug(f"JSON needs cleaning: {e}")
            
            # Try to fix unterminated strings
            # This is a simple heuristic - find unclosed quotes
            lines = json_text.split('\n')
            fixed_lines = []
            in_string = False
            escape_next = False
            
            for line in lines:
                fixed_line = ""
                for char in line:
                    if escape_next:
                        fixed_line += char
                        escape_next = False
                        continue
                    
                    if char == '\\':
                        escape_next = True
                        fixed_line += char
                    elif char == '"' and not escape_next:
                        in_string = not in_string
                        fixed_line += char
                    else:
                        fixed_line += char
                
                # If we're still in a string at end of line, close it
                if in_string and fixed_line.strip() and not fixed_line.rstrip().endswith('"'):
                    fixed_line += '"'
                    in_string = False
                
                fixed_lines.append(fixed_line)
            
            fixed_json = '\n'.join(fixed_lines)
            
            # Try parsing the fixed version
            try:
                json.loads(fixed_json)
                return fixed_json
            except json.JSONDecodeError:
                # If still fails, return original and let it fail with better error
                return json_text
    
    def _build_insights_prompt(
        self,
        contract_text: str,
        metadata: ContractMetadata,
        percentile_rankings: Dict[str, float],
        similar_contracts: List[Dict[str, Any]],
    ) -> str:
        """Build prompt for insight generation."""
        # Truncate contract text for speed (2000 chars is enough for key insights)
        truncated_text = contract_text[:2000] if len(contract_text) > 2000 else contract_text
        
        # Summarize similar contracts
        similar_summary = f"Found {len(similar_contracts)} similar contracts in database."
        if similar_contracts:
            similar_summary += " Top matches include contracts from similar roles and industries."
        
        # Build example JSON format as a separate string to avoid f-string parsing issues
        example_format = """{
  "red_flags": [
    {"issue": "Specific red flag", "explanation": "Detailed explanation"},
    ...
  ],
  "favorable_terms": [
    {"term": "Specific term", "explanation": "Detailed explanation"},
    ...
  ],
  "negotiation_priorities": [
    {"priority": "What to negotiate", "reason": "Why this matters"},
    ...
  ],
  "negotiation_scripts": [
    {"clause": "...", "script": "...", "success_probability": 0.7}
  ]
}"""
        
        prompt = f"""You are an expert contract analyst and negotiation advisor specializing in Indian employment contracts.

Contract Details:
- Type: {metadata.contract_type}
- Industry: {metadata.industry}
- Role: {metadata.role or 'Not specified'}
- Location: {metadata.location}
- Salary: {metadata.salary or 'Not specified'} INR
- Notice Period: {metadata.notice_period_days or 'Not specified'} days
- Non-compete: {'Yes' if metadata.non_compete else 'No'}

Percentile Rankings (compared to similar contracts):
{json.dumps(percentile_rankings, indent=2)}

Contract Text (excerpt):
{truncated_text}

Similar Contracts Context:
{similar_summary}

Analyze this contract and provide DETAILED, SPECIFIC insights with explanations:

1. RED FLAGS: List 3-5 specific red flags with detailed explanations
   Each red flag should have:
   - "issue": A specific description of the red flag
   - "explanation": Detailed explanation of why this is a concern, what it means, and how it compares to market standards

2. FAVORABLE TERMS: List 3-5 favorable terms with detailed explanations
   Each favorable term should have:
   - "term": A specific description of the favorable term
   - "explanation": Detailed explanation of why this is favorable, what it means, and how it compares to market standards

3. NEGOTIATION PRIORITIES: List 3-5 items to prioritize in negotiation with reasons
   Each priority should have:
   - "priority": What to negotiate
   - "reason": Detailed explanation of why this should be prioritized, expected impact, and market context

4. NEGOTIATION SCRIPTS: Provide 2-3 professional negotiation scripts for key issues
   Each script should have:
   - "clause": The clause name
   - "script": Professional negotiation script text
   - "success_probability": A number between 0.0 and 1.0

Focus on:
- Indian legal context and market practices
- Specific, actionable advice
- Professional, non-aggressive language
- Realistic success probabilities (0.0-1.0)

Return ONLY valid JSON in this format:
{example_format}
"""
        return prompt
    
    
    def analyze_contract_comprehensive(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive analysis in a SINGLE LLM call to save rate limits.
        Returns metadata, fairness score, and summary all at once.
        """
        # Truncate text to avoid token limits
        truncated_text = text[:15000] if len(text) > 15000 else text
        
        prompt = f"""
        Analyze this employment contract text and return a JSON object with the following structure:
        {{
            "metadata": {{
                "contract_type": "employment | freelance | internship | other",
                "role": "extracted role title",
                "industry": "extracted industry",
                "salary": 1200000 (numeric yearly value in local currency),
                "location": "extracted location",
                "notice_period_days": 30 (numeric days),
                "non_compete": true/false (boolean),
                "benefits": ["list", "of", "benefits"],
                "termination_clauses": "summary of termination terms"
            }},
            "fairness_score": 75 (integer 0-100),
            "fairness_reasoning": "Brief explanation of the score",
            "summary": "2-3 sentence summary of the contract"
        }}

        SCORING GUIDELINES:
        - 80-100: Excellent, pro-employee, high salary, good benefits
        - 60-79: Fair/Good, standard market terms
        - 40-59: Average/Below Average, some restrictive clauses
        - 0-39: Poor/Exploitative, very low salary or harsh terms

        Contract Text:
        {truncated_text}
        """
        
        try:
            # reduced retries to prevent locking up
            response_text = self._call_llm(prompt, max_tokens=1000, response_format="json_object", max_retries=2)
            
            # Clean up response if needed (remove markdown)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
                
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {e}")
            return {}

    def _call_llm(
        self,
        prompt: str,
        response_format: Optional[str] = None,
        max_tokens: int = 2000,
        max_retries: int = 0,  # CRITICAL: Default to 0 to prevent blocking/hanging. Fail fast.
    ) -> Any:
        """
        Call Gemini Flash with prompt and return response.
        Handles rate limits with robust exponential backoff.
        """
        base_delay = 5  # Start with 5s delay
        
        for attempt in range(max_retries):
            try:
                if self.provider == "gemini":
                    generation_config = {
                        "temperature": 0.1,
                        "max_output_tokens": max_tokens,
                    }
                    
                    if response_format == "json_object":
                        json_instruction = "\n\nCRITICAL: Return ONLY valid, complete JSON. Do not include any markdown formatting, code blocks, or explanatory text. Start directly with { and end with }. Ensure all strings are properly closed with quotes."
                        enhanced_prompt = prompt + json_instruction
                    else:
                        enhanced_prompt = prompt
                    
                    response = self.client.generate_content(
                        enhanced_prompt,
                        generation_config=generation_config
                    )
                    
                    response_text = response.text.strip()
                    
                    if response_format == "json_object":
                        if response_text.startswith("```json"):
                            response_text = response_text[7:]
                        if response_text.startswith("```"):
                            response_text = response_text[3:]
                        if response_text.endswith("```"):
                            response_text = response_text[:-3]
                        response_text = response_text.strip()
                    
                    return response_text
                else:
                    raise ValueError(f"Unsupported provider: {self.provider}")
                    
            except Exception as e:
                error_str = str(e)
                # Check for rate limit errors (429) or overload (503)
                if any(x in error_str for x in ["429", "quota", "rate", "503", "overloaded"]):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # 5, 10, 20, 40, 80
                        
                        # Add jitter
                        import random
                        delay += random.uniform(0, 2)
                        
                        logger.warning(f"Rate limit/Overload hit (Attempt {attempt+1}/{max_retries}). Waiting {delay:.1f}s...")
                        time.sleep(delay)
                        continue
                
                logger.error(f"LLM API call failed: {e}")
                # Don't retry invalid arguments or other permanent errors
                raise ValueError(f"LLM API error: {e}")
        
        raise ValueError(f"LLM API failed after {max_retries} attempts due to rate limits.")

