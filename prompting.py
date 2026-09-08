from pathlib import Path
import requests
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--phase", type=str, default="phase2")
parser.add_argument("--input_path", type=str, default="./data/{phase}/input.txt")
parser.add_argument("--prompt_path", type=str, default="./{phase}/prompt/final_prompt.txt")
parser.add_argument("--model", type=str, default="qwen3-30b-a3b-instruct-2507")
parser.add_argument("--output_path", type=str, default="./{phase}/results/{prompt_type}_{model}.ttl")
parser.add_argument("--api_key_path", type=str, default="./archive/apikey.txt")

args = parser.parse_args()

url = "https://chat-ai.academiccloud.de/v1/chat/completions"
model = args.model

input_path = Path(args.input_path.format(phase=args.phase))
prompt_path = Path(args.prompt_path.format(phase=args.phase))
out_path = Path(args.output_path.format(phase=args.phase, model=args.model))

with open(args.api_key_path, "r") as file:
    api_key = file.read().strip()

with open(prompt_path, "r") as file:
    prompt = file.read()

with open(input_path, "r") as file:
    input = file.read()

headers = {
    "Accept": "application/json",
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json",
    "inference-service": "saia-openai-gateway",
}

data = {
    "model": model,
    "messages": [
        {"role": "system", "content": prompt},
        {"role": "user", "content": input},
    ],
    "enable-tools": True,
    "arcana": {
        "id": "jihoo.chung01/nthpda3"
    },
    "temperature": 0.0,
    "top_p": 0.05,
}


try:
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    result = response.json()
    content = result["choices"][0]["message"]["content"]
    out_path.write_text(content, encoding="utf-8")
    print(content)
    print(f"\nSaved to {out_path}")

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP Error: {http_err}")
    print(f"{response.text}")
except Exception as err:
    print(f"Error: {err}")
