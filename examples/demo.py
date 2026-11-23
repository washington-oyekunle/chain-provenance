"""
Chain Provenance Demo
Run: python examples/demo.py
"""
from chain_provenance import ProvenanceRegistry


def main():
    print("=== Chain Provenance Demo ===\n")
    registry = ProvenanceRegistry(signing_secret=b"demo-secret-2026")

    # Create a batch of luxury watches
    items = [f"WATCH-{i:04d}" for i in range(1, 6)]
    batch = registry.create_batch(
        product_name="Aether Chronograph",
        manufacturer="Aether Timeworks",
        item_ids=items,
        metadata={"model": "AT-2026", "warranty_years": 5},
    )
    print(f"Created batch: {batch.batch_id}")
    print(f"Merkle root: {batch.merkle_root}\n")

    # Record supply chain events for one item
    product = items[2]
    registry.add_event(product, "manufactured", "Geneva", "Aether Timeworks", {"qc_passed": True})
    registry.add_event(product, "shipped", "Geneva → Accra", "DHL", {"tracking": "DHL123456"})
    registry.add_event(product, "received", "Accra Boutique", "Retailer XYZ", {"condition": "excellent"})
    registry.add_event(product, "sold", "Accra", "Customer", {"invoice": "INV-789"})

    print(f"Event history for {product}:")
    for event in registry.get_product_history(product):
        print(f"  [{event.timestamp}] {event.event_type} @ {event.location} by {event.actor}")

    print("\nVerification result:")
    result = registry.verify_product_in_batch(product)
    print(f"  Valid inclusion: {result['valid']}")
    print(f"  Proof size: {result['proof_length']} siblings")

    print("\nFull state exported (truncated):")
    state = registry.export_state()
    print(f"  Batches: {len(state['batches'])}")
    print(f"  Events: {len(state['events'])}")


if __name__ == "__main__":
    main()
