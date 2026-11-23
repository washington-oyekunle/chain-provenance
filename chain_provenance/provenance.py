"""
Core provenance engine: Products, Batches, Events, and verification.
Uses Merkle trees for efficient batch proofs and HMAC signatures for event integrity.
Production deployments should replace HMAC with proper ECDSA or on-chain anchoring.
"""
from __future__ import annotations

import hmac
import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from .merkle import MerkleTree, generate_batch_root


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ProvenanceEvent:
    event_id: str
    product_id: str
    event_type: str  # e.g. "manufactured", "shipped", "received", "sold", "verified"
    location: str
    actor: str  # company or person identifier
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def sign(self, secret: bytes) -> str:
        payload = json.dumps(
            {
                "event_id": self.event_id,
                "product_id": self.product_id,
                "event_type": self.event_type,
                "location": self.location,
                "actor": self.actor,
                "timestamp": self.timestamp,
                "metadata": self.metadata,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.signature = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return self.signature

    def verify(self, secret: bytes) -> bool:
        if not self.signature:
            return False
        payload = json.dumps(
            {
                "event_id": self.event_id,
                "product_id": self.product_id,
                "event_type": self.event_type,
                "location": self.location,
                "actor": self.actor,
                "timestamp": self.timestamp,
                "metadata": self.metadata,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        expected = hmac.new(secret, payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.signature)


@dataclass
class ProductBatch:
    batch_id: str
    product_name: str
    manufacturer: str
    item_ids: List[str]
    merkle_root: str
    created_at: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProvenanceRegistry:
    """
    In-memory or file-backed registry for products, batches, and events.
    Suitable for demos, local testing, and as a reference implementation.
    """

    def __init__(self, signing_secret: Optional[bytes] = None):
        self.signing_secret = signing_secret or b"default-demo-secret-change-me"
        self.batches: Dict[str, ProductBatch] = {}
        self.products: Dict[str, Dict[str, Any]] = {}  # product_id -> {batch_id, events: []}
        self.events: Dict[str, ProvenanceEvent] = {}

    def create_batch(
        self,
        product_name: str,
        manufacturer: str,
        item_ids: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProductBatch:
        if not item_ids:
            raise ValueError("Batch must contain at least one item")
        root, tree = generate_batch_root(item_ids)
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        batch = ProductBatch(
            batch_id=batch_id,
            product_name=product_name,
            manufacturer=manufacturer,
            item_ids=item_ids,
            merkle_root=root,
            created_at=utc_now(),
            metadata=metadata or {},
        )
        self.batches[batch_id] = batch
        for item_id in item_ids:
            self.products[item_id] = {"batch_id": batch_id, "events": []}
        return batch

    def add_event(
        self,
        product_id: str,
        event_type: str,
        location: str,
        actor: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProvenanceEvent:
        if product_id not in self.products:
            raise ValueError(f"Unknown product_id: {product_id}")
        event = ProvenanceEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            product_id=product_id,
            event_type=event_type,
            location=location,
            actor=actor,
            timestamp=utc_now(),
            metadata=metadata or {},
        )
        event.sign(self.signing_secret)
        self.events[event.event_id] = event
        self.products[product_id]["events"].append(event.event_id)
        return event

    def get_product_history(self, product_id: str) -> List[ProvenanceEvent]:
        if product_id not in self.products:
            return []
        return [self.events[eid] for eid in self.products[product_id]["events"]]

    def verify_product_in_batch(self, product_id: str) -> Optional[Dict[str, Any]]:
        if product_id not in self.products:
            return None
        batch_id = self.products[product_id]["batch_id"]
        batch = self.batches.get(batch_id)
        if not batch:
            return None
        try:
            index = batch.item_ids.index(product_id)
        except ValueError:
            return None
        leaves = [iid.encode("utf-8") for iid in batch.item_ids]
        tree = MerkleTree(leaves)
        proof = tree.get_proof(index)
        is_valid = MerkleTree.verify_proof(product_id.encode("utf-8"), proof, bytes.fromhex(batch.merkle_root))
        return {
            "valid": is_valid,
            "batch_id": batch_id,
            "merkle_root": batch.merkle_root,
            "proof_length": len(proof),
            "batch": batch.to_dict(),
        }

    def export_state(self) -> Dict[str, Any]:
        return {
            "batches": {bid: b.to_dict() for bid, b in self.batches.items()},
            "products": self.products,
            "events": {eid: e.to_dict() for eid, e in self.events.items()},
        }
