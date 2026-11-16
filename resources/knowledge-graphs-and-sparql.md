# Knowledge Graphs and SPARQL — GHINOVA starter workbook

**Level:** Intermediate · **Time:** 30–45 minutes · **Cost:** Free

## 1. Think in connections
A knowledge graph describes facts as links:

**Ghinwa → teaches → Python**  
**Python → usedFor → AI projects**  
**GHINOVA → offers → Tutorials**

Each fact has three parts: a **subject**, a **relationship**, and an **object**.

## 2. Your first graph (Turtle)

Copy this into a text file named `learning.ttl`:

```turtle
@prefix ex: <https://example.org/learning/> .

ex:Ghinwa ex:teaches ex:Python .
ex:Ghinwa ex:teaches ex:SPARQL .
ex:Python ex:usedFor ex:AIProjects .
ex:GHINOVA ex:offers ex:Tutorials .
```

The `ex:` prefix is a shortcut for a web address. This graph is fictional educational sample data.

## 3. Ask a question with SPARQL

```sparql
PREFIX ex: <https://example.org/learning/>
SELECT ?topic
WHERE {
  ex:Ghinwa ex:teaches ?topic .
}
```

Expected results: `ex:Python` and `ex:SPARQL`.

## 4. Try it in Python

```bash
python -m pip install rdflib
```

```python
from rdflib import Graph
graph = Graph()
graph.parse("learning.ttl", format="turtle")
query = """
PREFIX ex: <https://example.org/learning/>
SELECT ?topic WHERE { ex:Ghinwa ex:teaches ?topic . }
"""
for row in graph.query(query):
    print(row.topic)
```

## 5. Exercises
1. Add `ex:Ghinwa ex:teaches ex:RAG .`
2. Modify the query to retrieve everything that GHINOVA offers.
3. Add a person and a new relationship, then query it.

## 6. Why this matters
Graphs can connect evidence across documents, people, concepts and systems. SPARQL retrieves facts by following those relationships. GraphRAG systems may use these connections to support document retrieval and explanations.

**Next:** [Free graph retrieval notebook](https://ghinwafakih.github.io/ghinova/course-labs/shop/graph-retrieval-lab.ipynb).

© 2026 GHINOVA · Ghinwa.
