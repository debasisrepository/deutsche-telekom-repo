from typing import Any, Dict


class TOL4ValidationUtil:
    """
    TOL4 Validation Utility stub for supplier count rule enforcement.

    Implements the deterministic 3-6 supplier count business rule:
    - Pass: 3 <= count <= 6
    - Fail: count < 3 or count > 6
    """

    MIN_SUPPLIERS = 3
    MAX_SUPPLIERS = 6

    @staticmethod
    def validate_supplier_count(supplier_count: int) -> Dict[str, Any]:
        """
        Validate supplier count against the 3-6 rule.

        Args:
            supplier_count: Number of suppliers in the longlist

        Returns:
            Dictionary with:
            - verdict: "pass" or "fail"
            - violations: list of violation messages
        """
        violations = []

        if supplier_count < TOL4ValidationUtil.MIN_SUPPLIERS:
            violations.append(
                f"Supplier count {supplier_count} is below minimum required {TOL4ValidationUtil.MIN_SUPPLIERS}"
            )
        elif supplier_count > TOL4ValidationUtil.MAX_SUPPLIERS:
            violations.append(
                f"Supplier count {supplier_count} exceeds maximum allowed {TOL4ValidationUtil.MAX_SUPPLIERS}"
            )

        verdict = "pass" if len(violations) == 0 else "fail"

        return {
            "verdict": verdict,
            "violations": violations,
        }
