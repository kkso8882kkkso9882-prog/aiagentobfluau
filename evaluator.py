import json


class Evaluator:

    OBF_PREFIX = "-- AIOBF_CHUNK_V1\n"

    def check_obfuscation(
        self,
        original,
        obfuscated
    ):
        if not isinstance(original, str):
            return False

        if not isinstance(obfuscated, str):
            return False

        if not original.strip():
            return False

        if not obfuscated.startswith(self.OBF_PREFIX):
            return False

        payload = obfuscated[len(self.OBF_PREFIX):]

        try:
            plan = json.loads(payload)
        except json.JSONDecodeError:
            return False

        if not isinstance(plan, dict):
            return False

        if plan.get("version") != 1:
            return False

        chunks = plan.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            return False

        for c in chunks:
            if not isinstance(c, dict):
                return False
            if "i" not in c or "len" not in c or "op" not in c or "data" not in c:
                return False
            if not isinstance(c["i"], int):
                return False
            if not isinstance(c["len"], int) or c["len"] < 1:
                return False
            if c["op"] not in ("base64", "hex", "reverse"):
                return False
            if not isinstance(c["data"], str) or not c["data"]:
                return False

        n = len(chunks)
        indices = [c["i"] for c in chunks]
        if sorted(indices) != list(range(n)):
            return False

        return obfuscated != original

    def check_recovery(
        self,
        original,
        recovered
    ):
        if not isinstance(original, str):
            return False

        if not isinstance(recovered, str):
            return False

        return (
            original.strip()
            == recovered.strip()
        )

    def evaluate(
        self,
        original,
        obfuscated,
        recovered
    ):
        obfuscator_success = (
            self.check_obfuscation(
                original,
                obfuscated
            )
        )

        deobfuscator_success = (
            self.check_recovery(
                original,
                recovered
            )
        )

        return {
            "obfuscator_success":
                obfuscator_success,

            "deobfuscator_success":
                deobfuscator_success,

            "overall_success":
                (
                    obfuscator_success
                    and deobfuscator_success
                )
        }
