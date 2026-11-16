# Building AI Agents — GHINOVA beginner-friendly lab

**Level:** Intermediate · **Time:** 30–45 minutes · **Cost:** Free

An AI agent can choose steps and use approved tools to complete a task. Before connecting an AI model, practice the same workflow with a simple, predictable program.

## 1. Your first safe workflow
Goal: organize a list of tasks into “today” and “later”. This example does not send emails, open websites or change files.

```python
tasks = [
    {"name": "Review tutorial", "priority": "high"},
    {"name": "Choose blog image", "priority": "low"},
    {"name": "Check code example", "priority": "high"},
]
def organize(items):
    return {
        "today": [t["name"] for t in items if t["priority"] == "high"],
        "later": [t["name"] for t in items if t["priority"] != "high"]
    }
result = organize(tasks)
print(result)
```

## 2. The workflow as a picture

```text
Your request
    |
    v
Read approved tasks
    |
    v
Organize the tasks
    |
    v
Show draft to you
    |
    v
You decide what to do
```

## 3. From workflow to agent
A full agent may use a language model to choose which approved tool to use. That makes it flexible, but it also means you need checks: allowed actions, source verification, timeouts, logging and human approval.

## 4. Write your own agent instructions

> Organize only the task list I provide. Do not access other files, send messages or publish anything. Show the proposed result and ask for approval before taking action.

## 5. Exercises
1. Add a third category called “waiting”.
2. What could go wrong if the agent had permission to delete files?
3. Which actions should require explicit approval?

**Next:** [GHINOVA's free OpenClaw guide](https://ghinwafakih.github.io/ghinova/guides/openclaw-first-agent/).

© 2026 GHINOVA · Ghinwa.
