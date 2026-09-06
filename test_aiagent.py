# aiagentobfluau/test_aiagent.py

import json
import base64

from arena import Arena
from agents import ObfuscatorAgent, DeobfuscatorAgent
from evaluator import Evaluator
from scoring import ScoringSystem


def test_obfuscator():
    agent = ObfuscatorAgent()

    source = "print('Hello AI')"
    result = agent.obfuscate(source)

    assert isinstance(result, str)
    assert result != source
    assert result.startswith("-- AIOBF_CHUNK_V1\n")

    payload = result[len("-- AIOBF_CHUNK_V1\n"):]
    plan = json.loads(payload)
    assert plan["version"] == 1
    assert isinstance(plan["chunks"], list)
    assert len(plan["chunks"]) >= 1


def test_deobfuscator_roundtrip():
    obfuscator = ObfuscatorAgent()
    deobfuscator = DeobfuscatorAgent()

    source = "print('Hello AI')"

    obfuscated = obfuscator.obfuscate(source)
    recovered = deobfuscator.deobfuscate(obfuscated)

    assert recovered == source


def test_basic_chunk_roundtrip():
    obfuscator = ObfuscatorAgent()
    deobfuscator = DeobfuscatorAgent()

    source = "abc"
    assert deobfuscator.deobfuscate(
        obfuscator.obfuscate(source)
    ) == source


def test_multi_chunk_source():
    obfuscator = ObfuscatorAgent()
    deobfuscator = DeobfuscatorAgent()

    # Long enough to force multiple chunks (max 12 chars)
    source = "A" * 50
    obfuscated = obfuscator.obfuscate(source)
    plan = json.loads(obfuscated.split("\n", 1)[1])
    assert len(plan["chunks"]) >= 5
    assert deobfuscator.deobfuscate(obfuscated) == source


def test_mixed_operations():
    obfuscator = ObfuscatorAgent()
    deobfuscator = DeobfuscatorAgent()

    source = "mixed ops test 12345"
    # Run several times to likely hit mixed ops
    for _ in range(10):
        obfuscated = obfuscator.obfuscate(source)
        recovered = deobfuscator.deobfuscate(obfuscated)
        assert recovered == source
        plan = json.loads(obfuscated.split("\n", 1)[1])
        ops = {c["op"] for c in plan["chunks"]}
        # At least one valid op always present
        assert ops.issubset({"base64", "hex", "reverse"})


def test_invalid_chunk_index():
    deobfuscator = DeobfuscatorAgent()

    bad = {
        "version": 1,
        "chunks": [
            {"i": 0, "len": 1, "op": "reverse", "data": "a"},
            {"i": 2, "len": 1, "op": "reverse", "data": "b"},  # missing 1
        ],
    }
    payload = "-- AIOBF_CHUNK_V1\n" + json.dumps(bad)

    try:
        deobfuscator.deobfuscate(payload)
        assert False, "should have raised"
    except ValueError:
        assert True


def test_invalid_operation():
    deobfuscator = DeobfuscatorAgent()

    bad = {
        "version": 1,
        "chunks": [
            {"i": 0, "len": 1, "op": "rot13", "data": "a"},
        ],
    }
    payload = "-- AIOBF_CHUNK_V1\n" + json.dumps(bad)

    try:
        deobfuscator.deobfuscate(payload)
        assert False, "should have raised"
    except ValueError:
        assert True


def test_invalid_encoded_data():
    deobfuscator = DeobfuscatorAgent()

    bad = {
        "version": 1,
        "chunks": [
            {"i": 0, "len": 1, "op": "base64", "data": "!!!not-b64!!!"},
        ],
    }
    payload = "-- AIOBF_CHUNK_V1\n" + json.dumps(bad)

    try:
        deobfuscator.deobfuscate(payload)
        assert False, "should have raised"
    except ValueError:
        assert True


def test_invalid_chunk_length():
    deobfuscator = DeobfuscatorAgent()

    # reverse of "ab" is "ba", but claim len=1
    bad = {
        "version": 1,
        "chunks": [
            {"i": 0, "len": 1, "op": "reverse", "data": "ba"},
        ],
    }
    payload = "-- AIOBF_CHUNK_V1\n" + json.dumps(bad)

    try:
        deobfuscator.deobfuscate(payload)
        assert False, "should have raised"
    except ValueError:
        assert True


def test_evaluator():
    evaluator = Evaluator()

    source = "print('Hello AI')"
    obfuscator = ObfuscatorAgent()
    obfuscated = obfuscator.obfuscate(source)

    assert evaluator.check_obfuscation(
        source,
        obfuscated
    ) is True

    assert evaluator.check_recovery(
        source,
        source
    ) is True

    # Wrong prefix
    assert evaluator.check_obfuscation(
        source,
        "-- AIOBF_PIPE_V1\nfoo"
    ) is False


def test_scoring():
    scoring = ScoringSystem()

    # Obfuscator สำเร็จ / Deobfuscator ล้มเหลว
    result = scoring.calculate(True, False)

    assert result == {
        "obfuscator": 3,
        "deobfuscator": 0
    }

    # ทั้งคู่สำเร็จ
    result = scoring.calculate(True, True)

    assert result == {
        "obfuscator": 1,
        "deobfuscator": 3
    }

    # ทั้งคู่ล้มเหลว
    result = scoring.calculate(False, False)

    assert result == {
        "obfuscator": 0,
        "deobfuscator": 0
    }


def test_arena():
    arena = Arena()

    source = "print('Hello AI Arena')"

    result = arena.run(source)

    assert result["success"] is True
    assert result["evaluation"]["obfuscator_success"] is True
    assert result["evaluation"]["deobfuscator_success"] is True

    assert result["score"] == {
        "obfuscator": 1,
        "deobfuscator": 3
    }


def test_empty_source():
    arena = Arena()

    try:
        arena.run("")
        assert False
    except ValueError:
        assert True


def test_invalid_source_type():
    arena = Arena()

    try:
        arena.run(None)
        assert False
    except TypeError:
        assert True


def test_api_health():
    from app import app

    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/health")

        assert response.status_code == 200

        data = response.get_json()

        assert data["status"] == "ok"
        assert data["project"] == "aiagentobfluau"


def test_api_run():
    from app import app

    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/arena/run",
            json={
                "source": "print('Hello API')"
            }
        )

        assert response.status_code == 200

        data = response.get_json()

        assert data["success"] is True
        assert data["score"] == {
            "obfuscator": 1,
            "deobfuscator": 3
        }


def test_api_rejects_empty_source():
    from app import app

    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/arena/run",
            json={
                "source": ""
            }
        )

        assert response.status_code == 400


def test_api_rejects_missing_source():
    from app import app

    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.post(
            "/arena/run",
            json={}
        )

        assert response.status_code == 400


def test_dashboard_attrs():
    from app import app

    app.config["TESTING"] = True

    with app.test_client() as client:
        # Run one round so last_plan exists
        client.post(
            "/arena/run",
            json={"source": "dashboard test"}
        )

        response = client.get("/arena/dashboard")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert "strategy" in data
        assert "weights" in data
        assert "obfuscator" in data["weights"]
        assert "deobfuscator" in data["weights"]
