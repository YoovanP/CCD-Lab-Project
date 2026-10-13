"""Download the pinned model once; fail visibly rather than substituting fake output."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Settings
from app.inference import SentimentModel, download_assets
from app.model_registry import SENTIMENT


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="Run real positive/negative checks")
    args = parser.parse_args()
    settings = Settings()
    try:
        assets = download_assets(SENTIMENT, settings)
        print(f"Model: {SENTIMENT.source}")
        print(f"Revision: {SENTIMENT.revision}")
        print(f"Asset bytes: {sum(p.stat().st_size for p in assets.values())}")
        if args.verify:
            model = SentimentModel(SENTIMENT, settings)
            model.load()
            for text, expected in (
                ("I love this product. It is absolutely wonderful!", "positive"),
                ("I hate this product. It is terrible and disappointing.", "negative"),
            ):
                result = model.predict(text)
                print(json.dumps(result.__dict__))
                if result.label != expected:
                    raise RuntimeError(f"Demo prediction did not match expected {expected}")
            model.close()
        print("PASS: pinned model assets are available.")
        return 0
    except Exception as exc:
        print(f"FAIL: model preparation ({type(exc).__name__}). Check network/cache and docs/PHASE_1.md.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
