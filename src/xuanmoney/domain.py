from __future__ import annotations

from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class Unit(StrEnum):
    MONEY = "money"
    RATIO = "ratio"
    PERCENTAGE_POINT = "percentage_point"


class IncomeStatement(BaseModel):
    period: str
    currency: str = "CNY"
    revenue: Decimal
    cogs: Decimal
    operating_expenses: Decimal = Decimal("0")
    other_income: Decimal = Decimal("0")
    other_expenses: Decimal = Decimal("0")
    taxes: Decimal = Decimal("0")


class BalanceSheet(BaseModel):
    period: str
    currency: str = "CNY"
    assets: Decimal
    liabilities: Decimal
    equity: Decimal


class Evidence(BaseModel):
    source: str
    field: str
    period: str
    value: Decimal


class MetricResult(BaseModel):
    name: str
    value: Decimal
    unit: Unit
    evidence: list[Evidence] = Field(default_factory=list)


class VarianceResult(BaseModel):
    metric: str
    current: Decimal
    previous: Decimal
    absolute_change: Decimal
    relative_change: Decimal | None = None


class ValidationResult(BaseModel):
    name: str
    passed: bool
    details: str


class Finding(BaseModel):
    code: str
    message: str
    evidence: list[Evidence] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    period: str
    metrics: list[MetricResult] = Field(default_factory=list)
    variances: list[VarianceResult] = Field(default_factory=list)
    validations: list[ValidationResult] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)

    @property
    def validation_passed(self) -> bool:
        return all(item.passed for item in self.validations)
