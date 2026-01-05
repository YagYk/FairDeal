"""
Chatbot service for answering questions about contract analysis results.
Uses LLM to generate contextual responses based on analysis data.
"""
from typing import Dict, Any, Optional
from loguru import logger
from app.services.llm_service import LLMService


class ChatbotService:
    """
    Service for generating chatbot responses about contract analysis.
    
    Uses the analysis results to answer user questions about:
    - Fairness score
    - Red flags
    - Negotiation priorities
    - Percentile rankings
    - Contract terms
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def generate_response(
        self,
        question: str,
        analysis_data: Dict[str, Any],
    ) -> str:
        """
        Generate a chatbot response based on the question and analysis data.
        
        Args:
            question: User's question about the contract analysis
            analysis_data: Complete analysis result dictionary
            
        Returns:
            Chatbot response as string
        """
        logger.info(f"Generating chatbot response for question: {question[:100]}...")
        
        # Build context from analysis data
        context = self._build_context(analysis_data)
        
        # Build prompt for LLM
        prompt = self._build_chatbot_prompt(question, context)
        
        try:
            # Generate response using LLM (no response_format for text output)
            response = self.llm_service._call_llm(
                prompt,
                response_format=None,  # Text response, not JSON
                max_tokens=1000,
            )
            
            if isinstance(response, str):
                return response.strip()
            else:
                # If response is a dict (from JSON mode), extract text
                if isinstance(response, dict):
                    return str(response).strip()
                return str(response).strip()
                
        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return "I apologize, but I'm having trouble processing your question right now. Please try again or rephrase your question."
    
    def _build_context(self, analysis_data: Dict[str, Any]) -> str:
        """
        Build context string from analysis data for the chatbot.
        
        Args:
            analysis_data: Complete analysis result dictionary
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Contract metadata
        metadata = analysis_data.get("contract_metadata", {})
        context_parts.append("=== CONTRACT DETAILS ===")
        context_parts.append(f"Type: {metadata.get('contract_type', 'Unknown')}")
        context_parts.append(f"Industry: {metadata.get('industry', 'Unknown')}")
        context_parts.append(f"Role: {metadata.get('role', 'Not specified')}")
        context_parts.append(f"Location: {metadata.get('location', 'Unknown')}")
        if metadata.get('salary'):
            context_parts.append(f"Salary: ₹{metadata.get('salary'):,}")
        if metadata.get('notice_period_days'):
            context_parts.append(f"Notice Period: {metadata.get('notice_period_days')} days")
        context_parts.append(f"Non-Compete Clause: {'Yes' if metadata.get('non_compete') else 'No'}")
        context_parts.append("")
        
        # Fairness score
        fairness_score = analysis_data.get("fairness_score", 0)
        context_parts.append(f"=== FAIRNESS SCORE ===")
        context_parts.append(f"Overall Score: {fairness_score}%")
        context_parts.append("")
        
        # Percentile rankings
        percentiles = analysis_data.get("percentile_rankings", {})
        context_parts.append("=== MARKET COMPARISON ===")
        if percentiles.get("salary") is not None:
            context_parts.append(f"Salary Percentile: {percentiles.get('salary')}% (higher is better)")
        if percentiles.get("notice_period") is not None:
            context_parts.append(f"Notice Period Percentile: {percentiles.get('notice_period')}% (lower is better)")
        context_parts.append("")
        
        # Red flags
        red_flags = analysis_data.get("red_flags", [])
        if red_flags:
            context_parts.append("=== RED FLAGS ===")
            for i, flag in enumerate(red_flags, 1):
                if isinstance(flag, dict):
                    context_parts.append(f"{i}. {flag.get('issue', flag.get('title', str(flag)))}")
                    if flag.get('explanation'):
                        context_parts.append(f"   Explanation: {flag.get('explanation')}")
                else:
                    context_parts.append(f"{i}. {flag}")
            context_parts.append("")
        
        # Favorable terms
        favorable_terms = analysis_data.get("favorable_terms", [])
        if favorable_terms:
            context_parts.append("=== FAVORABLE TERMS ===")
            for i, term in enumerate(favorable_terms, 1):
                if isinstance(term, dict):
                    context_parts.append(f"{i}. {term.get('term', term.get('title', str(term)))}")
                    if term.get('explanation'):
                        context_parts.append(f"   Explanation: {term.get('explanation')}")
                else:
                    context_parts.append(f"{i}. {term}")
            context_parts.append("")
        
        # Negotiation priorities
        priorities = analysis_data.get("negotiation_priorities", [])
        if priorities:
            context_parts.append("=== NEGOTIATION PRIORITIES ===")
            for i, priority in enumerate(priorities, 1):
                if isinstance(priority, dict):
                    context_parts.append(f"{i}. {priority.get('priority', priority.get('title', str(priority)))}")
                    if priority.get('reason'):
                        context_parts.append(f"   Reason: {priority.get('reason')}")
                else:
                    context_parts.append(f"{i}. {priority}")
            context_parts.append("")
        
        # Negotiation scripts
        scripts = analysis_data.get("negotiation_scripts", [])
        if scripts:
            context_parts.append("=== NEGOTIATION SCRIPTS ===")
            for i, script in enumerate(scripts, 1):
                if isinstance(script, dict):
                    context_parts.append(f"{i}. {script.get('topic', script.get('title', f'Script {i}'))}")
                    if script.get('script'):
                        context_parts.append(f"   Script: {script.get('script')}")
                else:
                    context_parts.append(f"{i}. {script}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_chatbot_prompt(self, question: str, context: str) -> str:
        """
        Build the prompt for the chatbot LLM call.
        
        Args:
            question: User's question
            context: Formatted analysis context
            
        Returns:
            Complete prompt string
        """
        prompt = f"""You are a helpful AI assistant specialized in contract analysis. You help users understand their contract analysis results.

Your role is to:
- Answer questions about the contract analysis clearly and accurately
- Explain fairness scores, percentiles, and rankings in simple terms
- Help users understand red flags and favorable terms
- Provide guidance on negotiation priorities
- Be professional, friendly, and supportive

CONTRACT ANALYSIS DATA:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer the user's question based ONLY on the analysis data provided above
2. If the question asks about something not in the data, politely say you don't have that information
3. Use specific numbers and percentages from the analysis when relevant
4. Explain technical terms (like percentiles) in simple language
5. Be concise but thorough
6. If asked about negotiation, reference the negotiation priorities and scripts provided
7. If asked about fairness, explain the score and what factors contributed to it

Generate a helpful, accurate response:"""
        
        return prompt

