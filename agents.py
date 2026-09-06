import base64
import json
import random


class ObfuscatorAgent:

    OPERATIONS = ("base64", "hex", "reverse")

    def __init__(self):
        self.weights = {
            op: 1.0 for op in self.OPERATIONS
        }
        self.last_plan = None
        self.memory = []

    def _choose_operation(self):
        total = sum(self.weights.values())
        value = random.uniform(0, total)
        current = 0.0

        for op in self.OPERATIONS:
            current += self.weights[op]
            if value <= current:
                return op

        return self.OPERATIONS[-1]

    def _apply(self, data, operation):
        if operation == "base64":
            return base64.b64encode(
                data.encode("utf-8")
            ).decode("ascii")

        if operation == "hex":
            return data.encode("utf-8").hex()

        if operation == "reverse":
            return data[::-1]

        raise ValueError(
            f"Unknown operation: {operation}"
        )

    def obfuscate(self, source):
        if not isinstance(source, str):
            raise TypeError("source must be a string")

        chunks = []
        i = 0
        pos = 0
        n = len(source)

        while pos < n:
            length = random.randint(1, 12)
            if pos + length > n:
                length = n - pos

            piece = source[pos:pos + length]
            op = self._choose_operation()
            encoded = self._apply(piece, op)

            chunks.append({
                "i": i,
                "len": length,
                "op": op,
                "data": encoded,
            })

            i += 1
            pos += length

        self.last_plan = {
            "version": 1,
            "chunks": chunks,
        }

        payload = json.dumps(
            self.last_plan,
            separators=(",", ":"),
            ensure_ascii=True,
        )

        return f"-- AIOBF_CHUNK_V1\n{payload}"

    def learn(self, deobfuscator_success):
        if self.last_plan is None:
            return

        ops_used = [
            c["op"] for c in self.last_plan["chunks"]
        ]

        for op in ops_used:
            if deobfuscator_success:
                self.weights[op] *= 0.75
            else:
                self.weights[op] *= 1.30

            self.weights[op] = max(
                0.05,
                min(self.weights[op], 20.0),
            )

        self.memory.append({
            "ops": ops_used,
            "deobfuscator_success": deobfuscator_success,
            "weights": dict(self.weights),
        })

        if len(self.memory) > 500:
            self.memory.pop(0)


class DeobfuscatorAgent:

    OPERATIONS = ("base64", "hex", "reverse")

    def __init__(self):
        self.known_operations = {
            op: 1.0 for op in self.OPERATIONS
        }
        self.last_plan = None
        self.memory = []

    def _decode_operation(self, data, operation):
        if operation == "reverse":
            return data[::-1]

        if operation == "base64":
            decoded = base64.b64decode(data, validate=True)
            return decoded.decode("utf-8")

        if operation == "hex":
            decoded = bytes.fromhex(data)
            return decoded.decode("utf-8")

        raise ValueError(
            f"Unknown operation: {operation}"
        )

    def deobfuscate(self, obfuscated):
        if not isinstance(obfuscated, str):
            raise TypeError(
                "obfuscated must be a string"
            )

        prefix = "-- AIOBF_CHUNK_V1\n"

        if not obfuscated.startswith(prefix):
            raise ValueError("Unknown AIOBF format")

        payload = obfuscated[len(prefix):]

        try:
            plan = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Invalid chunk payload"
            ) from exc

        if not isinstance(plan, dict):
            raise ValueError("Invalid plan type")

        if plan.get("version") != 1:
            raise ValueError("Unsupported version")

        chunks = plan.get("chunks")
        if not isinstance(chunks, list) or not chunks:
            raise ValueError("Invalid chunks")

        # Validate indices: must be 0..n-1 unique
        n = len(chunks)
        indices = []
        for c in chunks:
            if not isinstance(c, dict):
                raise ValueError("Invalid chunk")
            if "i" not in c or "len" not in c or "op" not in c or "data" not in c:
                raise ValueError("Missing chunk fields")
            if not isinstance(c["i"], int):
                raise ValueError("Invalid chunk index")
            if not isinstance(c["len"], int) or c["len"] < 1:
                raise ValueError("Invalid original length")
            if c["op"] not in self.OPERATIONS:
                raise ValueError("Invalid operation")
            if not isinstance(c["data"], str):
                raise ValueError("Invalid encoded data")
            indices.append(c["i"])

        if sorted(indices) != list(range(n)):
            raise ValueError("Invalid chunk index sequence")

        # Sort by index and decode
        ordered = sorted(chunks, key=lambda c: c["i"])
        parts = []

        for c in ordered:
            try:
                piece = self._decode_operation(
                    c["data"],
                    c["op"],
                )
            except Exception as exc:
                raise ValueError(
                    "Failed to decode chunk"
                ) from exc

            if len(piece) != c["len"]:
                raise ValueError(
                    "Chunk length mismatch after decode"
                )

            parts.append(piece)

        self.last_plan = plan
        return "".join(parts)

    def learn(self, success):
        if self.last_plan is None:
            return

        ops_used = [
            c["op"] for c in self.last_plan["chunks"]
        ]

        for op in ops_used:
            if success:
                self.known_operations[op] *= 1.15
            else:
                self.known_operations[op] *= 0.85

            self.known_operations[op] = max(
                0.05,
                min(self.known_operations[op], 20.0),
            )

        self.memory.append({
            "ops": ops_used,
            "success": success,
        })

        if len(self.memory) > 500:
            self.memory.pop(0)
