Start with First Project

This repository contains a minimal starter for building a Python-based AI assistant. It implements the example plan from the course README and provides a runnable script to make your first API call.

Getting started

- Requirements: Python 3.8+ and `pip`.
- Install dependencies:

```bash
pip install -r requirements.txt
```

- Create an environment file from the example and add your OpenAI key:

```bash
copy .env.example .env
# then edit .env and set OPENAI_API_KEY
```

- Run the assistant:

```bash
python assistant.py
```

Files added

- [assistant.py](Ai_Projects/assistant.py): Minimal script that reads `OPENAI_API_KEY` from `.env` and sends a prompt to OpenAI's chat API.
- [requirements.txt](Ai_Projects/requirements.txt): Python dependencies (`python-dotenv`, `openai`).
- [.env.example](Ai_Projects/.env.example): Example environment file.

Next steps

- Expand `assistant.py` to keep chat history, add a CLI, or a small web UI.
- Swap the backend to Google AI Studio by replacing the SDK calls.

 I implemented both a CLI chat with history and a small Flask web UI.

 CLI usage

 - Interactive chat (keeps local history during the session):

 ```bash
 python Ai_Projects/assistant.py --mode interactive
 ```

 - Single-call mode (print a single reply):

 ```bash
 python Ai_Projects/assistant.py --mode once --prompt "Hello, AI!"
 ```

 Flask web UI

 - Start the server:

 ```bash
 # from the workspace root
 pip install -r Ai_Projects/requirements.txt
 python Ai_Projects/app.py
 ```

 - Open http://127.0.0.1:5000 in your browser.

New CLI commands (interactive mode)

- `/help` — show available commands.
- `/system <text>` — set a persistent system instruction/personality for the assistant.
- `/read <path>` — read a local file and inject its contents as a `system` message (context injection).
- `/save <filename>` — save the last assistant reply to a file in the current working directory.
- `/genfile <filename> <instruction>` — ask the model to generate the exact content for the requested file and save it locally.

Web UI additions

- Each assistant message has a small "Save to file" form. Enter a filename and the message content will be saved under an `outputs/` folder in the workspace. This is useful for letting the model produce structured outputs (e.g., markdown or JSON) and saving them automatically.

Security and notes

- The `/read` command reads files from the host filesystem; use carefully and avoid injecting very large binaries.
- Saved files are written using safe base filenames (no folders) into the workspace or `outputs/` to avoid directory traversal.
- For production use, add authentication and stricter sanitization.

