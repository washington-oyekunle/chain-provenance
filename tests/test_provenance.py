from chain_provenance.provenance import ProvenanceRegistry


def test_batch_creation_and_verification():
    reg = ProvenanceRegistry(signing_secret=b"test-secret")
    items = ["watch-001", "watch-002", "watch-003"]
    batch = reg.create_batch("Luxury Watch", "Acme Timepieces", items, {"model": "Chrono-X"})
    assert batch.merkle_root
    assert len(batch.item_ids) == 3

    result = reg.verify_product_in_batch("watch-002")
    assert result is not None
    assert result["valid"] is True
    assert result["batch_id"] == batch.batch_id


def test_event_signing_and_history():
    reg = ProvenanceRegistry(signing_secret=b"secure-key")
    reg.create_batch("Vaccine", "PharmaCo", ["vial-1001"])
    event = reg.add_event("vial-1001", "shipped", "Accra Warehouse", "Logistics Partner", {"temp": "2-8C"})
    assert event.signature
    assert event.verify(b"secure-key")

    history = reg.get_product_history("vial-1001")
    assert len(history) == 1
    assert history[0].event_type == "shipped"


def test_unknown_product():
    reg = ProvenanceRegistry()
    assert reg.verify_product_in_batch("nonexistent") is None
    assert reg.get_product_history("nonexistent") == []
