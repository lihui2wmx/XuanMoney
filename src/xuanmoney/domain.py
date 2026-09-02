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
    source: str = "income_statement"
    revenue: Decimal
    cogs: Decimal
    operating_expenses: Decimal = Decimal("0")
    other_income: Decimal = Decimal("0")
    other_expenses: Decimal = Decimal("0")
    taxes: Decimal = Decimal("0")


class BalanceSheet(BaseModel):
    period: str
    currency: str = "CNY"
    source: str = "balance_sheet"
    assets: Decimal
    liabilities: Decimal
    equity: Decimal


class Evidence(BaseModel):
    source: str
    field: str
    period: str
    value: Decimal
    dimension: str | None = None
    member: str | None = None


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


class ProfitBridgeContribution(BaseModel):
    component: str
    raw_change: Decimal
    contribution: Decimal
    evidence: list[Evidence] = Field(default_factory=list)


class ProfitBridgeResult(BaseModel):
    current_period: str
    previous_period: str
    total_net_profit_change: Decimal
    contributions: list[ProfitBridgeContribution] = Field(default_factory=list)
    reconciliation_difference: Decimal

    @property
    def reconciled(self) -> bool:
        return self.reconciliation_difference == 0


class ValidationResult(BaseModel):
    name: str
    passed: bool
    details: str


class DimensionalRow(BaseModel):
    period: str
    dimension: str
    member: str
    currency: str = "CNY"
    source: str = "dimensional"
    revenue: Decimal
    cogs: Decimal


class DimensionalMemberMetrics(BaseModel):
    period: str
    dimension: str
    member: str
    currency: str = "CNY"
    revenue: Decimal
    cogs: Decimal
    gross_profit: Decimal
    gross_margin: Decimal | None
    evidence: list[Evidence] = Field(default_factory=list)


class DimensionalMemberContribution(BaseModel):
    member: str
    revenue_change: Decimal
    cogs_change: Decimal
    gross_profit_change: Decimal
    evidence: list[Evidence] = Field(default_factory=list)


class DimensionalVarianceResult(BaseModel):
    dimension: str
    current_period: str
    previous_period: str
    total_gross_profit_change: Decimal
    member_contributions: list[DimensionalMemberContribution] = Field(default_factory=list)
    reconciliation_difference: Decimal

    @property
    def reconciled(self) -> bool:
        return self.reconciliation_difference == 0


class DimensionalAnalysisResult(BaseModel):
    dimension: str
    current_period: str
    previous_period: str | None = None
    current_members: list[DimensionalMemberMetrics] = Field(default_factory=list)
    previous_members: list[DimensionalMemberMetrics] = Field(default_factory=list)
    variance: DimensionalVarianceResult | None = None
    validations: list[ValidationResult] = Field(default_factory=list)

    @property
    def validation_passed(self) -> bool:
        return all(item.passed for item in self.validations)


class Finding(BaseModel):
    code: str
    message: str
    evidence: list[Evidence] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    period: str
    metrics: list[MetricResult] = Field(default_factory=list)
    variances: list[VarianceResult] = Field(default_factory=list)
    profit_bridge: ProfitBridgeResult | None = None
    validations: list[ValidationResult] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)

    @property
    def validation_passed(self) -> bool:
        return all(item.passed for item in self.validations)
