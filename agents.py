# aiagentobfluau/agents.py

import base64
import binascii
import random


class ObfuscatorAgent:
    """
    Adaptive Obfuscator Agent

    มีหลาย strategy และปรับ strategy จากผลการแข่งขัน
    """

    def __init__(self):
        self.strategies = [
            "base64",
            "hex",
        ]

        self.weights = {
            "base64": 1.0,
            "hex": 1.0,
        }

        self.last_strategy = None
        self.memory = []

    def _choose_strategy(self):
        total = sum(self.weights.values())

        value = random.uniform(0, total)

        current = 0

        for strategy in self.strategies:
            current += self.weights[strategy]

            if value <= current:
                return strategy

        return self.strategies[-1]

    def obfuscate(self, source: str) -> str:
        if not isinstance(source, str):
            raise TypeError("source must be a string")

        strategy = self._choose_strategy()
        self.last_strategy = strategy

        if strategy == "base64":
            encoded = base64.b64encode(
                source.encode("utf-8")
            ).decode("ascii")

            return "-- AIOBF_B64_V1\n" + encoded

        if strategy == "hex":
            encoded = source.encode("utf-8").hex()

            return "-- AIOBF_HEX_V1\n" + encoded

        raise ValueError("Unknown obfuscation strategy")

    def learn(self, deobfuscator_success: bool):
        """
        ถ้า Deobfuscator แกะได้:
            strategy นี้เสียเปรียบ → ลด weight

        ถ้า Deobfuscator แกะไม่ได้:
            strategy นี้แข็งแรงขึ้น → เพิ่ม weight
        """

        strategy = self.last_strategy

        if strategy is None:
            return

        if deobfuscator_success:
            self.weights[strategy] *= 0.85
        else:
            self.weights[strategy] *= 1.15

        self.weights[strategy] = max(
            0.1,
            min(self.weights[strategy], 10.0)
        )

        self.memory.append({
            "strategy": strategy,
            "deobfuscator_success": deobfuscator_success
        })


class DeobfuscatorAgent:
    """
    Adaptive Deobfuscator Agent

    พยายามเลือก strategy ที่ตัวเองมีข้อมูลมากที่สุด
    """

    def __init__(self):
        self.known_strategies = {
            "base64": 1.0,
            "hex": 1.0,
        }

        self.memory = []

        self.last_detected_strategy = None

    def deobfuscate(self, obfuscated: str) -> str:
        if not isinstance(obfuscated, str):
            raise TypeError("obfuscated must be a string")

        self.last_detected_strategy = None

        if obfuscated.startswith("-- AIOBF_B64_V1\n"):
            self.last_detected_strategy = "base64"

            encoded = obfuscated.split(
                "\n",
                1
            )[1]

            try:
                decoded = base64.b64decode(
                    encoded,
                    validate=True
                )

                return decoded.decode("utf-8")

            except (
                ValueError,
                UnicodeDecodeError,
                binascii.Error
            ) as exc:
                raise ValueError(
                    "Invalid Base64 payload"
                ) from exc

        if obfuscated.startswith("-- AIOBF_HEX_V1\n"):
            self.last_detected_strategy = "hex"

            encoded = obfuscated.split(
                "\n",
                1
            )[1]

            try:
                decoded = bytes.fromhex(encoded)

                return decoded.decode("utf-8")

            except (
                ValueError,
                UnicodeDecodeError
            ) as exc:
                raise ValueError(
                    "Invalid HEX payload"
                ) from exc

        raise ValueError("Unknown AIOBF format")

    def learn(self, success: bool):
        strategy = self.last_detected_strategy

        if strategy is None:
            return

        if success:
            self.known_strategies[strategy] *= 1.15
        else:
            self.known_strategies[strategy] *= 0.85

        self.known_strategies[strategy] = max(
            0.1,
            min(self.known_strategies[strategy], 10.0)
        )

        self.memory.append({
            "strategy": strategy,
            "success": success
        })
