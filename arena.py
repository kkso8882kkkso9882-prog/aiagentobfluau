import binascii
import json

from agents import (
    ObfuscatorAgent,
    DeobfuscatorAgent
)

from evaluator import Evaluator
from scoring import ScoringSystem


class Arena:

    def __init__(self):

        self.obfuscator = (
            ObfuscatorAgent()
        )

        self.deobfuscator = (
            DeobfuscatorAgent()
        )

        self.evaluator = Evaluator()
        self.scoring = ScoringSystem()

        self.round = 0

    def run(self, source):

        if not isinstance(source, str):
            raise TypeError(
                "source must be a string"
            )

        if not source.strip():
            raise ValueError(
                "source cannot be empty"
            )

        self.round += 1

        obfuscated = (
            self.obfuscator.obfuscate(
                source
            )
        )

        obfuscator_success = (
            self.evaluator.check_obfuscation(
                source,
                obfuscated
            )
        )

        recovered = None
        deobfuscator_success = False

        try:

            recovered = (
                self.deobfuscator.deobfuscate(
                    obfuscated
                )
            )

            deobfuscator_success = (
                self.evaluator.check_recovery(
                    source,
                    recovered
                )
            )

        except (
            TypeError,
            ValueError,
            UnicodeDecodeError,
            binascii.Error,
            json.JSONDecodeError,
        ):
            deobfuscator_success = False

        self.obfuscator.learn(
            deobfuscator_success
        )

        self.deobfuscator.learn(
            deobfuscator_success
        )

        scores = self.scoring.calculate(
            obfuscator_success,
            deobfuscator_success
        )

        def _plan_summary(plan):
            if plan is None:
                return None
            chunks = plan.get("chunks") or []
            ops = [c.get("op") for c in chunks]
            return {
                "version": plan.get("version"),
                "num_chunks": len(chunks),
                "operations": ops,
            }

        return {

            "success": True,

            "round":
                self.round,

            "source":
                source,

            "obfuscated":
                obfuscated,

            "recovered":
                recovered,

            "evaluation": {

                "obfuscator_success":
                    obfuscator_success,

                "deobfuscator_success":
                    deobfuscator_success
            },

            "score":
                scores,

            "feedback": {

                "obfuscator": {

                    "plan":
                        _plan_summary(
                            self.obfuscator.last_plan
                        ),

                    "deobfuscator_broke_it":
                        deobfuscator_success
                },

                "deobfuscator": {

                    "plan":
                        _plan_summary(
                            self.deobfuscator.last_plan
                        ),

                    "recovery_success":
                        deobfuscator_success
                }
            },

            "learning": {

                "obfuscator_weights":
                    dict(
                        self.obfuscator.weights
                    ),

                "deobfuscator_weights":
                    dict(
                        self.deobfuscator
                        .known_operations
                    )
            }
        }
