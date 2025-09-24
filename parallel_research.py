import asyncio
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import time

from forecasting_tools import (
    AskNewsSearcher,
    SmartSearcher,
    GeneralLlm,
    clean_indents,
    structure_output,
)
from forecasting_tools.helpers.metaculus_api import MetaculusQuestion

logger = logging.getLogger(__name__)


class MultiSearcher:
    """
    Parallel research system that queries multiple search sources concurrently.
    Based on the architecture of the top-performing forecasting bot.
    """

    def __init__(self, llm: GeneralLlm, max_workers: int = 5):
        self.llm = llm
        self.max_workers = max_workers
        self.searchers = self._initialize_searchers()

    def _initialize_searchers(self) -> List[Dict[str, Any]]:
        """
        Initialize available searchers with their configurations.
        """
        searchers = []

        # AskNews Searcher
        try:
            asknews_searcher = AskNewsSearcher()
            searchers.append({
                'name': 'AskNews',
                'searcher': asknews_searcher,
                'type': 'asknews',
                'enabled': True
            })
            logger.info("AskNews searcher initialized")
        except Exception as e:
            logger.warning(f"AskNews searcher failed to initialize: {e}")
            searchers.append({
                'name': 'AskNews',
                'searcher': None,
                'type': 'asknews',
                'enabled': False
            })

        # SmartSearcher (Exa-based)
        exa_key = os.getenv('EXA_API_KEY', '')
        if exa_key and exa_key != '1234567890':
            try:
                smart_searcher = SmartSearcher(
                    model="openrouter/openai/gpt-4o-mini",
                    temperature=0,
                    num_searches_to_run=2,
                    num_sites_per_search=5,
                    use_advanced_filters=False,
                )
                searchers.append({
                    'name': 'SmartSearcher',
                    'searcher': smart_searcher,
                    'type': 'smart',
                    'enabled': True
                })
                logger.info("SmartSearcher initialized")
            except Exception as e:
                logger.warning(f"SmartSearcher failed to initialize: {e}")
                searchers.append({
                    'name': 'SmartSearcher',
                    'searcher': None,
                    'type': 'smart',
                    'enabled': False
                })
        else:
            logger.info("EXA API key not available, skipping SmartSearcher")
            searchers.append({
                'name': 'SmartSearcher',
                'searcher': None,
                'type': 'smart',
                'enabled': False
            })

        return searchers

    async def generate_search_queries(self, question: MetaculusQuestion) -> List[str]:
        """
        Generate multiple targeted search queries using different strategies.
        """
        logger.info("Generating search queries...")

        # Strategy 1: Direct question analysis
        direct_prompt = clean_indents(f"""
            I need to generate search queries to research this forecasting question.

            Question: {question.question_text}
            Background: {question.background_info}

            Generate 3 targeted search queries (under 10 words each) that would help find relevant information.
            Focus on different aspects of the question.

            Your response should be exactly 3 queries separated by semicolons.
        """)

        # Strategy 2: Decomposition-based queries
        decomposition_prompt = clean_indents(f"""
            Break down this forecasting question into sub-questions, then generate search queries.

            Question: {question.question_text}
            Background: {question.background_info}

            First, identify 2-3 key sub-questions that need to be answered.
            Then, generate 1 search query for each sub-question.

            Your response should be exactly 3 queries separated by semicolons.
        """)

        # Strategy 3: Timeline and trends
        timeline_prompt = clean_indents(f"""
            Generate search queries focused on recent trends and developments related to this question.

            Question: {question.question_text}
            Background: {question.background_info}

            Generate 3 queries focused on current trends, recent developments, and expert opinions.

            Your response should be exactly 3 queries separated by semicolons.
        """)

        try:
            # Run query generation in parallel
            tasks = [
                self.llm.invoke(direct_prompt),
                self.llm.invoke(decomposition_prompt),
                self.llm.invoke(timeline_prompt)
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Extract queries from responses
            all_queries = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.warning(f"Query generation strategy {i} failed: {response}")
                    continue

                queries = self._extract_queries_from_response(response)
                all_queries.extend(queries)

            # Remove duplicates and limit to top queries
            unique_queries = list(dict.fromkeys(all_queries))  # Preserve order
            final_queries = unique_queries[:6]  # Limit to 6 queries max

            logger.info(f"Generated {len(final_queries)} unique search queries")
            return final_queries

        except Exception as e:
            logger.error(f"Error generating search queries: {e}")
            # Fallback to basic queries
            return [question.question_text[:50] + "..."]

    def _extract_queries_from_response(self, response: str) -> List[str]:
        """
        Extract search queries from LLM response.
        """
        try:
            # Split by semicolons and clean up
            queries = [q.strip().strip('"\'') for q in response.split(';') if q.strip()]
            return [q for q in queries if len(q) > 3]  # Filter out very short queries
        except Exception as e:
            logger.warning(f"Error extracting queries: {e}")
            return [response.strip()[:100]]  # Fallback to truncated response

    async def search_with_all_sources(self, query: str, max_results_per_source: int = 3) -> List[Dict[str, Any]]:
        """
        Execute search query across all available sources in parallel.
        """
        logger.info(f"Searching for: {query}")

        tasks = []
        for searcher_config in self.searchers:
            if searcher_config['enabled']:
                task = self._search_with_source(searcher_config, query, max_results_per_source)
                tasks.append(task)

        if not tasks:
            logger.warning("No search sources available")
            return []

        # Execute searches in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Collect successful results
        all_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Search source {i} failed: {result}")
                continue

            # Add source information to each result
            for item in result:
                item['search_source'] = self.searchers[i]['name']
                item['search_query'] = query
            all_results.extend(result)

        logger.info(f"Found {len(all_results)} results for query: {query}")
        return all_results

    async def _search_with_source(self, searcher_config: Dict[str, Any], query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Execute search with a specific source.
        """
        searcher = searcher_config['searcher']
        source_type = searcher_config['type']

        try:
            if source_type == 'asknews':
                response = await searcher.get_formatted_news_async(query)
                return self._parse_asknews_response(response)

            elif source_type == 'smart':
                prompt = f"Find recent news and information about: {query}"
                response = await searcher.invoke(prompt)
                return self._parse_smart_response(response)

            else:
                logger.warning(f"Unknown searcher type: {source_type}")
                return []

        except Exception as e:
            logger.error(f"Error searching with {searcher_config['name']}: {e}")
            return []

    def _parse_asknews_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse AskNews response into structured articles.
        """
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
        # Split response into individual articles if possible
        articles = []

        # Try to split by common separators
        if '\n\n' in response:
            sections = response.split('\n\n')
        else:
            sections = [response]

        for i, section in enumerate(sections):
            if section.strip():
                article = {
                    'title': f'Search Result {i+1}',
                    'summary': section.strip(),
                    'source': 'SmartSearcher',
                    'url': '',
                    'publish_date': datetime.now().strftime('%Y-%m-%d')
                }
                articles.append(article)

        return articles

    async def comprehensive_search(self, question: MetaculusQuestion, max_queries: int = 4, max_results_per_query: int = 3) -> List[Dict[str, Any]]:
        """
        Execute comprehensive search with query generation and parallel execution.
        """
        logger.info(f"Starting comprehensive search for question: {question.question_text}")

        # Step 1: Generate search queries
        queries = await self.generate_search_queries(question)

        # Step 2: Execute searches in parallel
        search_tasks = []
        for query in queries[:max_queries]:
            task = self.search_with_all_sources(query, max_results_per_source)
            search_tasks.append(task)

        all_results = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Step 3: Collect and deduplicate results
        collected_results = []
        for result in all_results:
            if isinstance(result, Exception):
                logger.warning(f"Search query failed: {result}")
                continue
            collected_results.extend(result)

        # Deduplicate by URL or title
        unique_results = []
        seen_urls = set()
        seen_titles = set()

        for result in collected_results:
            url = result.get('url', '')
            title = result.get('title', '')

            if url and url in seen_urls:
                continue
            if title and title.lower() in seen_titles:
                continue

            unique_results.append(result)
            seen_urls.add(url)
            seen_titles.add(title.lower())

        logger.info(f"Comprehensive search completed. Found {len(unique_results)} unique results")
        return unique_results

    async def rate_relevance(self, articles: List[Dict[str, Any]], question: MetaculusQuestion) -> List[Dict[str, Any]]:
        """
        Rate the relevance of articles to the forecasting question.
        """
        logger.info("Rating article relevance...")

        rated_articles = []

        for article in articles:
            prompt = clean_indents(f"""
                Rate the relevance of this article to the forecasting question.

                Question: {question.question_text}
                Background: {question.background_info}

                Article Title: {article.get('title', 'N/A')}
                Article Summary: {article.get('summary', 'N/A')}

                Rate relevance on a scale of 1-6:
                1 = Irrelevant
                2 = Slightly relevant
                3 = Somewhat relevant
                4 = Relevant
                5 = Highly relevant
                6 = Most relevant

                If the content appears to be an error message or technical issue, rate it 1.

                Respond with just the number.
            """)

            try:
                response = await self.llm.invoke(prompt)
                rating = self._extract_rating(response)
                article['relevance_score'] = rating
                rated_articles.append(article)
            except Exception as e:
                logger.warning(f"Error rating article: {e}")
                article['relevance_score'] = 3  # Default medium relevance
                rated_articles.append(article)

        # Sort by relevance score
        rated_articles.sort(key=lambda x: x['relevance_score'], reverse=True)

        logger.info(f"Relevance rating completed. Top score: {rated_articles[0]['relevance_score'] if rated_articles else 'N/A'}")
        return rated_articles

    def _extract_rating(self, response: str) -> int:
        """
        Extract numerical rating from LLM response.
        """
        try:
            import re
            # Look for a number between 1-6
            numbers = re.findall(r'\b([1-6])\b', response)
            if numbers:
                return int(numbers[0])
            else:
                return 3  # Default
        except Exception as e:
            logger.warning(f"Error extracting rating: {e}")
            return 3

    async def summarize_research(self, articles: List[Dict[str, Any]], question: MetaculusQuestion, max_articles: int = 10) -> str:
        """
        Summarize the most relevant research findings.
        """
        logger.info("Summarizing research findings...")

        # Filter for relevant articles (score >= 4)
        relevant_articles = [a for a in articles if a.get('relevance_score', 3) >= 4]

        if not relevant_articles:
            logger.warning("No highly relevant articles found for summarization")
            return "No relevant research findings were identified."

        # Take top articles
        top_articles = relevant_articles[:max_articles]

        # Create summary prompt
        articles_text = "\n\n".join([
            f"Article {i+1} (Score: {article.get('relevance_score', 3)}):\n"
            f"Title: {article.get('title', 'N/A')}\n"
            f"Source: {article.get('search_source', 'N/A')}\n"
            f"Summary: {article.get('summary', 'N/A')}"
            for i, article in enumerate(top_articles)
        ])

        prompt = clean_indents(f"""
            Summarize the key research findings that are most relevant to this forecasting question.

            Question: {question.question_text}
            Background: {question.background_info}

            Research Articles:
            {articles_text}

            Provide a concise summary (under 300 words) that highlights:
            1. Key facts and data points
            2. Expert opinions or trends
            3. Any conflicting information
            4. Most relevant considerations for forecasting

            Focus only on information that would help make an accurate forecast.
        """)

        try:
            summary = await self.llm.invoke(prompt)
            logger.info(f"Research summary completed ({len(summary)} characters)")
            return summary
        except Exception as e:
            logger.error(f"Error summarizing research: {e}")
            # Fallback: concatenate top article summaries
            fallback = "\n\n".join([
                f"{a.get('title', 'N/A')}: {a.get('summary', 'N/A')[:200]}..."
                for a in top_articles[:3]
            ])
            return fallback


# Example usage and testing
async def test_multi_searcher():
    """
    Test function to demonstrate the MultiSearcher capabilities.
    """
    from forecasting_tools.ai_models import GeneralLlm

    # Initialize LLM
    llm = GeneralLlm(model="openrouter/openai/gpt-4o-mini", temperature=0)

    # Create MultiSearcher
    searcher = MultiSearcher(llm)

    # Create a test question
    class TestQuestion:
        def __init__(self):
            self.question_text = "What will be the age of the oldest human alive by 2100?"
            self.background_info = "Current record is 122 years. Question asks about maximum human lifespan by 2100."
            self.resolution_criteria = "Age must be verified by Guinness World Records."

    question = TestQuestion()

    # Test comprehensive search
    print("Testing comprehensive search...")
    results = await searcher.comprehensive_search(question, max_queries=2, max_results_per_query=2)
    print(f"Found {len(results)} results")

    # Test relevance rating
    if results:
        print("Testing relevance rating...")
        rated = await searcher.rate_relevance(results, question)
        print(f"Top rated article score: {rated[0]['relevance_score'] if rated else 'N/A'}")

        # Test summarization
        print("Testing summarization...")
        summary = await searcher.summarize_research(rated, question)
        print(f"Summary length: {len(summary)} characters")

    print("MultiSearcher test completed!")


if __name__ == "__main__":
    asyncio.run(test_multi_searcher())