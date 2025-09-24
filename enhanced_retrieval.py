import asyncio
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from forecasting_tools import (
    AskNewsSearcher,
    SmartSearcher,
    GeneralLlm,
    clean_indents,
    structure_output,
)
from forecasting_tools.helpers.metaculus_api import MetaculusQuestion

logger = logging.getLogger(__name__)


class EnhancedRetrievalSystem:
    """
    Enhanced retrieval system implementing query expansion and sub-question decomposition
    as described in the "Approaching Human-Level Forecasting with Language Models" paper.
    """
    
    def __init__(self, llm: GeneralLlm):
        self.llm = llm
    
    async def generate_search_queries(self, question: MetaculusQuestion) -> List[str]:
        """
        Generate multiple search queries using query expansion techniques.
        """
        # Method 1: Direct query expansion
        direct_prompt = clean_indents(f"""
            I will provide you with a forecasting question and the background information for the question.
            Question: {question.question_text}
            Background: {question.background_info}
            
            Task:
            - Generate brief search queries (up to 10 words each) to gather information on Google that could influence the forecast.
            - You must generate exactly 3 queries
            
            Your response should take the following structure:
            Thoughts:
            {{ Insert your thinking here. }}
            
            Search Queries:
            {{ Insert the queries here. Use semicolons to separate the queries. }}
        """)
        
        # Method 2: Sub-question decomposition
        decomposition_prompt = clean_indents(f"""
            I will provide you with a forecasting question and the background information for the question. 
            I will then ask you to generate short search queries (up to 10 words each) that I'll use to find articles on Google News to help answer the question.
            
            Question: {question.question_text}
            Background: {question.background_info}
            
            You must generate exactly 3 queries
            
            Start off by writing down sub-questions. Then use your sub-questions to help steer the search queries you produce.
            
            Your response should take the following structure:
            Thoughts:
            {{ Insert your thinking here. }}
            
            Search Queries:
            {{ Insert the queries here. Use semicolons to separate the queries. }}
        """)
        
        # Get queries from both methods
        direct_response = await self.llm.invoke(direct_prompt)
        decomposition_response = await self.llm.invoke(decomposition_prompt)
        
        # Extract queries from responses
        direct_queries = self._extract_queries_from_response(direct_response)
        decomposition_queries = self._extract_queries_from_response(decomposition_response)
        
        # Combine and deduplicate queries
        all_queries = list(set(direct_queries + decomposition_queries))
        return all_queries
    
    def _extract_queries_from_response(self, response: str) -> List[str]:
        """
        Extract search queries from LLM response.
        """
        try:
            # Look for the "Search Queries:" line
            if "Search Queries:" in response:
                queries_part = response.split("Search Queries:")[1].strip()
                # Split by semicolons and clean up
                queries = [q.strip().strip('"\'') for q in queries_part.split(";")]
                return [q for q in queries if q]  # Remove empty queries
            else:
                # Fallback: try to extract any line that looks like queries
                lines = response.split("\n")
                for line in lines:
                    if ";" in line and len(line.split(";")) >= 2:
                        queries = [q.strip().strip('"\'') for q in line.split(";")]
                        return [q for q in queries if q]
                # Last resort: return the whole response as one query
                return [response.strip()]
        except Exception as e:
            logger.warning(f"Error extracting queries: {e}. Returning original response.")
            return [response.strip()]
    
    async def retrieve_articles(self, queries: List[str], max_articles_per_query: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve articles using multiple search APIs with fallback options.
        """
        all_articles = []

        # Try to use AskNewsSearcher (may fail due to API key issues)
        asknews_available = False
        try:
            asknews_searcher = AskNewsSearcher()
            # Test with a simple query first
            test_result = await asknews_searcher.get_formatted_news_async("test")
            if "error" not in test_result.lower() and "unauthorized" not in test_result.lower():
                asknews_available = True
                logger.info("AskNews API is available")
            else:
                logger.warning("AskNews API returned error response, will use fallback")
        except Exception as e:
            logger.warning(f"AskNews API not available: {e}")

        # Use SmartSearcher (more reliable) - but only if EXA API key is available
        smart_searcher = None
        exa_key = os.getenv('EXA_API_KEY', '')
        if exa_key and exa_key != '1234567890':  # Check if it's a real API key
            try:
                smart_searcher = SmartSearcher(
                    model="openrouter/openai/gpt-4o-mini",
                    temperature=0,
                    num_searches_to_run=1,  # Reduced for faster testing
                    num_sites_per_search=max_articles_per_query,
                    use_advanced_filters=False,
                )
                logger.info("SmartSearcher initialized successfully")
            except Exception as e:
                logger.warning(f"SmartSearcher not available: {e}")
        else:
            logger.info("EXA API key not available, skipping SmartSearcher")

        # Retrieve from available sources
        for query in queries[:2]:  # Limit to top 2 queries for faster testing
            try:
                # Get articles from AskNews if available
                if asknews_available:
                    try:
                        asknews_articles = await asknews_searcher.get_formatted_news_async(query)
                        parsed_asknews = self._parse_asknews_response(asknews_articles)
                        all_articles.extend(parsed_asknews)
                        logger.info(f"Got {len(parsed_asknews)} articles from AskNews for query: {query}")
                    except Exception as e:
                        logger.warning(f"Error retrieving from AskNews for query '{query}': {e}")

                # Get articles from SmartSearcher if available
                if smart_searcher:
                    try:
                        smart_prompt = f"Find recent news articles about: {query}"
                        smart_articles = await smart_searcher.invoke(smart_prompt)
                        parsed_smart = self._parse_smart_response(smart_articles)
                        all_articles.extend(parsed_smart)
                        logger.info(f"Got {len(parsed_smart)} articles from SmartSearcher for query: {query}")
                    except Exception as e:
                        logger.warning(f"Error retrieving from SmartSearcher for query '{query}': {e}")

            except Exception as e:
                logger.warning(f"Error processing query '{query}': {e}")

        # If no articles retrieved, create fallback content based on the queries
        if not all_articles:
            logger.info("No articles retrieved, creating fallback research content")
            fallback_content = []
            for query in queries[:3]:
                fallback_content.append({
                    'title': f'Research Topic: {query}',
                    'summary': f'Query-based research on: {query}. No specific articles found, but this topic is relevant to the forecasting question.',
                    'source': 'Query Analysis',
                    'url': '',
                    'publish_date': datetime.now().strftime('%Y-%m-%d'),
                    'relevance_score': 4
                })
            return fallback_content

        # Deduplicate articles by URL
        unique_articles = {}
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in unique_articles:
                unique_articles[url] = article
            elif not url:  # Keep articles without URLs (fallback content)
                unique_articles[f"article_{len(unique_articles)}"] = article

        result = list(unique_articles.values())
        logger.info(f"Total unique articles retrieved: {len(result)}")
        return result
    
    def _parse_asknews_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse AskNews response into structured articles.
        """
        # Simple parsing - in practice, you'd want more sophisticated parsing
        articles = []
        lines = response.split('\n')
        current_article = {}
        
        for line in lines:
            if line.startswith('**') and line.endswith('**'):
                if current_article:
                    articles.append(current_article)
                    current_article = {}
                current_article['title'] = line.strip('*')
            elif line.startswith('Original language:'):
                current_article['language'] = line.replace('Original language:', '').strip()
            elif line.startswith('Publish date:'):
                current_article['publish_date'] = line.replace('Publish date:', '').strip()
            elif line.startswith('Source:['):
                # Extract URL from markdown link
                import re
                match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
                if match:
                    current_article['source'] = match.group(1)
                    current_article['url'] = match.group(2)
            elif line.strip() and 'title' in current_article and 'summary' not in current_article:
                current_article['summary'] = line.strip()
        
        if current_article:
            articles.append(current_article)
            
        return articles
    
    def _parse_smart_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse SmartSearcher response into structured articles.
        """
        # Simple parsing - in practice, you'd want more sophisticated parsing
        articles = []
        # For now, we'll treat the entire response as one article
        articles.append({
            'title': 'Retrieved Information',
            'summary': response,
            'source': 'SmartSearcher',
            'url': '',
            'publish_date': datetime.now().strftime('%Y-%m-%d')
        })
        return articles
    
    async def rate_article_relevance(self, articles: List[Dict[str, Any]], question: MetaculusQuestion) -> List[Dict[str, Any]]:
        """
        Rate the relevance of articles to the forecasting question.
        """
        rated_articles = []
        
        for article in articles:
            prompt = clean_indents(f"""
                Please consider the following forecasting question and its background information.
                After that, I will give you a news article and ask you to rate its relevance with respect to the forecasting question.
                
                Question:
                {question.question_text}
                
                Question Background: {question.background_info}
                Resolution Criteria: {question.resolution_criteria}
                
                Article:
                {article.get('title', '')}
                {article.get('summary', '')}
                
                Please rate the relevance of the article to the question, at the scale of 1-6
                1 – irrelevant
                2 – slightly relevant
                3 – somewhat relevant
                4 – relevant
                5 – highly relevant
                6 – most relevant
                
                Guidelines:
                - You don't need to access any external sources. Just consider the information provided.
                - Focus on the content of the article, not the title.
                - If the text content is an error message about JavaScript, paywall, cookies or other technical issues, output a score of 1.
                
                Your response should look like the following:
                Thought: {{ Insert your thinking }}
                Rating: {{ Insert answer here }}
            """)
            
            try:
                response = await self.llm.invoke(prompt)
                rating = self._extract_rating_from_response(response)
                article['relevance_score'] = rating
                rated_articles.append(article)
            except Exception as e:
                logger.warning(f"Error rating article relevance: {e}")
                article['relevance_score'] = 3  # Default medium relevance
                rated_articles.append(article)
        
        # Sort by relevance score (descending)
        rated_articles.sort(key=lambda x: x['relevance_score'], reverse=True)
        return rated_articles
    
    def _extract_rating_from_response(self, response: str) -> int:
        """
        Extract numerical rating from LLM response.
        """
        try:
            # Look for "Rating:" followed by a number
            import re
            match = re.search(r'Rating:\s*(\d+)', response)
            if match:
                rating = int(match.group(1))
                return max(1, min(6, rating))  # Clamp between 1-6
            else:
                # Fallback: look for any number in the response
                numbers = re.findall(r'\d+', response)
                if numbers:
                    rating = int(numbers[0])
                    return max(1, min(6, rating))
                else:
                    return 3  # Default medium relevance
        except Exception as e:
            logger.warning(f"Error extracting rating: {e}. Returning default rating.")
            return 3
    
    async def summarize_articles(self, articles: List[Dict[str, Any]], question: MetaculusQuestion, max_articles: int = 15) -> str:
        """
        Summarize the most relevant articles.
        """
        # Filter out low relevance articles (score < 4)
        filtered_articles = [a for a in articles if a.get('relevance_score', 3) >= 4]
        
        # Take top N articles
        top_articles = filtered_articles[:max_articles]
        
        # Create summary prompt
        articles_text = "\n\n".join([
            f"Article {i+1}:\nTitle: {article.get('title', 'N/A')}\nSummary: {article.get('summary', 'N/A')}"
            for i, article in enumerate(top_articles)
        ])
        
        prompt = clean_indents(f"""
            I want to make the following articles shorter (condense them to no more than 200 words total).
            
            Articles:
            {articles_text}
            
            When doing this task for me, please do not remove any details that would be helpful for making considerations about the following forecasting question. 
            
            Forecasting Question: {question.question_text}
            Question Background: {question.background_info}
            
            Please provide a concise summary that preserves all relevant information for forecasting.
        """)
        
        try:
            summary = await self.llm.invoke(prompt)
            return summary
        except Exception as e:
            logger.warning(f"Error summarizing articles: {e}")
            # Fallback: return concatenated summaries
            fallback_summary = "\n\n".join([
                f"{article.get('title', 'N/A')}: {article.get('summary', 'N/A')}"
                for article in top_articles
            ])
            return fallback_summary[:1000]  # Limit length
    
    async def enhanced_retrieve(self, question: MetaculusQuestion) -> str:
        """
        Complete enhanced retrieval pipeline.
        """
        logger.info(f"Starting enhanced retrieval for question: {question.question_text}")
        
        # Step 1: Generate search queries
        queries = await self.generate_search_queries(question)
        logger.info(f"Generated {len(queries)} search queries")
        
        # Step 2: Retrieve articles
        articles = await self.retrieve_articles(queries)
        logger.info(f"Retrieved {len(articles)} articles")
        
        # Step 3: Rate relevance
        rated_articles = await self.rate_article_relevance(articles, question)
        logger.info("Rated article relevance")
        
        # Step 4: Summarize
        summary = await self.summarize_articles(rated_articles, question)
        logger.info("Generated article summary")
        
        return summary


# Example usage
async def main():
    # This would be called from your main bot
    pass


if __name__ == "__main__":
    asyncio.run(main())