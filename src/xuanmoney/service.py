from __future__ import annotations

from xuanmoney.agent.state import AgentPhase, FinanceAgentState
from xuanmoney.domain import AnalysisResult, BalanceSheet, Finding, IncomeStatement
from xuanmoney.finance.metrics import profitability_metrics
from xuanmoney.finance.validation import validate_balance_sheet
from xuanmoney.finance.variance import compare_metric_sets


def analyze_financials(
    *,
    query: str,
    current: IncomeStatement,
    previous: IncomeStatement | None = None,
    balance_sheet: BalanceSheet | None = None,
) -> FinanceAgentState:
    state = FinanceAgentState(
        query=query,
        plan=[
            "compute deterministic profitability metrics",
            "compare periods when prior data is available",
            "validate accounting identities when validation data is available",
            "derive evidence-backed findings",
        ],
    )

    try:
        state.phase = AgentPhase.COMPUTING
        metrics = profitability_metrics(current)
        variances = []
        if previous is not None:
            variances = compare_metric_sets(metrics, profitability_metrics(previous))

        state.phase = AgentPhase.VALIDATING
        validations = []
        if balance_sheet is not None:
            validations.append(validate_balance_sheet(balance_sheet))

        state.phase = AgentPhase.ANALYZING
        metrics_by_name = {item.name: item for item in metrics}
        findings: list[Finding] = []
        for variance in variances:
            if variance.metric == "net_profit" and variance.absolute_change < 0:
                metric = metrics_by_name[variance.metric]
                findings.append(
                    Finding(
                        code="NET_PROFIT_DECLINE",
                        message=(
                            "Net profit declined versus the comparison period by "
                            f"{abs(variance.absolute_change)}."
                        ),
                        evidence=metric.evidence,
                    )
                )
            elif variance.metric == "gross_margin" and variance.absolute_change < 0:
                metric = metrics_by_name[variance.metric]
                findings.append(
                    Finding(
                        code="GROSS_MARGIN_DECLINE",
                        message=(
                            "Gross margin declined versus the comparison period by "
                            f"{abs(variance.absolute_change)} in ratio terms."
                        ),
                        evidence=metric.evidence,
                    )
                )

        state.result = AnalysisResult(
            period=current.period,
            metrics=metrics,
            variances=variances,
            validations=validations,
            findings=findings,
        )
        state.phase = AgentPhase.COMPLETE
        return state
    except Exception as exc:
        state.phase = AgentPhase.FAILED
        state.errors.append(str(exc))
        return state
