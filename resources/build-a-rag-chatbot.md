# Build a RAG Chatbot — GHINOVA project workbook

**Level:** Intermediate · **Time:** 60–90 minutes · **Cost:** Free

## What you'll build
A small question-answering app that searches your own notes before drafting an answer. This example uses Python and a local TF-IDF retriever; it does **not** require an API key or an LLM. It teaches the retrieval step used in RAG.

## 1. Install
Create a Python environment and run:

```bash
python -m pip install scikit-learn
```

## 2. Copy this complete program
Save as `retrieval_demo.py`:

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

documents = [
    "GHINOVA teaches Python and practical AI.",
    "RAG retrieves relevant documents before generating an answer.",
    "Knowledge graphs connect entities and their relationships.",
]
question = input("Ask a question: ")
vectorizer = TfidfVectorizer()
matrix = vectorizer.fit_transform(documents + [question])
scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
best = int(scores.argmax())
if scores[best] < 0.1:
    print("I don't have enough information to answer.")
else:
    print("Most relevant source:", documents[best])
    print("Similarity score:", round(float(scores[best]), 3))
```

Run `python retrieval_demo.py`. Ask “What does RAG do?” and then ask something outside the notes.

## 3. Turn retrieval into RAG
In a full RAG system, the retrieved text is passed to a language model with an instruction like:

> Answer using only the source text. If the source does not contain the answer, say so. Include the source reference.

The example above intentionally stops before generation, so it cannot hallucinate a generated answer.

## 4. Your challenge
Add five notes of your own. Test five questions. Record which note was retrieved and whether it was relevant.

| Question | Expected note | Retrieved note | Relevant? |
| --- | --- | --- | --- |
| What does RAG do? | RAG note | | |
| What is a knowledge graph? | KG note | | |

## 5. Check your learning
- What happens when the answer is not in the documents?
- Why is the similarity threshold useful?
- Why must you cite the original document rather than the model's confidence?

**Next:** Try the [free PDF chatbot tutorial](https://ghinwafakih.github.io/ghinova/guides/pdf-chatbot-python/).

© 2026 GHINOVA · Ghinwa. Educational material; review generated answers before relying on them.
