# aiagentobfluau/scoring.py


class ScoringSystem:
    """ระบบคำนวณคะแนนของ AI Agents"""

    OBFUSCATOR_SUCCESS = 3
    DEOBFUSCATOR_SUCCESS = 3
    OBFUSCATOR_BROKEN = -2

    def calculate(
        self,
        obfuscator_success: bool,
        deobfuscator_success: bool
    ) -> dict:
        obfuscator_score = 0
        deobfuscator_score = 0

        # Obfuscator ทำสำเร็จ
        if obfuscator_success:
            obfuscator_score += self.OBFUSCATOR_SUCCESS

        # Deobfuscator แกะสำเร็จ
        if deobfuscator_success:
            deobfuscator_score += self.DEOBFUSCATOR_SUCCESS

            # ถ้าแกะได้ แสดงว่า Obfuscator ถูกเจาะ
            if obfuscator_success:
                obfuscator_score += self.OBFUSCATOR_BROKEN

        # ไม่ให้คะแนนติดลบ
        obfuscator_score = max(0, obfuscator_score)
        deobfuscator_score = max(0, deobfuscator_score)

        return {
            "obfuscator": obfuscator_score,
            "deobfuscator": deobfuscator_score
        }
