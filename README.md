# cnh-sandbox

Throwaway practice repo for hackathon tooling (Gitar code review and Elasticsearch). Not a submission; will be deleted.

## Drills

1. **Gitar review:** branch, add a function without type hints, open a PR, read Gitar's review.
2. **CI diagnosis and auto-apply:** branch, change `is_back_to_back` to use `<=`, open a PR, let CI fail. Watch Gitar diagnose it, then comment `gitar auto-apply:on` (or `gitar fix CI`) and confirm the fix lands. Then comment `gitar auto-apply:off`.
3. **Elastic:** follow the usage block at the top of `elastic_drill.py`. Check that `setup` finishes (first semantic_text use loads the inference model and can take minutes), that `search "securing the kernel with ebpf"` ranks t1/t2 even though "kernel" is not in t1, that `--quiet` filters, and that `aggs` returns buckets.
