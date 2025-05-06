
#!/usr/bin/env python3
"""CLI Wrapper for Gemini API (gemini-2.0-flash)"""

import argparse
import json
import os
import sys
import time
import threading
import signal
import requests
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type

MAX_TOKENS = 1048000
MODEL = "gemini-2.0-flash"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

class GeminiAPIError(Exception):
    pass

def get_auth_token():
    token = os.getenv("GEMINI_API_KEY")
    if not token:
        raise EnvironmentError("Please set the GEMINI_API_KEY environment variable.")
    return token

def enforce_token_limit(prompt, max_tokens):
    estimated_tokens = int(len(prompt.split()) * 1.33)
    if estimated_tokens > max_tokens:
        raise ValueError(f"Prompt too long: estimated {estimated_tokens} tokens > {max_tokens} limit.")
    return prompt

def start_spinner(stop_event):
    spinner = ["[ ⠋ ]", "[ ⠙ ]", "[ ⠹ ]", "[ ⠸ ]", "[ ⠼ ]", "[ ⠴ ]", "[ ⠦ ]", "[ ⠧ ]", "[ ⠇ ]", "[ ⠏ ]"]
    idx = 0
    while not stop_event.is_set():
        print(f"\r{spinner[idx % len(spinner)]} Thinking...", end="", flush=True)
        idx += 1
        time.sleep(0.1)
    print("\r" + " " * 40 + "\r", end="")

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3), retry=retry_if_exception_type((requests.exceptions.RequestException, GeminiAPIError)))
def send_gemini_request(prompt_text):
    enforce_token_limit(prompt_text, MAX_TOKENS)
    key = get_auth_token()
    url = GEMINI_API_URL.format(model=MODEL, key=key)

    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        raise GeminiAPIError(f"HTTP {response.status_code}: {response.text}")
    return response.json()

def parse_response(json_response):
    try:
        parts = json_response["candidates"][0]["content"]["parts"]
        return "".join(part.get("text", "") for part in parts)
    except (KeyError, IndexError, TypeError):
        raise GeminiAPIError("Unexpected response structure")

def signal_handler(sig, frame):
    print("\n[INFO] Interrupted by user.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(description="Send prompts to Google Gemini API (gemini-2.0-flash)")
    parser.add_argument("prompt", nargs=1, help="Prompt for the model. If stdin is piped, it will be prepended.")
    parser.add_argument("--complete", action="store_true", help="Show spinner while waiting for response")

    args = parser.parse_args()
    stdin_data = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    prompt_input = f"{stdin_data}\n\n{args.prompt[0].strip()}" if stdin_data else args.prompt[0].strip()

    try:
        if args.complete:
            stop_event = threading.Event()
            spinner_thread = threading.Thread(target=start_spinner, args=(stop_event,))
            spinner_thread.start()

        response = send_gemini_request(prompt_input)
        output = parse_response(response)

        if args.complete:
            stop_event.set()
            spinner_thread.join()

        print(output.strip() or "[INFO] No response.")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
