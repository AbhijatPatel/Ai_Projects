from dotenv import load_dotenv
import os
import sys
import argparse
import openai


def get_response(history, prompt, model="gpt-3.5-turbo", max_tokens=300):
    messages = history + [{"role": "user", "content": prompt}]
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    content = resp.choices[0].message.content.strip()
    return content


def interactive_loop():
    history = []
    print("Interactive chat. Type 'exit' to quit. Type '/help' for commands.")
    while True:
        try:
            prompt = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not prompt:
            continue
        cmd = prompt.strip()
        if cmd.lower() == "exit":
            break
        if cmd.startswith("/"):
            parts = cmd.split(" ", 2)
            command = parts[0].lower()
            if command == "/help":
                print("Commands:\n  /help\n  /system <text>  - set system instruction\n  /read <path>    - read local file and inject as system context\n  /save <filename> - save last assistant reply to file\n  /genfile <filename> <instruction> - ask model to generate file content and save it")
                continue
            if command == "/system":
                if len(parts) < 2:
                    print("Usage: /system <text>")
                    continue
                sys_msg = parts[1] if len(parts) == 2 else parts[1] + (" " + parts[2] if len(parts) > 2 else "")
                history.insert(0, {"role": "system", "content": sys_msg})
                print("System instruction set.")
                continue
            if command == "/read":
                if len(parts) < 2:
                    print("Usage: /read <path>")
                    continue
                path = parts[1]
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = f.read()
                    ctx = f"Context from file {path}:\n" + data
                    history.insert(0, {"role": "system", "content": ctx})
                    print(f"Injected context from {path} as system message.")
                except Exception as e:
                    print("Failed to read file:", e)
                continue
            if command == "/save":
                if len(parts) < 2:
                    print("Usage: /save <filename>")
                    continue
                filename = parts[1]
                # find last assistant reply
                last = None
                for m in reversed(history):
                    if m.get("role") == "assistant":
                        last = m.get("content")
                        break
                if not last:
                    print("No assistant reply found to save.")
                    continue
                safe_name = os.path.basename(filename)
                out_path = os.path.join(os.getcwd(), safe_name)
                try:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(last)
                    print(f"Saved assistant reply to {out_path}")
                except Exception as e:
                    print("Failed to save file:", e)
                continue
            if command == "/genfile":
                if len(parts) < 3:
                    print("Usage: /genfile <filename> <instruction>")
                    continue
                filename = parts[1]
                instruction = parts[2]
                # Ask model to output only the file content
                gen_prompt = f"Produce the exact content for the file named {filename}. Respond with the file content only, no commentary. Instruction: {instruction}"
                try:
                    reply = get_response(history, gen_prompt)
                    safe_name = os.path.basename(filename)
                    out_path = os.path.join(os.getcwd(), safe_name)
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(reply)
                    # append to history
                    history.append({"role": "assistant", "content": reply})
                    print(f"Generated and saved {out_path}")
                except Exception as e:
                    print("Failed to generate or save file:", e)
                continue
            print("Unknown command. Type /help for commands.")
            continue
        try:
            assistant_reply = get_response(history, prompt)
            history.append({"role": "user", "content": prompt})
            history.append({"role": "assistant", "content": assistant_reply})
            print("\nAssistant:\n" + assistant_reply + "\n")
        except Exception as e:
            print("API call failed:", e)


def run_once(prompt):
    history = []
    try:
        reply = get_response(history, prompt)
        print(reply)
    except Exception as e:
        print("API call failed:", e)


def main():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set. Copy .env.example to .env and set your key.")
        sys.exit(1)

    openai.api_key = api_key

    parser = argparse.ArgumentParser(description="Simple AI assistant")
    parser.add_argument("--mode", choices=["interactive", "once"], default="interactive")
    parser.add_argument("--prompt", type=str, help="Prompt to send in 'once' mode")
    args = parser.parse_args()

    if args.mode == "interactive":
        interactive_loop()
    else:
        if not args.prompt:
            print("Provide --prompt when using --mode once")
            sys.exit(1)
        run_once(args.prompt)


if __name__ == "__main__":
    main()
