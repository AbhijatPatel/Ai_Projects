from flask import Flask, render_template, request, session, redirect, url_for
from dotenv import load_dotenv
import os
import openai


load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

openai.api_key = os.getenv("OPENAI_API_KEY")


def get_response(history, prompt, model="gpt-3.5-turbo", max_tokens=300):
    messages = history + [{"role": "user", "content": prompt}]
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    content = resp.choices[0].message.content.strip()
    return content


@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if prompt:
            history = session.get("history", [])
            try:
                reply = get_response(history, prompt)
                history.append({"role": "user", "content": prompt})
                history.append({"role": "assistant", "content": reply})
                session["history"] = history
            except Exception as e:
                reply = f"API call failed: {e}"
                history.append({"role": "assistant", "content": reply})
                session["history"] = history
        return redirect(url_for("index"))

    history = session.get("history", [])
    return render_template("index.html", history=history)


@app.route("/clear", methods=["POST"])
def clear():
    session.pop("history", None)
    return redirect(url_for("index"))


@app.route("/save", methods=["POST"])
def save():
    content = request.form.get("content", "").strip()
    filename = request.form.get("filename", "").strip()
    if not content or not filename:
        return redirect(url_for("index"))
    safe_name = os.path.basename(filename)
    out_dir = os.path.join(os.getcwd(), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, safe_name)
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        # append confirmation to history
        history = session.get("history", [])
        history.append({"role": "assistant", "content": f"Saved content to {out_path}"})
        session["history"] = history
    except Exception as e:
        history = session.get("history", [])
        history.append({"role": "assistant", "content": f"Failed to save file: {e}"})
        session["history"] = history
    return redirect(url_for("index"))


if __name__ == "__main__":
    if not openai.api_key:
        print("OPENAI_API_KEY not set. See .env.example")
    app.run(host="0.0.0.0", port=5000, debug=True)
