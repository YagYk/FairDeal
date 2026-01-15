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
        
        IMPORTANT:
        - To avoid LLM rate limiting and quota issues, the chatbot now uses
          deterministic, rule-based responses only.
        - This still uses the full analysis data (fairness score, red flags,
          market data, negotiation priorities) to answer questions.
        
        Args:
            question: User's question about the contract analysis
            analysis_data: Complete analysis result dictionary
            
        Returns:
            Chatbot response as string
        """
        logger.info(f"Generating chatbot response (rule-based) for question: {question[:100]}...")
        
        # Directly use rule-based engine to avoid LLM and rate limits
        try:
            return self._generate_fallback_response(question, analysis_data)
        except Exception as e:
            logger.error(f"Rule-based chatbot failed: {e}")
            return "I had trouble generating a detailed answer, but your analysis dashboard (Fairness Score, Red Flags, Market Data, Negotiation) has the latest results."
            
    def _generate_fallback_response(self, question: str, analysis_data: Dict[str, Any]) -> str:
        """
        Generate a rule-based response when LLM is unavailable.
        Uses keyword matching to find relevant analysis sections.
        """
        q_lower = question.lower()
        
        # 1. Fairness Score / Overall Assessment
        if any(w in q_lower for w in ["score", "fair", "rating", "assessment", "good", "bad"]):
            score = analysis_data.get("fairness_score", 0)
            rating = "Excellent" if score >= 80 else "Good" if score >= 65 else "Average" if score >= 50 else "Poor"
            return f"Based on my analysis, this contract has a Fairness Score of **{score}/100** ({rating}). This score is calculated based on salary competitiveness (%s percentile), notice period, and the presence of red flags." % (
                analysis_data.get("percentile_rankings", {}).get("salary", "unknown")
            )

        # 2. Salary / Pay / Compensation
        if any(w in q_lower for w in ["salary", "pay", "compensation", "money", "ctc"]):
            meta = analysis_data.get("contract_metadata", {})
            salary = meta.get("salary")
            try:
                # Try to format if it's a number
                if isinstance(salary, (int, float)):
                    salary_str = f"₹{salary:,}"
                elif isinstance(salary, str) and salary.isdigit():
                    salary_str = f"₹{int(salary):,}"
                else:
                    salary_str = str(salary) if salary else "not specified"
            except:
                salary_str = str(salary) if salary else "not specified"
                
            percentile = analysis_data.get("percentile_rankings", {}).get("salary", "unknown")
            return f"The extracted salary is **{salary_str}** per year. In the current market context, this places you in the **{percentile}th percentile**. Ensuring your compensation aligns with industry standards is critical."
            
        # 3. Notice Period
        if any(w in q_lower for w in ["notice", "resign", "leaving", "period"]):
            meta = analysis_data.get("contract_metadata", {})
            days = meta.get("notice_period_days") or "standard"
            percentile = analysis_data.get("percentile_rankings", {}).get("notice_period", "neutral")
            return f"The notice period is **{days} days**. Compared to similar contracts, this is in the **{percentile}th percentile**. A standard notice period is typically 30-60 days."

        # 4. Red Flags / Risks / Issues
        if any(w in q_lower for w in ["red flag", "risk", "issue", "problem", "warn", "bad"]):
            flags = analysis_data.get("red_flags", [])
            if not flags:
                return "I found no major red flags in this contract. It appears to be relatively standard."
            
            flag_text = "\n".join([f"- {f.get('issue', f) if isinstance(f, dict) else f}" for f in flags[:3]])
            return f"I identified **{len(flags)} potential red flags** that you should review:\n\n{flag_text}\n\nI recommend clarifying these clauses before signing."

        # 5. Negotiation / Improvement
        if any(w in q_lower for w in ["negotiate", "improve", "better", "ask", "change"]):
            priorities = analysis_data.get("negotiation_priorities", [])
            if not priorities:
                return "Based on the score, the terms seem reasonable, but you can always negotiate salary or benefits."

            priority_text = "\n".join([f"- {p.get('priority', p) if isinstance(p, dict) else p}" for p in priorities[:3]])
            return f"Here are the top areas you might want to negotiate:\n\n{priority_text}\n\nCheck the 'Negotiation' tab for specific scripts you can use."

        # Fallback context-aware generic response
        return (
            "I couldn't match your question to a specific part of the analysis, "
            "but your contract has already been analyzed. Try asking about:\n"
            "- fairness score\n- salary / compensation\n- notice period\n- red flags or risks\n- what to negotiate"
        )
    
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

