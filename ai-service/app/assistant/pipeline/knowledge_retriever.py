"""
KnowledgeRetriever — wraps FAQRepository and PolicyRepository.
Called once per pipeline run; results passed into tool context so tools
don't need their own DB access for FAQ/policy lookups.
"""
import logging
from typing import Any, Dict, List

from app.assistant.repositories.knowledge_repositories import FAQRepository, PolicyRepository

logger = logging.getLogger(__name__)


class KnowledgeRetriever:
    def __init__(self, faq_repo: FAQRepository, policy_repo: PolicyRepository):
        self._faq = faq_repo
        self._policy = policy_repo

    async def retrieve(self, query: str, role: str = "customer") -> Dict[str, List[Dict[str, Any]]]:
        """
        Pre-fetches FAQ and policy results for a query.
        Results are injected into the tool context so FAQ/Policy tools
        can return them without an additional DB round-trip.
        """
        faq_results = await self._faq.retrieve(query=query, role=role)
        policy_results = await self._policy.retrieve(topic=query)

        logger.debug(f"KnowledgeRetriever: {len(faq_results)} FAQs, {len(policy_results)} policies")
        return {
            "faq_results": [{"q": f["question"], "a": f["answer"]} for f in faq_results],
            "policy_results": [{"topic": p["topic"], "content": p["content"]} for p in policy_results],
        }
