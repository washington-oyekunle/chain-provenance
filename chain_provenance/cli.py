"""
Command-line interface for the Chain Provenance toolkit.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from .provenance import ProvenanceRegistry


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Chain Provenance — blockchain-style product tracking and anti-counterfeiting"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # create-batch
    p_create = sub.add_parser("create-batch", help="Register a new product batch with Merkle root")
    p_create.add_argument("--name", required=True, help="Product name")
    p_create.add_argument("--manufacturer", required=True)
    p_create.add_argument("--items", required=True, nargs="+", help="List of unique item IDs")
    p_create.add_argument("--metadata", default="{}", help="JSON metadata")

    # add-event
    p_event = sub.add_parser("add-event", help="Record a supply-chain event for a product")
    p_event.add_argument("--product", required=True)
    p_event.add_argument("--type", required=True, dest="event_type")
    p_event.add_argument("--location", required=True)
    p_event.add_argument("--actor", required=True)
    p_event.add_argument("--metadata", default="{}")

    # verify
    p_verify = sub.add_parser("verify", help="Verify a product belongs to its registered batch")
    p_verify.add_argument("--product", required=True)

    # history
    p_hist = sub.add_parser("history", help="Show full event history for a product")
    p_hist.add_argument("--product", required=True)

    args = parser.parse_args(argv)
    registry = ProvenanceRegistry()  # In real use, load from file/DB

    if args.command == "create-batch":
        meta = json.loads(args.metadata)
        batch = registry.create_batch(args.name, args.manufacturer, args.items, meta)
        print(json.dumps(batch.to_dict(), indent=2))
        print(f"\nMerkle root: {batch.merkle_root}")
        print(f"Batch ID: {batch.batch_id}")

    elif args.command == "add-event":
        meta = json.loads(args.metadata)
        event = registry.add_event(args.product, args.event_type, args.location, args.actor, meta)
        print(json.dumps(event.to_dict(), indent=2))

    elif args.command == "verify":
        result = registry.verify_product_in_batch(args.product)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print("Product not found or invalid", file=sys.stderr)
            sys.exit(1)

    elif args.command == "history":
        events = registry.get_product_history(args.product)
        print(json.dumps([e.to_dict() for e in events], indent=2))


if __name__ == "__main__":
    main()
