"""Agent responsible for generating content plans."""

from __future__ import annotations

from typing import Dict, List


class ContentAgent:
    """Produce lightweight content roadmaps without external LLM dependencies."""

    def generate_strategy(self, brand_name: str, niche: str | None) -> Dict[str, List[str]]:
        base_topics = [
            "Behind-the-scenes",
            "Educational tips",
            "Trending challenges",
            "Customer testimonials",
        ]

        if niche:
            base_topics.append(f"Niche spotlight: {niche.title()}")

        weekly_plan = [
            f"Day {idx + 1}: Focus on {topic}" for idx, topic in enumerate(base_topics[:5])
        ]

        hooks = [
            f"What {brand_name} won't tell you...",
            f"3 secrets from {brand_name}'s playbook",
            f"Why {brand_name} dominates {niche or 'the scene'}",
        ]

        return {
            "weekly_plan": weekly_plan,
            "hooks": hooks,
            "cta": ["Follow for daily inspiration", "Comment your thoughts", "Share if helpful"],
        }
