# -*- coding: utf-8 -*-
"""
GenPark Reasoning Majority Voting Consensus Engine Client
Implements Self-Consistency Best-of-N temperature resampler with semantic deduplication and confidence-weighted voting.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
import re
from typing import Dict, Any, List

class GenParkReasoningMajorityVotingConsensusEngine:
    """
    Self-Consistency (Wang et al.) Weighted Consensus Engine:
    Extracts canonical answers across diverse reasoning rollouts,
    clusters equivalent semantic outputs, and calculates confidence-weighted consensus.
    """

    def __init__(self, answer_similarity_threshold: float = 0.82):
        self.sim_thresh = answer_similarity_threshold

    def normalize_answer(self, raw_text: str) -> str:
        """Extracts and normalizes final answer from LaTeX boxed, equals sign, or terminal text."""
        # Check \boxed{...}
        m = re.search(r'\\boxed\{([^}]+)\}', raw_text)
        if m:
            ans = m.group(1).strip()
        else:
            # Check last sentence or line
            lines = [l.strip() for l in raw_text.strip().split('\n') if l.strip()]
            last_line = lines[-1] if lines else raw_text
            # Check after 'is' or '='
            if "=" in last_line:
                ans = last_line.split("=")[-1].strip().rstrip(".")
            else:
                ans = last_line.rstrip(".")

        # Clean punctuation and whitespace
        ans = re.sub(r'\s+', ' ', ans).strip().lower()
        return ans

    def calculate_string_similarity(self, str_a: str, str_b: str) -> float:
        """Jaccard token similarity over normalized terms."""
        set_a = set(str_a.split())
        set_b = set(str_b.split())
        if not set_a or not set_b:
            return 1.0 if str_a == str_b else 0.0
        return len(set_a.intersection(set_b)) / len(set_a.union(set_b))

    def resolve_majority_consensus(
        self,
        candidate_rollouts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Clusters Best-of-N reasoning rollouts into consensus groups.
        """
        if not candidate_rollouts:
            return {"error": "Empty candidate rollouts"}

        clusters = []  # list of dicts: {"canonical": str, "weight": float, "items": list}

        for c in candidate_rollouts:
            norm_ans = self.normalize_answer(c.get("output_text", ""))
            conf = c.get("confidence_score", 0.80)
            step_count = c.get("step_count", 5)

            # Weight incorporates confidence with mild parsimony preference
            weight = conf * (1.0 / (1.0 + 0.01 * max(0, step_count - 10)))

            matched_cluster = None
            for cl in clusters:
                if cl["canonical"] == norm_ans or self.calculate_string_similarity(cl["canonical"], norm_ans) >= self.sim_thresh:
                    matched_cluster = cl
                    break

            if matched_cluster:
                matched_cluster["weight"] += weight
                matched_cluster["items"].append(c.get("rollout_id", f"R-{len(matched_cluster['items'])+1}"))
            else:
                clusters.append({
                    "canonical": norm_ans,
                    "weight": weight,
                    "items": [c.get("rollout_id", "R-1")]
                })

        # Sort clusters by cumulative weight descending
        clusters.sort(key=lambda x: x["weight"], reverse=True)
        total_weight = sum(cl["weight"] for cl in clusters) or 1.0
        winner = clusters[0]

        consensus_ratio = round((len(winner["items"]) / len(candidate_rollouts)) * 100.0, 1)
        weighted_conf = round((winner["weight"] / total_weight) * 100.0, 1)

        return {
            "consensus_canonical_answer": winner["canonical"],
            "weighted_consensus_confidence_pct": weighted_conf,
            "raw_vote_consensus_ratio_pct": consensus_ratio,
            "total_candidate_rollouts": len(candidate_rollouts),
            "distinct_clusters_count": len(clusters),
            "consensus_certainty_verdict": "STRONG_CONSENSUS" if consensus_ratio >= 65.0 else ("CONVERGENT_MAJORITY" if consensus_ratio >= 45.0 else "DIVERGENT_HIGH_UNCERTAINTY"),
            "cluster_breakdown": [
                {
                    "answer": cl["canonical"],
                    "votes": len(cl["items"]),
                    "normalized_weight_pct": round((cl["weight"] / total_weight) * 100.0, 1),
                    "rollouts": cl["items"]
                }
                for cl in clusters
            ]
        }
