from __future__ import annotations

from src.modeling import bundle_summary_as_json, train_and_save


if __name__ == "__main__":
    bundle = train_and_save(n_samples=1000, random_state=42)
    print("Training completed successfully.")
    print(bundle_summary_as_json(bundle))
