# aiagentobfluau/test_aiagent.py

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
    assert result.startswith("-- AIOBF_LUA_V1\n")


def test_deobfuscator():
    obfuscator = ObfuscatorAgent()
    deobfuscator = DeobfuscatorAgent()

    source = "print('Hello AI')"

    obfuscated = obfuscator.obfuscate(source)
    recovered = deobfuscator.deobfuscate(obfuscated)

    assert recovered == source


def test_evaluator():
    evaluator = Evaluator()

    source = "print('Hello AI')"
    obfuscated = "-- AIOBF_LUA_V1\nSGVsbG8="

    assert evaluator.check_obfuscation(
        source,
        obfuscated
    ) is True

    assert evaluator.check_recovery(
        source,
        source
    ) is True


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
