# -*- coding: utf-8 -*-
"""
Example usage of GenParkReasoningMajorityVotingConsensusEngine
Demonstrates Self-Consistency Best-of-N voting across 5 stochastic reasoning traces.
"""

from client import GenParkReasoningMajorityVotingConsensusEngine

def main():
    engine = GenParkReasoningMajorityVotingConsensusEngine()

    rollouts = [
        {"rollout_id": "T1", "output_text": "After computing the modular arithmetic, \\boxed{24}", "confidence_score": 0.96, "step_count": 8},
        {"rollout_id": "T2", "output_text": "Thus, the expression must divide 24 exactly. Answer is 24.", "confidence_score": 0.94, "step_count": 7},
        {"rollout_id": "T3", "output_text": "We find the constant factor is \\boxed{24}", "confidence_score": 0.91, "step_count": 10},
        {"rollout_id": "T4", "output_text": "Therefore the product is 12.", "confidence_score": 0.72, "step_count": 6},
        {"rollout_id": "T5", "output_text": "By prime factorization, \\boxed{24}", "confidence_score": 0.95, "step_count": 9}
    ]

    res = engine.resolve_majority_consensus(rollouts)

    print("================================================================")
    print("GenPark Reasoning Majority Voting Consensus Engine - Live Runs")
    print("================================================================\n")
    print(f"Consensus Answer      : {res['consensus_canonical_answer']}")
    print(f"Weighted Confidence   : {res['weighted_consensus_confidence_pct']}%")
    print(f"Raw Vote Agreement    : {res['raw_vote_consensus_ratio_pct']}% [{res['consensus_certainty_verdict']}]")
    print(f"Distinct Clusters     : {res['distinct_clusters_count']} clusters\n")
    print("Cluster Leaderboard:")
    for cl in res['cluster_breakdown']:
        print(f"  * Answer '{cl['answer']:<10}': {cl['votes']} votes ({cl['normalized_weight_pct']}%) -> Rollouts: {', '.join(cl['rollouts'])}")

if __name__ == "__main__":
    main()
