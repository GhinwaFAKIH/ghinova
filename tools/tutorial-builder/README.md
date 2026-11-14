# GHINOVA Tutorial Builder for OpenClaw

A dedicated OpenClaw workspace for planning and writing tutorials, exercises and solutions, then exporting a Markdown guide and Jupyter/Colab-compatible notebook. It uses OpenClaw's tools and the local Ollama model you select. It is not a separate LLM or a hosted website chatbot.

## On your Mac

Prerequisites: your working OpenClaw installation, Python 3, Ollama running, and an installed local model with tool support. No API key or paid service is required by this package. Model downloads, storage, memory and electricity still use your own computer's resources. Quality and speed depend on the model and Mac.

1. Download this repository (GitHub: Code → Download ZIP), unzip it, and open Terminal in `tools/tutorial-builder`.
2. Run `ollama list` to find the exact name of an installed local model. Do not select a cloud model.
3. Check `openclaw models list` to confirm the local Ollama model is available to OpenClaw. If not, configure the local Ollama provider first using the official documentation below. Do not change the main agent's model just to install this workspace.
4. Run `python3 setup.py --model YOUR_LOCAL_MODEL_NAME` with the actual name. The installer verifies local Ollama and tool support, creates a separate workspace, and registers `ghinova-tutorial`. It refuses to overwrite an existing workspace. It does not change provider settings, existing agents, model fallbacks, tool permissions, or install models.
5. In OpenClaw, check the new agent's model is `ollama/<your model>`, local endpoint `http://127.0.0.1:11434`, and remove any inherited paid model fallbacks for this agent before use. If unsure, inspect the configuration before generating anything. Workspace instructions alone do not enforce billing or sandboxing.
6. Open `openclaw dashboard`, select the new agent and start a new session. Paste `FIRST-PROMPT.txt`. Approve the plan when ready. If filesystem/exec tools are unavailable, enable only what this workspace needs in your OpenClaw configuration; do not grant broad system access.

Written outputs appear in `~/.openclaw/workspace-ghinova-tutorial/outputs/<topic>/`. The export script uses Python's standard library, validates lesson data and Python syntax, and creates `tutorial.md` and `tutorial.ipynb`. It never executes generated lesson code. Review generated code before testing it in an isolated environment. Colab compatibility does not guarantee dependencies will install or code will run unchanged.

## Review workflow

Topic → outline → your approval → explanations and code → exercises and solutions → export → validation report → your publication decision.

No posting, email sending, cloud publishing or paid API calls are built into this package. The same agent can work in French or Arabic when requested. Start with a short lesson to evaluate your model's reliability.

## Validation and limitations

Exporter tested on valid data, Unicode, invalid Python syntax and overwrite protection. Installer syntax checked. This package has not been installed or tested end-to-end on Ginwa's Mac; OpenClaw and a local model are unavailable in the build environment. Registration flags are based on current official docs; older versions may differ. If setup fails, keep the error and `openclaw --version` output (never share tokens).

Official references:
- https://docs.openclaw.ai/cli/agents
- https://docs.openclaw.ai/providers/ollama
- https://docs.openclaw.ai/providers/ollama/configuration

The free public GHINOVA website guide is separate and unchanged.
