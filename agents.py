# aiagentobfluau/agents.py

import base64


class ObfuscatorAgent:
    """AI Obfuscator placeholder สำหรับ v0.1"""

    def obfuscate(self, source: str) -> str:
        if not isinstance(source, str):
            raise TypeError("source must be a string")

        encoded = base64.b64encode(
            source.encode("utf-8")
        ).decode("ascii")

        return "-- AIOBF_LUA_V1\n" + encoded


class DeobfuscatorAgent:
    """AI Deobfuscator placeholder สำหรับ v0.1"""

    PREFIX = "-- AIOBF_LUA_V1\n"

    def deobfuscate(self, obfuscated: str) -> str:
        if not isinstance(obfuscated, str):
            raise TypeError("obfuscated must be a string")

        if not obfuscated.startswith(self.PREFIX):
            raise ValueError("Invalid AIOBF format")

        encoded = obfuscated[len(self.PREFIX):]

        try:
            decoded = base64.b64decode(
                encoded,
                validate=True
            )
            return decoded.decode("utf-8")

        except (ValueError, UnicodeDecodeError) as exc:
            raise ValueError("Invalid encoded Lua data") from exc
