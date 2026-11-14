# Lesson JSON format

Create a JSON object with:
- `title`: nonempty string
- `level`: audience description
- `language`: English, French, Arabic, or the requested language
- `objectives`: list of nonempty strings
- `cells`: ordered list of `{ "type": "markdown" | "code", "source": "..." }`
- `sources`: list of source descriptions/URLs actually consulted (may be empty)
- `validation`: honest text, e.g. "Syntax checked only; code has not been executed."

Code cells contain ordinary Python (no notebook magics or shell commands). Explain installation commands in Markdown cells. Use at least one Markdown cell and one code cell. Include exercises and clearly separated solutions. Do not add generated execution outputs.

The exporter refuses to overwrite existing output files unless explicitly given `--overwrite`. Normally write each revision in a new output directory.
