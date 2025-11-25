"""
Oracle Service - Generates context-aware reflection questions for Debrief.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class OracleService:
    """AI Oracle for generating reflection questions."""
    
    def __init__(self, llm_wrapper=None):
        """
        Initialize Oracle with LLM wrapper.
        
        Args:
            llm_wrapper: The Mirix AgentWrapper instance for LLM calls
        """
        self.llm = llm_wrapper
    
    async def generate_reflection_question(
        self,
        task_title: str,
        duration_minutes: int,
        project_why: Optional[str] = None,
        project_what: Optional[str] = None
    ) -> str:
        """
        Generate a context-aware reflection question.
        
        Args:
            task_title: The task that was completed
            duration_minutes: How long the session lasted
            project_why: The purpose of the project
            project_what: The goal of the project
        
        Returns:
            A specific reflection question (max 25 words)
        """
        if not self.llm:
            return self._get_fallback_question(task_title, duration_minutes)
        
        try:
            prompt = self._build_prompt(task_title, duration_minutes, project_why, project_what)
            
            # Use the LLM wrapper's chat method
            response = await self.llm.chat(
                message=prompt,
                system_prompt="You are the Oracle, a wise AI guide for reflection. Generate ONE specific, actionable question (max 25 words).",
                max_tokens=60,
                temperature=0.7
            )
            
            question = response.strip()
            
            # Validate question quality
            if len(question) < 10 or len(question.split()) > 30:
                logger.warning(f"Generated question quality issue: {question}")
                return self._get_fallback_question(task_title, duration_minutes)
            
            return question
            
        except Exception as e:
            logger.error(f"Failed to generate reflection question: {e}")
            return self._get_fallback_question(task_title, duration_minutes)
    
    def _build_prompt(self, task_title, duration_minutes, project_why, project_what):
        """Build the LLM prompt for question generation."""
        context_parts = [f"Task completed: {task_title}"]
        
        if duration_minutes:
            if duration_minutes < 15:
                context_parts.append(f"Duration: {duration_minutes} min (quick)")
            elif duration_minutes > 60:
                context_parts.append(f"Duration: {duration_minutes} min (extended)")
            else:
                context_parts.append(f"Duration: {duration_minutes} min")
        
        if project_why:
            context_parts.append(f"Project purpose: {project_why[:100]}")
        
        if project_what:
            context_parts.append(f"Project goal: {project_what[:100]}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""Context:
{context}

Generate ONE specific reflection question that helps identify:
- What went well or poorly
- A key learning or insight
- How to improve next time

Question (max 25 words):"""
        
        return prompt
    
    def _get_fallback_question(self, task_title: str, duration_minutes: int) -> str:
        """Return a context-aware fallback question if LLM fails."""
        if duration_minutes and duration_minutes > 60:
            return f"This task took {duration_minutes} minutes. What caused it to take longer than expected?"
        elif "bug" in task_title.lower() or "fix" in task_title.lower():
            return "What was the root cause of this issue, and how can you prevent it next time?"
        elif "implement" in task_title.lower() or "create" in task_title.lower():
            return "What was the most challenging part of this implementation, and what did you learn?"
        else:
            return "What was the most valuable insight from this task, and how will you apply it?"


# Singleton instance
_oracle_service = None


def get_oracle_service(llm_wrapper=None):
    """Get or create the Oracle service singleton."""
    global _oracle_service
    if _oracle_service is None:
        _oracle_service = OracleService(llm_wrapper)
    return _oracle_service
