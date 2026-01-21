"""
Full user workflow test - simulates normal MCP server usage.

This test demonstrates a realistic user workflow:
1. Discover available tools
2. Reload CSV data
3. Perform multiple search queries
4. Output results in nicely formatted JSON

The test works with both stdio and HTTP transports.
"""

import json


class TestStdioUserWorkflow:
    """Full user workflow test for stdio transport."""

    def test_full_user_workflow(self, stdio_client):
        """Simulate a complete user workflow: discover tools, reload data, query."""
        workflow_results = {"workflow": "stdio_user_workflow", "steps": []}

        # Step 1: Discover available tools
        step1 = {
            "step": 1,
            "action": "discover_tools",
            "request": {"method": "tools/list", "params": {}},
        }
        response = stdio_client.send_request("tools/list")
        step1["response"] = response
        step1["tools_found"] = len(response.get("result", {}).get("tools", []))
        workflow_results["steps"].append(step1)

        # Step 2: Reload CSV data
        step2 = {
            "step": 2,
            "action": "reload_transactions",
            "request": {
                "method": "tools/call",
                "params": {"name": "reload_transactions", "arguments": {}},
            },
        }
        response = stdio_client.send_request(
            "tools/call", {"name": "reload_transactions", "arguments": {}}
        )
        step2["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                reload_data = json.loads(result_data)
                step2["reload_summary"] = {
                    "total_records": reload_data.get("total_records", 0),
                    "new_records": reload_data.get("new_records", 0),
                    "removed_records": reload_data.get("removed_records", 0),
                    "files_scanned": reload_data.get("files_scanned", 0),
                }
            except json.JSONDecodeError:
                step2["reload_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step2)

        # Step 3: Query 1 - Simple search
        step3 = {
            "step": 3,
            "action": "simple_search",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_transactions",
                    "arguments": {"query": "grocery", "max_results": 5},
                },
            },
        }
        response = stdio_client.send_request(
            "tools/call",
            {"name": "search_transactions", "arguments": {"query": "grocery", "max_results": 5}},
        )
        step3["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                search_data = json.loads(result_data)
                step3["search_summary"] = {
                    "results_count": len(search_data.get("results", [])),
                    "matched": search_data.get("summary", {}).get("matched", 0),
                    "sample_results": search_data.get("results", [])[:2],  # First 2 results
                }
            except json.JSONDecodeError:
                step3["search_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step3)

        # Step 4: Query 2 - Filtered search with date range
        step4 = {
            "step": 4,
            "action": "filtered_search",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_transactions",
                    "arguments": {
                        "query": "payment",
                        "date_start": "2024-01-01",
                        "date_end": "2024-12-31",
                        "max_results": 3,
                    },
                },
            },
        }
        response = stdio_client.send_request(
            "tools/call",
            {
                "name": "search_transactions",
                "arguments": {
                    "query": "payment",
                    "date_start": "2024-01-01",
                    "date_end": "2024-12-31",
                    "max_results": 3,
                },
            },
        )
        step4["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                search_data = json.loads(result_data)
                step4["search_summary"] = {
                    "results_count": len(search_data.get("results", [])),
                    "matched": search_data.get("summary", {}).get("matched", 0),
                    "filters_applied": search_data.get("filters", {}),
                    "sample_results": search_data.get("results", [])[:2],
                }
            except json.JSONDecodeError:
                step4["search_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step4)

        # Step 5: Query 3 - Amount range search
        step5 = {
            "step": 5,
            "action": "amount_range_search",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_transactions",
                    "arguments": {"amount_min": -1000, "amount_max": -100, "max_results": 3},
                },
            },
        }
        response = stdio_client.send_request(
            "tools/call",
            {
                "name": "search_transactions",
                "arguments": {"amount_min": -1000, "amount_max": -100, "max_results": 3},
            },
        )
        step5["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                search_data = json.loads(result_data)
                step5["search_summary"] = {
                    "results_count": len(search_data.get("results", [])),
                    "matched": search_data.get("summary", {}).get("matched", 0),
                    "amount_range": {"min": -1000, "max": -100},
                    "sample_results": search_data.get("results", [])[:2],
                }
            except json.JSONDecodeError:
                step5["search_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step5)

        # Output workflow results as nicely formatted JSON
        workflow_json = json.dumps(workflow_results, indent=2, default=str)
        print("\n" + "=" * 80)
        print("STDIO USER WORKFLOW TEST RESULTS")
        print("=" * 80)
        print(workflow_json)
        print("=" * 80 + "\n")

        # Basic assertions
        assert "steps" in workflow_results
        assert len(workflow_results["steps"]) == 5
        assert workflow_results["steps"][0]["tools_found"] > 0


class TestHttpUserWorkflow:
    """Full user workflow test for HTTP transport."""

    def test_full_user_workflow(self, http_client):
        """Simulate a complete user workflow: discover tools, reload data, query."""
        workflow_results = {"workflow": "http_user_workflow", "steps": []}

        # Step 1: Discover available tools
        step1 = {
            "step": 1,
            "action": "discover_tools",
            "request": {"method": "tools/list", "params": {}},
        }
        response = http_client.send_request("tools/list")
        step1["response"] = response
        step1["tools_found"] = len(response.get("result", {}).get("tools", []))
        workflow_results["steps"].append(step1)

        # Step 2: Reload CSV data
        step2 = {
            "step": 2,
            "action": "reload_transactions",
            "request": {
                "method": "tools/call",
                "params": {"name": "reload_transactions", "arguments": {}},
            },
        }
        response = http_client.send_request(
            "tools/call", {"name": "reload_transactions", "arguments": {}}
        )
        step2["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                reload_data = json.loads(result_data)
                step2["reload_summary"] = {
                    "total_records": reload_data.get("total_records", 0),
                    "new_records": reload_data.get("new_records", 0),
                    "removed_records": reload_data.get("removed_records", 0),
                    "files_scanned": reload_data.get("files_scanned", 0),
                }
            except json.JSONDecodeError:
                step2["reload_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step2)

        # Step 3: Query 1 - Simple search
        step3 = {
            "step": 3,
            "action": "simple_search",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_transactions",
                    "arguments": {"query": "grocery", "max_results": 5},
                },
            },
        }
        response = http_client.send_request(
            "tools/call",
            {"name": "search_transactions", "arguments": {"query": "grocery", "max_results": 5}},
        )
        step3["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                search_data = json.loads(result_data)
                step3["search_summary"] = {
                    "results_count": len(search_data.get("results", [])),
                    "matched": search_data.get("summary", {}).get("matched", 0),
                    "sample_results": search_data.get("results", [])[:2],
                }
            except json.JSONDecodeError:
                step3["search_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step3)

        # Step 4: Query 2 - Filtered search with date range
        step4 = {
            "step": 4,
            "action": "filtered_search",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_transactions",
                    "arguments": {
                        "query": "payment",
                        "date_start": "2024-01-01",
                        "date_end": "2024-12-31",
                        "max_results": 3,
                    },
                },
            },
        }
        response = http_client.send_request(
            "tools/call",
            {
                "name": "search_transactions",
                "arguments": {
                    "query": "payment",
                    "date_start": "2024-01-01",
                    "date_end": "2024-12-31",
                    "max_results": 3,
                },
            },
        )
        step4["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                search_data = json.loads(result_data)
                step4["search_summary"] = {
                    "results_count": len(search_data.get("results", [])),
                    "matched": search_data.get("summary", {}).get("matched", 0),
                    "filters_applied": search_data.get("filters", {}),
                    "sample_results": search_data.get("results", [])[:2],
                }
            except json.JSONDecodeError:
                step4["search_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step4)

        # Step 5: Query 3 - Amount range search
        step5 = {
            "step": 5,
            "action": "amount_range_search",
            "request": {
                "method": "tools/call",
                "params": {
                    "name": "search_transactions",
                    "arguments": {"amount_min": -1000, "amount_max": -100, "max_results": 3},
                },
            },
        }
        response = http_client.send_request(
            "tools/call",
            {
                "name": "search_transactions",
                "arguments": {"amount_min": -1000, "amount_max": -100, "max_results": 3},
            },
        )
        step5["response"] = response
        if "result" in response:
            result_data = response["result"].get("content", [{}])[0].get("text", "{}")
            try:
                search_data = json.loads(result_data)
                step5["search_summary"] = {
                    "results_count": len(search_data.get("results", [])),
                    "matched": search_data.get("summary", {}).get("matched", 0),
                    "amount_range": {"min": -1000, "max": -100},
                    "sample_results": search_data.get("results", [])[:2],
                }
            except json.JSONDecodeError:
                step5["search_summary"] = {"raw_response": result_data[:200]}
        workflow_results["steps"].append(step5)

        # Output workflow results as nicely formatted JSON
        workflow_json = json.dumps(workflow_results, indent=2, default=str)
        print("\n" + "=" * 80)
        print("HTTP USER WORKFLOW TEST RESULTS")
        print("=" * 80)
        print(workflow_json)
        print("=" * 80 + "\n")

        # Basic assertions
        assert "steps" in workflow_results
        assert len(workflow_results["steps"]) == 5
        assert workflow_results["steps"][0]["tools_found"] > 0
