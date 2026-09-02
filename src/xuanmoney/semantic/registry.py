from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class SemanticField:
    name: str
    aliases: tuple[str, ...]
    required: bool = False


def _normalize_header(value: str) -> str:
    value = value.strip().casefold()
    value = re.sub(r"[\s\-_./()（）]+", "", value)
    return value


INCOME_STATEMENT_FIELDS: tuple[SemanticField, ...] = (
    SemanticField("period", ("period", "accounting_period", "期间", "会计期间", "月份"), True),
    SemanticField("currency", ("currency", "币种")),
    SemanticField("revenue", ("revenue", "operating_revenue", "营业收入", "销售收入"), True),
    SemanticField("cogs", ("cogs", "cost_of_goods_sold", "operating_cost", "营业成本", "销售成本"), True),
    SemanticField("operating_expenses", ("operating_expenses", "opex", "经营费用", "运营费用")),
    SemanticField("other_income", ("other_income", "其他收益", "其他收入")),
    SemanticField("other_expenses", ("other_expenses", "其他支出", "其他费用")),
    SemanticField("taxes", ("taxes", "income_tax", "所得税", "所得税费用")),
)


class SemanticMappingError(ValueError):
    pass


def resolve_income_statement_columns(headers: Iterable[str]) -> dict[str, str]:
    """Resolve source headers to the canonical v0.1 income-statement schema.

    Mapping is deliberately explicit. Unknown headers are ignored; ambiguous aliases and
    missing required fields fail closed rather than being guessed by an LLM.
    """

    source_headers = [str(header) for header in headers]
    normalized_sources: dict[str, list[str]] = {}
    for header in source_headers:
        normalized_sources.setdefault(_normalize_header(header), []).append(header)

    resolved: dict[str, str] = {}
    for field in INCOME_STATEMENT_FIELDS:
        matches: list[str] = []
        for alias in field.aliases:
            matches.extend(normalized_sources.get(_normalize_header(alias), []))
        matches = list(dict.fromkeys(matches))
        if len(matches) > 1:
            raise SemanticMappingError(
                f"multiple source columns map to canonical field {field.name!r}: {matches}"
            )
        if matches:
            resolved[field.name] = matches[0]
        elif field.required:
            raise SemanticMappingError(
                f"required canonical field {field.name!r} has no recognized source column"
            )

    return resolved
