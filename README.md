# Gemini CLI

A simple command-line interface for Google's Gemini 2.0 Flash API.

## Installation

```bash
pip install .
```

## Usage

```bash
gemini "Explain how AI works"
echo "data" | gemini "Summarize this"
gemini "Instruction" --complete
```

## Requirements

- Set environment variable:
  ```bash
  export GEMINI_API_KEY=your_key_here
  ```

## License

MIT
