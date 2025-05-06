# 🚀 Gemini CLI

A lightweight and user-friendly command-line interface for interacting with **Google's Gemini 2.0 Flash API** — ideal for quick queries, summarization, text generation, and automation workflows.

---

## 🔧 Installation

Clone the repo and install locally using `pip`:

```bash
pip install .
```

---

## ⚙️ Requirements

You need a Gemini API key from Google.  
👉 Get yours here: [https://aistudio.google.com/](https://aistudio.google.com/)

Once you have the key, set it as an environment variable.

### 1. Export the API Key (temporary for current session)

```bash
export GEMINI_API_KEY="your_key_here"
```

### 2. Make it permanent

#### For Zsh users (macOS default shell):

```bash
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.zshrc
source ~/.zshrc
```

#### For Bash users (most Linux distros):

```bash
echo 'export GEMINI_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🧪 Usage Examples

```bash
gemini "Explain how AI works"
```

Use piped input with your instruction:

```bash
echo "This is a paragraph to summarize." | gemini "Summarize this"
```

Save output to a file:

```bash
gemini "Write a short poem" > poem.txt
```

Enable spinner while waiting for a complete response:

```bash
gemini "Give me a market analysis" --complete
```

---

## 🛠️ Features

- Gemini 2.0 Flash model support
- Handles long prompts (up to ~1 million tokens)
- Streamlined spinner for long-form completions
- Supports stdin, file output, and piping
- Lightweight and dependency-free CLI experience

---

## ⚖️ License

MIT – free to use, modify, and distribute.
```

---
