#!/usr/bin/env python3
"""CLI Wrapper for Gemini API (gemini-2.0-flash) — colorized output + working spinner on macOS"""

import argparse
import json
import os
import sys
import time
import threading
import signal
import requests
import re
import itertools
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Constants
MAX_TOKENS = 1048000
MODEL = "gemini-2.0-flash"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

class GeminiAPIError(Exception):
    pass

# Environment token
def get_auth_token():
    token = os.getenv("GEMINI_API_KEY")
    if not token:
        raise EnvironmentError("Please set the GEMINI_API_KEY environment variable.")
    return token

# Token safety check
def enforce_token_limit(prompt, max_tokens):
    estimated_tokens = int(len(prompt.split()) * 1.33)
    if estimated_tokens > max_tokens:
        raise ValueError(f"Prompt too long: estimated {estimated_tokens} tokens > {max_tokens} limit.")
    return prompt

# Spinner that works reliably on macOS
def start_spinner(stop_event):
    spinner_cycle = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
    try:
        while not stop_event.is_set():
            spin = next(spinner_cycle)
            sys.stdout.write(f"\r{Fore.MAGENTA}[ {spin} ] Thinking...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        # Clear spinner line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

# Request to Gemini
@retry(wait=wait_fixed(2), stop=stop_after_attempt(3),
       retry=retry_if_exception_type((requests.exceptions.RequestException, GeminiAPIError)))
def send_gemini_request(prompt_text):
    enforce_token_limit(prompt_text, MAX_TOKENS)
    key = get_auth_token()
    url = GEMINI_API_URL.format(model=MODEL, key=key)

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise GeminiAPIError(f"HTTP {response.status_code}: {response.text}")
    return response.json()

# Format Gemini output for CLI
def parse_response(json_response):
    try:
        parts = json_response["candidates"][0]["content"]["parts"]
        raw_text = "".join(part.get("text", "") for part in parts)

        # Strip markdown
        clean_text = re.sub(r'\*\*`([^`]*)`\*\*', r'\1', raw_text)
        clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
        clean_text = re.sub(r'`([^`]*)`', r'\1', clean_text)
        clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean_text)

        lines = clean_text.splitlines()
        output_lines = []
        section_indent = False

        for line in lines:
            stripped = line.strip()
            if not stripped:
                output_lines.append("")
                continue

            # Section headers
            if re.match(r"^\d+\.\s", stripped) or stripped.endswith(":") or "recommendation" in stripped.lower():
                section_indent = False
                header = stripped.upper()
                output_lines.append(Fore.CYAN + Style.BRIGHT + "\n" + header)
                output_lines.append(Fore.CYAN + "-" * len(header))
            # Example commands
            elif stripped.lower().startswith("example"):
                output_lines.append(Fore.GREEN + "    " + stripped)
            # CLI flags
            elif re.match(r"^-[\w\-]+", stripped):
                output_lines.append(Fore.YELLOW + "  " + stripped)
            # Bullets or numbered items
            elif stripped.startswith("*") or stripped.startswith("-"):
                output_lines.append("  " + stripped.lstrip("*- ").strip())
            else:
                output_lines.append(stripped)

        return "\n".join(output_lines)

    except (KeyError, IndexError, TypeError):
        raise GeminiAPIError("Unexpected response structure")

# Handle Ctrl+C
def signal_handler(sig, frame):
    print("\n[INFO] Interrupted by user.")
    sys.exit(0)

# Main entry point
def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Send prompts to Google Gemini API (gemini-2.0-flash)")
    parser.add_argument("prompt", nargs=1, help="Prompt for the model. If stdin is piped, it will be prepended.")
    parser.add_argument("--complete", action="store_true", help="Show spinner while waiting for response")
    args = parser.parse_args()

    stdin_data = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    prompt_input = f"{stdin_data}\n\n{args.prompt[0].strip()}" if stdin_data else args.prompt[0].strip()

    stop_event = None
    spinner_thread = None

    try:
        if args.complete:
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=start_spinner, args=(stop_event,), daemon=True)
            spinner_thread.start()

        response = send_gemini_request(prompt_input)
        output = parse_response(response)

        print(output.strip() or "[INFO] No response.")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if stop_event:
            stop_event.set()
        if spinner_thread:
            spinner_thread.join()

if __name__ == "__main__":
    main()
