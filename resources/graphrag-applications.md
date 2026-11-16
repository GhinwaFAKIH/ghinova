# GraphRAG Applications — GHINOVA mini-project

**Level:** Advanced introduction · **Time:** 45–60 minutes · **Cost:** Free

GraphRAG combines connected facts (a graph) with evidence retrieval to help answer questions. This worksheet demonstrates the **graph traversal and evidence selection** parts, without claiming to run a complete generative system.

## 1. Scenario
A small workshop monitors machines. We want to know why a machine needs attention.

Example facts:
- Machine M-102 has a temperature reading of 89°C.
- Machine M-102 has a vibration reading of 6.2 mm/s.
- A maintenance note mentions bearing wear.

These are fictional example readings, not live equipment data.

## 2. Build a tiny graph with Python

```python
facts = {
    "M-102": [("temperature", "89 C"), ("vibration", "6.2 mm/s"), ("maintenance_note", "bearing wear")],
    "M-103": [("temperature", "64 C"), ("vibration", "2.1 mm/s")]
}
machine = "M-102"
print("Evidence for", machine)
for relation, value in facts[machine]:
    print("-", relation, ":", value)
```

## 3. Add simple rules

```python
temperature = 89
vibration = 6.2
if temperature > 80 and vibration > 5:
    print("Review required: both readings exceed example thresholds.")
else:
    print("No combined alert from these example thresholds.")
```

The thresholds above are for learning only. They are **not** industrial safety limits.

## 4. What a full GraphRAG application adds
1. Structured data and graph relationships.
2. Search over relevant maintenance documents.
3. A language model that drafts an explanation using retrieved evidence.
4. Source citations and a way to say “not enough information”.
5. Human review before operational decisions.

## 5. Your challenge
Add machine M-104, then write a function that lists all machines above the example temperature threshold. Explain why a graph link alone does not prove the cause of a failure.

**Next:** Try the [free graph retrieval notebook](https://ghinwafakih.github.io/ghinova/course-labs/shop/graph-retrieval-lab.ipynb).

© 2026 GHINOVA · Ghinwa.
