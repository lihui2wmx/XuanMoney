from __future__ import annotations

from decimal import Decimal

from xuanmoney.domain import BalanceSheet, ValidationResult


def validate_balance_sheet(
    statement: BalanceSheet,
    *,
    tolerance: Decimal = Decimal("0.01"),
) -> ValidationResult:
    difference = statement.assets - (statement.liabilities + statement.equity)
    passed = abs(difference) <= tolerance
    return ValidationResult(
        name="balance_sheet_identity",
        passed=passed,
        details=(
            f"assets - liabilities - equity = {difference}; "
            f"tolerance = {tolerance}"
        ),
    )
