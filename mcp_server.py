# -*- coding: utf-8 -*-
"""
GenPark Reasoning Majority Voting Consensus Engine MCP Server
Exposes Self-Consistency consensus and answer clustering tools via JSON-RPC 2.0 over STDIO.
"""

import sys
import json
from client import GenParkReasoningMajorityVotingConsensusEngine

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-reasoning-majority-voting-consensus-engine", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "resolve_majority_consensus",
                        "description": "Extracts canonical answers across diverse reasoning rollouts, clusters equivalent semantic outputs, and calculates confidence-weighted consensus.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "candidate_rollouts": {
                                    "type": "array",
                                    "items": {"type": "object"}
                                }
                            },
                            "required": ["candidate_rollouts"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "resolve_majority_consensus":
            engine = GenParkReasoningMajorityVotingConsensusEngine()
            res = engine.resolve_majority_consensus(args.get("candidate_rollouts", []))
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}}
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32600, "message": f"Method '{method}' not supported"}}

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("MCP Server Discovery Test OK")
        eng = GenParkReasoningMajorityVotingConsensusEngine()
        test_res = eng.resolve_majority_consensus([
            {"output_text": "The answer is 42", "confidence_score": 0.95},
            {"output_text": "Therefore \\boxed{42}", "confidence_score": 0.90},
            {"output_text": "It is 17", "confidence_score": 0.60}
        ])
        print(f"Test Consensus: {test_res['consensus_canonical_answer']}")
        return

    for line in sys.stdin:
        if not line.strip(): continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
