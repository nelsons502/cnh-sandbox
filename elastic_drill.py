"""Practice drill for the Elastic Cloud trial. Standard library only.

Usage:
  export ES_URL="https://<deployment>.es.<region>.elastic.cloud"   # or http://localhost:9200
  export ES_API_KEY="<base64 api key>"
  python3 elastic_drill.py setup     # create index with semantic_text (waits on the inference model)
  python3 elastic_drill.py search "securing the kernel with ebpf"
  python3 elastic_drill.py aggs
  python3 elastic_drill.py teardown
"""
import json
import os
import sys
import urllib.error
import urllib.request

INDEX = "drill-talks"
ES_URL = os.environ.get("ES_URL", "http://localhost:9200").rstrip("/")
ES_API_KEY = os.environ.get("ES_API_KEY", "")

TALKS = [
    ("t1", "Runtime Guardrails Without Sidecars", "How we used eBPF programs to enforce network and syscall policy in multi-tenant clusters.", "Security", "high", "loud"),
    ("t2", "Kernel-Level Visibility for Platform Teams", "Tracing every packet and process without changing application code, using extended Berkeley Packet Filter.", "Observability", "medium", "moderate"),
    ("t3", "Scaling Spark on Kubernetes", "Shuffle services, YuniKorn scheduling and lessons from petabyte-scale data platforms.", "Data", "high", "loud"),
    ("t4", "A Gentle Introduction to Admission Control", "Writing your first validating webhook and policy with Kyverno, explained for beginners.", "Security", "low", "quiet"),
    ("t5", "GPU Sharing for Inference Workloads", "Dynamic resource allocation and time slicing for serving models efficiently.", "AI", "medium", "moderate"),
]


def call(method, path, body=None):
    req = urllib.request.Request(ES_URL + path, method=method, data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Content-Type", "application/json")
    if ES_API_KEY:
        req.add_header("Authorization", "ApiKey " + ES_API_KEY)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as err:
        print(f"{method} {path} -> {err.code}: {err.read().decode()[:800]}")
        raise SystemExit(1)


def setup():
    call("PUT", f"/{INDEX}", {
        "mappings": {"properties": {
            "title": {"type": "text"},
            "description": {"type": "text", "copy_to": "description_semantic"},
            "description_semantic": {"type": "semantic_text"},
            "track": {"type": "keyword"},
            "crowd": {"type": "keyword"},
            "noise": {"type": "keyword"},
        }}
    })
    lines = []
    for talk_id, title, desc, track, crowd, noise in TALKS:
        lines.append(json.dumps({"index": {"_index": INDEX, "_id": talk_id}}))
        lines.append(json.dumps({"title": title, "description": desc, "track": track, "crowd": crowd, "noise": noise}))
    req = urllib.request.Request(ES_URL + "/_bulk?refresh=true", method="POST", data=("\n".join(lines) + "\n").encode())
    req.add_header("Content-Type", "application/x-ndjson")
    if ES_API_KEY:
        req.add_header("Authorization", "ApiKey " + ES_API_KEY)
    with urllib.request.urlopen(req, timeout=600) as resp:
        result = json.loads(resp.read())
    print("bulk errors:", result.get("errors"), "items:", len(result.get("items", [])))


def search(query, quiet_only=False):
    lexical = {"multi_match": {"query": query, "fields": ["title^2", "description"]}}
    semantic = {"semantic": {"field": "description_semantic", "query": query}}
    filters = [{"term": {"noise": "quiet"}}] if quiet_only else []
    body = {
        "retriever": {"rrf": {
            "retrievers": [
                {"standard": {"query": {"bool": {"must": lexical, "filter": filters}}}},
                {"standard": {"query": {"bool": {"must": semantic, "filter": filters}}}},
            ],
            "rank_window_size": 20,
        }},
        "_source": ["title", "track", "noise"],
    }
    for hit in call("POST", f"/{INDEX}/_search", body)["hits"]["hits"]:
        print(f"{hit['_score']:.4f}  {hit['_source']['title']}  [{hit['_source']['track']}, {hit['_source']['noise']}]")


def aggs():
    body = {"size": 0, "aggs": {"by_track": {"terms": {"field": "track"}, "aggs": {"by_noise": {"terms": {"field": "noise"}}}}}}
    print(json.dumps(call("POST", f"/{INDEX}/_search", body)["aggregations"], indent=2))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "setup":
        setup()
    elif cmd == "search":
        search(" ".join(a for a in sys.argv[2:] if a != "--quiet"), quiet_only="--quiet" in sys.argv)
    elif cmd == "aggs":
        aggs()
    elif cmd == "teardown":
        print(call("DELETE", f"/{INDEX}"))
    else:
        print(__doc__)
