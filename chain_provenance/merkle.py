"""
Pure Python Merkle Tree implementation for batch provenance proofs.
Supports efficient inclusion proofs for individual items in a product batch.
"""
from __future__ import annotations

import hashlib
from typing import List, Optional, Tuple


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


class MerkleTree:
    def __init__(self, leaves: List[bytes]):
        if not leaves:
            raise ValueError("Merkle tree requires at least one leaf")
        self.leaves = [sha256(leaf) for leaf in leaves]
        self.layers = self._build_layers(self.leaves)
        self.root = self.layers[-1][0] if self.layers else b""

    def _build_layers(self, leaves: List[bytes]) -> List[List[bytes]]:
        layers = [leaves]
        current = leaves[:]
        while len(current) > 1:
            next_layer = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_layer.append(sha256(left + right))
            layers.append(next_layer)
            current = next_layer
        return layers

    def get_proof(self, index: int) -> List[Tuple[bytes, bool]]:
        """Return list of (sibling_hash, sibling_is_left).
        If sibling_is_left is True, sibling comes first in the hash.
        """
        if index < 0 or index >= len(self.leaves):
            raise IndexError("Leaf index out of range")
        proof = []
        idx = index
        for layer in self.layers[:-1]:
            is_right_child = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right_child else idx + 1
            if sibling_idx >= len(layer):
                sibling_idx = idx
            # sibling_is_left: True if the sibling is the left child (i.e. current is right)
            sibling_is_left = is_right_child
            proof.append((layer[sibling_idx], sibling_is_left))
            idx //= 2
        return proof

    @staticmethod
    def verify_proof(leaf: bytes, proof: List[Tuple[bytes, bool]], root: bytes) -> bool:
        computed = sha256(leaf)
        for sibling, sibling_is_left in proof:
            if sibling_is_left:
                # sibling is left, so hash(sibling + computed)
                computed = sha256(sibling + computed)
            else:
                # sibling is right, so hash(computed + sibling)
                computed = sha256(computed + sibling)
        return computed == root

    def root_hex(self) -> str:
        return self.root.hex()


def generate_batch_root(item_ids: List[str]) -> Tuple[str, MerkleTree]:
    leaves = [item_id.encode("utf-8") for item_id in item_ids]
    tree = MerkleTree(leaves)
    return tree.root_hex(), tree
