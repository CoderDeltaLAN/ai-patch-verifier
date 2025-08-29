# ai-patch-verifier — AI Patch Verifier
# Source: https://github.com/CoderDeltaLAN/ai-patch-verifier
# License: MIT
import random

from ai_patch_verifier.core import compute_trust_score


def test_empty_diff_score_base():
    r = compute_trust_score("")
    assert r["score"] == 70 and r["reasons"] == []


def test_only_todo_penalizes():
    r = compute_trust_score("TODO: later")
    assert r["score"] == 60 and "TODO" in " ".join(r["reasons"])


def test_only_binary_penalizes():
    r = compute_trust_score("Binary files a/b differ")
    assert r["score"] == 60 and "binarios" in " ".join(r["reasons"])


def test_tests_plus_todo_net_zero():
    r = compute_trust_score("+ def test_x():\n+  assert True\nTODO")
    assert r["score"] == 70


def test_bounds_0_100_stable():
    # in esta heurística actual, score no excede [0,100]
    payload = "TODO\n" * 100 + "Binary files a/b differ\n" * 100
    r = compute_trust_score(payload)
    assert 0 <= r["score"] <= 100


def test_random_inputs_are_bounded():
    random.seed(1234)
    for _ in range(50):
        s = "".join(chr(random.randint(32, 126)) for _ in range(200))
        r = compute_trust_score(s)
        assert 0 <= r["score"] <= 100
