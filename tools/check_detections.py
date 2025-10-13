import glob
import json
from elasticsearch import Elasticsearch

ES = Elasticsearch(["http://localhost:9200"])


def load_detection(path):
    with open(path, "r") as f:
        return json.load(f)


def run_detection(det):
    index = det.get("index", "*")
    query = det.get("query", {"match_all": {}})
    res = ES.count(index=index, body={"query": query})
    return res.get('count', 0)


if __name__ == '__main__':
    for path in glob.glob("../detections/*.json"):
        det = load_detection(path)
        count = run_detection(det)
        print(f"{det.get('title')} -> {count} hits")
