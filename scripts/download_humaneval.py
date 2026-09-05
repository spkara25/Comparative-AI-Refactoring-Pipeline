import json
import os
import urllib.request

HUMANEVAL_URL = "https://raw.githubusercontent.com/openai/human-eval/master/data/HumanEval.jsonl.gz"

def setup_humaneval_samples(sample_count: int = 5):
    """
    Downloads and extracts sample problems from HumanEval into the dataset folders.
    """
    import gzip
    import io

    os.makedirs("datasets/legacy", exist_ok=True)
    os.makedirs("datasets/tests", exist_ok=True)

    print(f"Downloading HumanEval dataset from {HUMANEVAL_URL}...")
    req = urllib.request.Request(HUMANEVAL_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as response:
        compressed_data = response.read()

    with gzip.GzipFile(fileobj=io.BytesIO(compressed_data)) as gz:
        lines = gz.readlines()

    count = 0
    for line in lines:
        if count >= sample_count:
            break

        data = json.loads(line.decode("utf-8"))
        task_id = data["task_id"].replace("/", "_").lower()  # e.g. openai_humaneval_0
        entry_point = data["entry_point"]
        prompt = data["prompt"]
        canonical_solution = data["canonical_solution"]
        test_code = data["test"]

        # 1. Write the legacy source implementation
        source_path = f"datasets/legacy/{task_id}.py"
        full_code = f"{prompt}{canonical_solution}\n"
        with open(source_path, "w", encoding="utf-8") as f:
            f.write(full_code)

        # 2. Write matching pytest file
        test_path = f"datasets/tests/test_{task_id}.py"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(f"from datasets.legacy.{task_id} import {entry_point}\n\n")
            f.write(test_code + "\n")
            f.write(f"\ndef test_{task_id}_functional():\n    check({entry_point})\n")

        print(f"Extracted: {task_id} -> {source_path}")
        count += 1

    print(f"Successfully extracted {count} HumanEval tasks into datasets/.")

if __name__ == "__main__":
    setup_humaneval_samples(sample_count=5)