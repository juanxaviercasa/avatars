"""Offline composition only. No cloud API calls or Kaggle submissions."""
import argparse
import json
from pathlib import Path

from .db import store
from .models import Variant
from .production import ProductionPolicy, plan_variant, provider_catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("providers")
    plan = sub.add_parser("plan")
    plan.add_argument("variant_id")
    compose = sub.add_parser("compose")
    compose.add_argument("variant_id")
    compose.add_argument("bundle", type=Path)
    compose.add_argument("--no-hyperframes", action="store_true")
    args = parser.parse_args()
    if args.command == "providers":
        result = provider_catalog()
    elif args.command == "plan":
        result = plan_variant(args.variant_id)
    else:
        from .precomputed_avatar import compose_bundle
        v = store().get("variants", args.variant_id, Variant)
        if not v:
            parser.error("Variante inexistente")
        policy = ProductionPolicy(export_hyperframes=not args.no_hyperframes)
        report = plan_variant(v.id, policy)
        if report["blockers"]:
            parser.error("; ".join(report["blockers"]))
        out = compose_bundle(args.bundle, v.persona_id, source_variant_id=v.id, production_policy=policy)
        result = {"variant_id": out.id, "status": out.status, "duration": out.duration,
                  "output_directory": str(Path(out.video_path).parent), "generation_started": False}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
