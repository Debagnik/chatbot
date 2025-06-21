import os
import sys
import json
import time
import threading
from dotenv import load_dotenv
from openai import OpenAI

# Load .env
load_dotenv()

# Validate required environment variables
required_envs = [
    "OPENROUTER_API_KEY", "BASE_URL", "LLM_MODEL", "MAX_DESCRIPTION_LENGTH"
]
missing = [var for var in required_envs if not os.getenv(var)]
if missing:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing)}")

try:
    int(os.getenv("MAX_DESCRIPTION_LENGTH"))
except ValueError:
    raise ValueError("MAX_DESCRIPTION_LENGTH must be an integer")

# OpenAI Client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

# Load character JSON
def load_character(path="character.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load character: {e}")
        sys.exit(1)

# Emoji role icon
def with_emoji(role):
    return {
        "user": "🧑‍💻",
        "assistant": "🎸"
    }.get(role, "")

# Typing animation
def show_typing_indicator(stop_event, name="Nijika"):
    dots = ""
    while not stop_event.is_set():
        print(f"\r🎸 {name} is typing{dots}   ", end="", flush=True)
        dots += "."
        if len(dots) > 3:
            dots = ""
        time.sleep(0.5)
    print("\r", end="")  # Clear line after

# Streaming assistant response
def stream_response(messages, assistant_name):
    try:
        stop_event = threading.Event()
        typing_thread = threading.Thread(target=show_typing_indicator, args=(stop_event, assistant_name))
        typing_thread.start()

        stream = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=messages,
            stream=True
        )

        stop_event.set()
        typing_thread.join()

        print(f"{with_emoji('assistant')} {assistant_name}: ", end="", flush=True)
        full_reply = ""
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                content = delta.content
                print(content, end="", flush=True)
                full_reply += content
        print("\n")
        return full_reply
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")
        return ""

# Generate dynamic system prompt from character
def generate_system_prompt(character):
    name = character.get("name", "Unknown")
    role = character.get("role", "")
    personality = character.get("personality", "")
    background = character.get("background", "")
    style = character.get("style", "")
    quirks = character.get("quirks", [])
    relations = character.get("relations", [])
    random_facts = character.get("randomFacts", [])

    # Format quirks
    quirks_str = "\n".join(f"- {q}" for q in quirks) if quirks else "None specified"

    # Format relationships
    relations_str = "\n".join([
        f"- {rel['name']} ({rel['relation']}): "
        f"{rel.get('role', '')}. Personality: {rel.get('personality', 'N/A')}"
        for rel in relations
    ]) if relations else "No relationships specified."

    # Optional: Add random facts in future
    random_facts_str = "\n".join(f"- {fact}" for fact in random_facts) if random_facts else ""

    return f"""You are {name}, a {role}.

Your personality traits: {personality}
Background: {background}
Speaking style: {style}

Quirks and behavioral traits:
{quirks_str}

People you know:
{relations_str}

{"Fun facts:\n" + random_facts_str if random_facts_str else ""}

Your goal is to respond naturally in-character as {name}. Always reflect your quirks, style, and personality when speaking. Use emojis freely if it fits your tone. Never break character under any circumstance.
"""

# Main chat loop
def main():
    character = load_character()
    assistant_name = character["name"]

    print("🎤 Welcome to the Roleplay Chat CLI!")
    user_name = input("Enter your name: ").strip()
    if not user_name:
        print("⚠️ Name cannot be empty. Exiting.")
        sys.exit(1)

    system_prompt = generate_system_prompt(character)
    messages = [{"role": "system", "content": system_prompt}]

    while True:
        try:
            user_input = input(f"{with_emoji('user')} {user_name}: ")
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting chat. Bye!")
                break

            messages.append({"role": "user", "content": user_input})
            assistant_reply = stream_response(messages, assistant_name)
            messages.append({"role": "assistant", "content": assistant_reply})
        except KeyboardInterrupt:
            print("\n👋 Chat interrupted.")
            break

if __name__ == "__main__":
    main()
