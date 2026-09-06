# aiagentobfluau/evaluator.py

class Evaluator:
    """
    ตรวจสอบผลลัพธ์ของ Obfuscator และ Deobfuscator
    โดยไม่ execute Lua
    """

    OBF_PREFIX = "-- AIOBF_LUA_V1\n"

    def check_obfuscation(self, original: str, obfuscated: str) -> bool:
        if not isinstance(original, str):
            return False

        if not isinstance(obfuscated, str):
            return False

        if not original.strip():
            return False

        if not obfuscated.startswith(self.OBF_PREFIX):
            return False

        payload = obfuscated[len(self.OBF_PREFIX):]

        # ต้องมีข้อมูลหลัง prefix
        if not payload.strip():
            return False

        # ผลลัพธ์ต้องแตกต่างจาก source เดิม
        if obfuscated == original:
            return False

        return True

    def check_recovery(self, original: str, recovered: str) -> bool:
        if not isinstance(original, str):
            return False

        if not isinstance(recovered, str):
            return False

        return original.strip() == recovered.strip()

    def evaluate(
        self,
        original: str,
        obfuscated: str,
        recovered: str
    ) -> dict:
        obfuscator_success = self.check_obfuscation(
            original,
            obfuscated
        )

        deobfuscator_success = self.check_recovery(
            original,
            recovered
        )

        return {
            "obfuscator_success": obfuscator_success,
            "deobfuscator_success": deobfuscator_success,
            "overall_success": (
                obfuscator_success
                and deobfuscator_success
            )
        }
