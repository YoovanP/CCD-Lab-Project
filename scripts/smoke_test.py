"""Run Phase 1 acceptance checks against a live HTTP server (standard library only)."""
import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    def call(path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = Request(base + path, data=data,
                          headers={"Content-Type": "application/json"} if data else {})
        try:
            with urlopen(request, timeout=30) as response:
                return response.status, json.loads(response.read())
        except HTTPError as exc:
            return exc.code, json.loads(exc.read())

    try:
        for path in ("/health/live", "/health/ready", "/api/models", "/api/models/sentiment"):
            status, _ = call(path)
            if status != 200:
                raise RuntimeError(f"{path}: expected 200, got {status}")
            print(f"PASS: {path}")
        for text, expected in (
            ("I love this product. It is absolutely wonderful!", "positive"),
            ("I hate this product. It is terrible and disappointing.", "negative"),
        ):
            status, body = call("/api/inference", {"model": "sentiment", "input": text})
            if status != 200 or body.get("prediction") != expected:
                raise RuntimeError(f"Real {expected} prediction failed: {status}")
            if not (0 <= body["confidence"] <= 1 and body["processing_time_ms"] > 0):
                raise RuntimeError("Invalid prediction score or measured timing")
            print(f"PASS: real {expected} prediction")
            print(json.dumps(body))
        for request_body, expected in (
            ({"model": "unknown", "input": "hello"}, 404),
            ({"model": "sentiment", "input": ""}, 422),
            ({"model": "sentiment", "input": " \t"}, 422),
            ({"model": "sentiment"}, 422),
            ({"model": "sentiment", "input": "x" * 2001}, 422),
        ):
            status, _ = call("/api/inference", request_body)
            if status != expected:
                raise RuntimeError(f"Validation: expected {expected}, got {status}")
            print(f"PASS: error status {expected}")
        print("PASS: Phase 1 live HTTP acceptance checks.")
        return 0
    except (URLError, OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"FAIL: {exc}. Check server startup and docs/PHASE_1.md.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
