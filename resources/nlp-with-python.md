# NLP with Python — GHINOVA hands-on workbook

**Level:** Beginner–intermediate · **Time:** 30–45 minutes · **Cost:** Free

Natural language processing (NLP) helps software work with human language. This mini-lab shows how to clean and count words without external libraries.

## 1. Run this example

```python
import re
from collections import Counter

reviews = [
    "The chatbot is helpful and fast!",
    "Helpful tutorial, but the setup was slow.",
    "The chatbot answers questions quickly."
]
def tokenize(text):
    return re.findall(r"[a-z]+", text.lower())

words = [word for review in reviews for word in tokenize(review)]
counts = Counter(words)
print("Most common words:", counts.most_common(8))
```

## 2. Understand the output
- **Lowercasing** makes “Helpful” and “helpful” the same word.
- **Tokenization** splits a sentence into smaller pieces.
- **Counting** reveals repeated words, but not their meaning.

## 3. Try a simple keyword classifier

```python
positive = {"helpful", "fast", "great"}
for review in reviews:
    tokens = set(tokenize(review))
    print("positive keyword found:", bool(tokens & positive), "|", review)
```

This is a rule-based demonstration, not a trained sentiment model. It will miss sarcasm, negation and unfamiliar words.

## 4. Exercises
1. Add two reviews in French or English. What happens to accented characters?
2. Add “not helpful” to the data. Why does a keyword-only rule get this wrong?
3. Replace the positive words with words relevant to your own project.

## 5. Mini-project
Create a CSV file with 10 short customer comments. Count the 10 most frequent words. Write down two limitations of your approach.

**Next:** Explore [GHINOVA's shop](https://ghinwafakih.github.io/ghinova/shop.html) for more hands-on labs.

© 2026 GHINOVA · Ghinwa.
