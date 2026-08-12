"""Run retrieval evaluation against a running API; reports only measured metrics."""
import json
from pathlib import Path
def main():
 rows=[json.loads(x) for x in Path("evaluation/dataset.jsonl").read_text().splitlines()]
 print(f"Loaded {len(rows)} labeled queries. Configure credentials and API calls before measurement.")
if __name__=="__main__": main()
