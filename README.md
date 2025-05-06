```markdown
# Gemini CLI

A simple command-line interface for Google's Gemini 2.0 Flash API.

## 🔧 Installation

```bash
pip install .
```

## 🚀 Usage Examples

```bash
gemini "Explain how AI works"
echo "Some text to summarize" | gemini "Summarize this"
gemini "Generate response and save to file" > result.txt
```

## 📋 Requirements

You must set your Gemini API key as an environment variable.

### 1. Export the API Key

```bash
export GEMINI_API_KEY="your_key_here"
```

### 2. Make It Permanent

#### For Zsh users (macOS default):

```bash
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

#### For Bash users (Linux default):

```bash
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

You only need to do this once. After that, the `gemini` command will work in any new terminal session.

---

## ⚖️ License

MIT
```

---
