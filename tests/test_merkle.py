import pytest
from chain_provenance.merkle import MerkleTree, generate_batch_root


def test_merkle_root_consistency():
    items = ["item001", "item002", "item003", "item004"]
    root1, tree1 = generate_batch_root(items)
    root2, tree2 = generate_batch_root(items)
    assert root1 == root2
    assert tree1.root == tree2.root


def test_proof_verification_valid():
    items = [f"sku-{i:04d}" for i in range(8)]
    root, tree = generate_batch_root(items)
    for idx, item in enumerate(items):
        proof = tree.get_proof(idx)
        assert MerkleTree.verify_proof(item.encode(), proof, bytes.fromhex(root))


def test_proof_verification_invalid():
    items = ["a", "b", "c"]
    root, tree = generate_batch_root(items)
    proof = tree.get_proof(0)
    # Tamper with leaf
    assert not MerkleTree.verify_proof(b"tampered", proof, bytes.fromhex(root))


def test_single_leaf():
    root, tree = generate_batch_root(["only-one"])
    proof = tree.get_proof(0)
    assert MerkleTree.verify_proof(b"only-one", proof, bytes.fromhex(root))
