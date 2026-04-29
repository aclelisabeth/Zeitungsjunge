"""AI-powered article summarization service."""

import os
from typing import Optional
import asyncio
from openai import OpenAI, APIError
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SummarizationService:
    """Service for AI-powered article summarization."""

    def __init__(self):
        """Initialize the summarization service."""
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 150

    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        return self.client is not None and OPENAI_API_KEY is not None

    def summarize(
        self,
        title: str,
        description: Optional[str] = None,
        content: Optional[str] = None
    ) -> Optional[str]:
        """Summarize article using OpenAI."""
        if not self.is_available():
            logger.warning("OpenAI API key not configured")
            return None

        try:
            # Prepare text to summarize
            text_to_summarize = f"Title: {title}\n"
            if description:
                text_to_summarize += f"Description: {description}\n"
            if content:
                text_to_summarize += f"Content: {content[:500]}"  # Limit to 500 chars

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional news summarizer. Provide concise, factual summaries in 2-3 sentences."
                    },
                    {
                        "role": "user",
                        "content": f"Summarize this news article:\n\n{text_to_summarize}"
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.5
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"Successfully summarized article: {title[:50]}...")
            return summary

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return None

    async def summarize_async(
        self,
        title: str,
        description: Optional[str] = None,
        content: Optional[str] = None
    ) -> Optional[str]:
        """Async wrapper for summarization."""
        return await asyncio.to_thread(
            self.summarize,
            title,
            description,
            content
        )

    def batch_summarize(
        self,
        articles: list
    ) -> list:
        """Summarize multiple articles."""
        results = []
        for article in articles:
            summary = self.summarize(
                article.get("title"),
                article.get("description"),
                article.get("content")
            )
            results.append({
                "article_id": article.get("id"),
                "summary": summary
            })
        return results


# Global summarization service instance
summarization_service = SummarizationService()
