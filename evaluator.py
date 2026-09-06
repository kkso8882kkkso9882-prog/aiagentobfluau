class Evaluator:

    OBF_PREFIXES = (
        "-- AIOBF_PIPE_V1\n",
    )

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

        if not obfuscated.startswith(
            self.OBF_PREFIXES
        ):
            return False

        parts = obfuscated.split(
            "\n",
            2
        )

        if len(parts) != 3:
            return False

        pipeline = parts[1]
        payload = parts[2]

        if not pipeline.startswith("-- "):
            return False

        if not pipeline[3:].strip():
            return False

        if not payload.strip():
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
