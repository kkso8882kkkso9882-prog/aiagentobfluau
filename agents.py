import base64
import random


class ObfuscatorAgent:

    def __init__(self):
        self.strategies = [
            ("base64",),
            ("hex",),
            ("reverse",),
            ("base64", "hex"),
            ("hex", "base64"),
            ("reverse", "base64"),
            ("reverse", "hex"),
            ("base64", "reverse"),
            ("hex", "reverse"),
        ]

        self.weights = {
            self._name(s): 1.0
            for s in self.strategies
        }

        self.last_pipeline = None
        self.memory = []

    def _name(self, pipeline):
        return " -> ".join(pipeline)

    def _choose_pipeline(self):
        total = sum(self.weights.values())
        value = random.uniform(0, total)

        current = 0.0

        for pipeline in self.strategies:
            name = self._name(pipeline)
            current += self.weights[name]

            if value <= current:
                return pipeline

        return self.strategies[-1]

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
            raise TypeError(
                "source must be a string"
            )

        pipeline = self._choose_pipeline()
        self.last_pipeline = pipeline

        data = source

        for operation in pipeline:
            data = self._apply(
                data,
                operation
            )

        return (
            "-- AIOBF_PIPE_V1\n"
            f"-- {self._name(pipeline)}\n"
            f"{data}"
        )

    def learn(self, deobfuscator_success):

        if self.last_pipeline is None:
            return

        name = self._name(
            self.last_pipeline
        )

        if deobfuscator_success:
            self.weights[name] *= 0.75
        else:
            self.weights[name] *= 1.30

        self.weights[name] = max(
            0.05,
            min(self.weights[name], 20.0)
        )

        self.memory.append({
            "pipeline": name,
            "deobfuscator_success":
                deobfuscator_success,
            "weight":
                self.weights[name]
        })

        if len(self.memory) > 500:
            self.memory.pop(0)


class DeobfuscatorAgent:

    def __init__(self):

        self.known_operations = {
            "base64": 1.0,
            "hex": 1.0,
            "reverse": 1.0,
        }

        self.last_pipeline = None
        self.memory = []

    def _decode_operation(
        self,
        data,
        operation
    ):

        if operation == "reverse":
            return data[::-1]

        if operation == "base64":

            decoded = base64.b64decode(
                data,
                validate=True
            )

            return decoded.decode(
                "utf-8"
            )

        if operation == "hex":

            decoded = bytes.fromhex(data)

            return decoded.decode(
                "utf-8"
            )

        raise ValueError(
            f"Unknown operation: {operation}"
        )

    def deobfuscate(self, obfuscated):

        if not isinstance(obfuscated, str):
            raise TypeError(
                "obfuscated must be a string"
            )

        prefix = "-- AIOBF_PIPE_V1\n"

        if not obfuscated.startswith(prefix):
            raise ValueError(
                "Unknown AIOBF format"
            )

        lines = obfuscated.split("\n", 2)

        if len(lines) != 3:
            raise ValueError(
                "Invalid pipeline payload"
            )

        pipeline_line = lines[1]

        if not pipeline_line.startswith("-- "):
            raise ValueError(
                "Invalid pipeline"
            )

        pipeline = tuple(
            part.strip()
            for part in pipeline_line[3:].split(" -> ")
        )

        data = lines[2]

        self.last_pipeline = pipeline

        for operation in reversed(pipeline):

            data = self._decode_operation(
                data,
                operation
            )

        return data

    def learn(self, success):

        if self.last_pipeline is None:
            return

        for operation in self.last_pipeline:

            if success:
                self.known_operations[
                    operation
                ] *= 1.15
            else:
                self.known_operations[
                    operation
                ] *= 0.85

            self.known_operations[
                operation
            ] = max(
                0.05,
                min(
                    self.known_operations[
                        operation
                    ],
                    20.0
                )
            )

        self.memory.append({
            "pipeline":
                " -> ".join(
                    self.last_pipeline
                ),
            "success": success
        })

        if len(self.memory) > 500:
            self.memory.pop(0)
