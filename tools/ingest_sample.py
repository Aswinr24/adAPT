import json
import sys
from elasticsearch import Elasticsearch, helpers

ELASTIC_URL = "http://localhost:9200"
INDEX_PREFIX = "winlogbeat-test"


def main(path="../samples/sample_events.json"):
    es = Elasticsearch([ELASTIC_URL])
    with open(path, "r") as f:
        docs = json.load(f)

    actions = []
    for i, doc in enumerate(docs):
        actions.append({
            "_index": f"{INDEX_PREFIX}-2025.10.16",
            "_id": i + 1,
            "_source": doc,
        })

    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} documents into {ELASTIC_URL}")


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else "../samples/sample_events.json"
    main(path)
