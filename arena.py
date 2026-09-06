# aiagentobfluau/arena.py

from agents import ObfuscatorAgent, DeobfuscatorAgent
from evaluator import Evaluator
from scoring import ScoringSystem


class Arena:
    """ตัวควบคุมการแข่งขันระหว่าง Obfuscator และ Deobfuscator"""

    def __init__(self):
        self.obfuscator = ObfuscatorAgent()
        self.deobfuscator = DeobfuscatorAgent()
        self.evaluator = Evaluator()
        self.scoring = ScoringSystem()

    def run(self, source: str) -> dict:
        if not isinstance(source, str):
            raise TypeError("source must be a string")

        if not source.strip():
            raise ValueError("source cannot be empty")

        # =========================
        # 1. Obfuscator
        # =========================

        obfuscated = self.obfuscator.obfuscate(source)

        # =========================
        # 2. ตรวจการ Obfuscate
        # =========================

        obfuscator_success = self.evaluator.check_obfuscation(
            source,
            obfuscated
        )

        # =========================
        # 3. Deobfuscator
        # =========================

        recovered = None
        deobfuscator_success = False

        try:
            recovered = self.deobfuscator.deobfuscate(
                obfuscated
            )

            deobfuscator_success = self.evaluator.check_recovery(
                source,
                recovered
            )

        except (TypeError, ValueError):
            deobfuscator_success = False

        # =========================
        # 4. คำนวณคะแนน
        # =========================

        scores = self.scoring.calculate(
            obfuscator_success,
            deobfuscator_success
        )

        # =========================
        # 5. Result
        # =========================

        return {
            "success": True,
            "source": source,
            "obfuscated": obfuscated,
            "recovered": recovered,
            "evaluation": {
                "obfuscator_success": obfuscator_success,
                "deobfuscator_success": deobfuscator_success
            },
            "score": scores
        }
