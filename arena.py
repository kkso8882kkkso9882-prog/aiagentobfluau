# aiagentobfluau/arena.py

from agents import (
    ObfuscatorAgent,
    DeobfuscatorAgent
)

from evaluator import Evaluator
from scoring import ScoringSystem


class Arena:

    def __init__(self):
        self.obfuscator = ObfuscatorAgent()
        self.deobfuscator = DeobfuscatorAgent()

        self.evaluator = Evaluator()
        self.scoring = ScoringSystem()

        self.round = 0

    def run(self, source: str) -> dict:

        if not isinstance(source, str):
            raise TypeError("source must be a string")

        if not source.strip():
            raise ValueError("source cannot be empty")

        self.round += 1

        # =========================
        # 1. Obfuscator
        # =========================

        obfuscated = self.obfuscator.obfuscate(source)

        obfuscator_success = (
            self.evaluator.check_obfuscation(
                source,
                obfuscated
            )
        )

        # =========================
        # 2. Deobfuscator
        # =========================

        recovered = None
        deobfuscator_success = False

        try:
            recovered = self.deobfuscator.deobfuscate(
                obfuscated
            )

            deobfuscator_success = (
                self.evaluator.check_recovery(
                    source,
                    recovered
                )
            )

        except (TypeError, ValueError):
            deobfuscator_success = False

        # =========================
        # 3. Feedback
        # =========================

        self.obfuscator.learn(
            deobfuscator_success
        )

        self.deobfuscator.learn(
            deobfuscator_success
        )

        # =========================
        # 4. Score
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

            "round": self.round,

            "source": source,

            "obfuscated": obfuscated,

            "recovered": recovered,

            "evaluation": {
                "obfuscator_success":
                    obfuscator_success,

                "deobfuscator_success":
                    deobfuscator_success
            },

            "score": scores,

            "feedback": {
                "obfuscator": {
                    "strategy":
                        self.obfuscator.last_strategy,

                    "deobfuscator_broke_it":
                        deobfuscator_success
                },

                "deobfuscator": {
                    "strategy":
                        self.deobfuscator.last_detected_strategy,

                    "recovery_success":
                        deobfuscator_success
                }
            },

            "learning": {
                "obfuscator_weights":
                    dict(self.obfuscator.weights),

                "deobfuscator_weights":
                    dict(self.deobfuscator.known_strategies)
            }
        }
