# Chain Provenance

**Pure Python blockchain-style product provenance and anti-counterfeiting toolkit.**

Generate Merkle roots for product batches, create inclusion proofs, record signed supply-chain events, and verify authenticity in real time. Designed for luxury goods, pharmaceuticals, food, electronics, and logistics companies that need transparent, tamper-evident tracking without running a full blockchain node.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why this exists

Counterfeiting and opaque supply chains cost industries billions annually. Traditional databases can be altered. This toolkit gives you:

- **Merkle-batch registration** — prove an individual item belongs to an authenticated batch with a short cryptographic proof
- **Signed event history** — every shipment, quality check, and sale is cryptographically signed
- **Zero heavy dependencies** for the core engine (stdlib only)
- **CLI + library** — drop into existing systems or run as a standalone service
- **Ready for on-chain anchoring** — export Merkle roots and event hashes to Ethereum, Polygon, or any L2

## Features

- Pure-Python Merkle tree with inclusion proofs
- Product batches with unique item IDs
- Timestamped, signed provenance events
- Full history retrieval and verification
- Exportable state for persistence or blockchain anchoring
- Comprehensive test suite
- CLI for rapid operations

## Quick start

```bash
git clone https://github.com/washington-oyekunle/chain-provenance.git
cd chain-provenance
python -m pip install -e .
python examples/demo.py
```

### CLI examples

```bash
# Create a batch
python -m chain_provenance.cli create-batch \
  --name "Aether Chronograph" \
  --manufacturer "Aether Timeworks" \
  --items WATCH-0001 WATCH-0002 WATCH-0003

# Record an event
python -m chain_provenance.cli add-event \
  --product WATCH-0002 \
  --type shipped \
  --location "Geneva → Accra" \
  --actor "DHL"

# Verify inclusion
python -m chain_provenance.cli verify --product WATCH-0002
```

## Library usage

```python
from chain_provenance import ProvenanceRegistry

registry = ProvenanceRegistry(signing_secret=b"your-secret-key")

batch = registry.create_batch(
    "Luxury Watch",
    "Manufacturer Inc",
    ["SKU-001", "SKU-002", "SKU-003"],
    metadata={"model": "Chrono-X"}
)

event = registry.add_event(
    "SKU-002",
    "quality_checked",
    "Factory Floor",
    "QC Team",
    metadata={"passed": True}
)

result = registry.verify_product_in_batch("SKU-002")
print(result["valid"])  # True
```

## Real-world use cases

- **Luxury goods** — watches, handbags, sneakers: customers scan QR to see full provenance
- **Pharmaceuticals** — track vaccine or drug vials from manufacturer to clinic with temperature events
- **Food & agriculture** — farm-to-table transparency for organic produce or premium coffee
- **Electronics** — component authenticity and warranty tracking
- **Logistics** — multi-party handoff verification without a central trusted database

## Architecture

```
Item IDs → Merkle Tree → Root (anchorable on-chain)
                ↓
         Signed Events (HMAC or ECDSA)
                ↓
      Verification API / QR Codes
```

For production, replace the in-memory registry with SQLite/Postgres and the HMAC signer with ECDSA (via the `cryptography` library) or on-chain signatures.

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## Roadmap

- [ ] Persistent storage (SQLite)
- [ ] QR code generation for consumer verification
- [ ] FastAPI verification service
- [ ] Optional Ethereum anchoring helper
- [ ] ECDSA signature support
- [ ] Web dashboard

## License

MIT
