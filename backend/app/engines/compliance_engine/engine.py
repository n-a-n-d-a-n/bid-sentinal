"""
Deterministic Compliance Rule Engine

CRITICAL: NO LLM IS USED FOR ARITHMETIC OR RULE EVALUATION.
All computations are pure Python deterministic logic.
LLM is only used upstream for extraction; never for threshold decisions.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, UTC
from enum import Enum
from typing import Any, Dict, List, Optional
import structlog

logger = structlog.get_logger(__name__)


class RuleResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    NOT_VERIFIED = "NOT_VERIFIED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass
class EvaluationEvidence:
    rule_id: str
    field: str
    computed_value: Any
    threshold_value: Any
    operator: str
    result: RuleResult
    detail: str
    source_documents: List[str] = field(default_factory=list)
    confidence: float = 1.0


@dataclass
class RuleEvaluationResult:
    rule_id: str
    rule_name: str
    category: str
    mandatory: bool
    result: RuleResult
    computed_value: Any
    threshold_value: Any
    detail: str
    evidence: List[EvaluationEvidence] = field(default_factory=list)
    confidence: float = 1.0
    warnings: List[str] = field(default_factory=list)


class ComplianceEngine:
    """
    Deterministic compliance evaluation engine.
    Supports: numeric thresholds, averages, sums, counts,
    date validity, existence checks, set membership,
    cross-source equality, percentage calculations, conditional rules.
    """

    OPERATORS = {
        ">=": lambda a, b: a >= b,
        "<=": lambda a, b: a <= b,
        ">": lambda a, b: a > b,
        "<": lambda a, b: a < b,
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
    }

    def evaluate_rule(
        self,
        rule_definition: Dict[str, Any],
        extracted_data: Dict[str, Any],
        verification_results: Dict[str, Any] = None,
    ) -> RuleEvaluationResult:
        """
        Route rule to the appropriate evaluator based on rule_type.
        Returns a deterministic result — no LLM involved.
        """
        rule_id = rule_definition.get("rule_id", "UNKNOWN")
        rule_name = rule_definition.get("name", rule_id)
        rule_type = rule_definition.get("type", "THRESHOLD")
        category = rule_definition.get("category", "COMPLIANCE")
        mandatory = rule_definition.get("mandatory", True)

        try:
            evaluator = getattr(self, f"_eval_{rule_type.lower()}", None)
            if evaluator is None:
                return RuleEvaluationResult(
                    rule_id=rule_id, rule_name=rule_name, category=category,
                    mandatory=mandatory, result=RuleResult.MANUAL_REVIEW,
                    computed_value=None, threshold_value=None,
                    detail=f"Unknown rule type '{rule_type}' — requires manual review.",
                )
            return evaluator(rule_definition, extracted_data, verification_results or {})
        except Exception as exc:
            logger.error("rule_evaluation_error", rule_id=rule_id, error=str(exc), exc_info=True)
            return RuleEvaluationResult(
                rule_id=rule_id, rule_name=rule_name, category=category,
                mandatory=mandatory, result=RuleResult.MANUAL_REVIEW,
                computed_value=None, threshold_value=None,
                detail=f"Evaluation error: {exc}. Manual review required.",
            )

    def _eval_threshold(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        """Single field vs threshold."""
        field_path = rule["field"]
        op = rule["operator"]
        threshold = rule["threshold"]
        rule_id = rule["rule_id"]
        value = self._get_field(data, field_path)

        if value is None:
            return self._not_found(rule, field_path)

        try:
            numeric_val = float(value)
            numeric_threshold = float(threshold)
        except (TypeError, ValueError) as e:
            return RuleEvaluationResult(
                rule_id=rule_id, rule_name=rule.get("name", rule_id),
                category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
                result=RuleResult.MANUAL_REVIEW,
                computed_value=value, threshold_value=threshold,
                detail=f"Non-numeric value '{value}' — cannot evaluate.",
            )

        passes = self.OPERATORS.get(op, lambda a, b: False)(numeric_val, numeric_threshold)
        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if passes else RuleResult.FAIL,
            computed_value=numeric_val, threshold_value=numeric_threshold,
            detail=(
                f"Field '{field_path}' = {numeric_val:,.2f} {op} threshold {numeric_threshold:,.2f}: "
                f"{'PASS' if passes else 'FAIL'}"
            ),
        )

    def _eval_average(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        """Average of a list of values vs threshold."""
        field_path = rule["field"]
        op = rule["operator"]
        threshold = rule["threshold"]
        period = rule.get("period", 3)
        rule_id = rule["rule_id"]

        values = self._get_field(data, field_path)
        if values is None or not isinstance(values, list):
            return self._not_found(rule, field_path)

        numeric_values = []
        for v in values[:period]:
            try:
                numeric_values.append(float(v))
            except (TypeError, ValueError):
                pass

        if not numeric_values:
            return self._not_found(rule, field_path + "[numeric_values]")

        avg = sum(numeric_values) / len(numeric_values)
        threshold_f = float(threshold)
        passes = self.OPERATORS.get(op, lambda a, b: False)(avg, threshold_f)

        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if passes else RuleResult.FAIL,
            computed_value=avg, threshold_value=threshold_f,
            detail=(
                f"Average of {len(numeric_values)} year(s) = {avg:,.2f} "
                f"({', '.join(f'{v:,.2f}' for v in numeric_values)}) "
                f"{op} threshold {threshold_f:,.2f}: {'PASS' if passes else 'FAIL'}"
            ),
        )

    def _eval_sum(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        field_path = rule["field"]
        op = rule["operator"]
        threshold = rule["threshold"]
        rule_id = rule["rule_id"]

        values = self._get_field(data, field_path)
        if values is None or not isinstance(values, list):
            return self._not_found(rule, field_path)

        total = sum(float(v) for v in values if v is not None)
        threshold_f = float(threshold)
        passes = self.OPERATORS.get(op, lambda a, b: False)(total, threshold_f)

        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if passes else RuleResult.FAIL,
            computed_value=total, threshold_value=threshold_f,
            detail=f"Sum = {total:,.2f} {op} {threshold_f:,.2f}: {'PASS' if passes else 'FAIL'}",
        )

    def _eval_existence(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        """Check if a field/document type exists."""
        field_path = rule["field"]
        rule_id = rule["rule_id"]

        value = self._get_field(data, field_path)
        exists = value is not None and value != "" and value != []

        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if exists else RuleResult.FAIL,
            computed_value=str(value) if value else None,
            threshold_value="EXISTS",
            detail=f"Field '{field_path}' {'found' if exists else 'NOT FOUND / MISSING'}.",
        )

    def _eval_date_validity(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        """Check that a date field is not expired."""
        field_path = rule["field"]
        reference_date_str = rule.get("reference_date", "TODAY")
        rule_id = rule["rule_id"]

        value = self._get_field(data, field_path)
        if value is None:
            return self._not_found(rule, field_path)

        ref_date = date.today() if reference_date_str == "TODAY" else date.fromisoformat(reference_date_str)

        try:
            if isinstance(value, str):
                doc_date = date.fromisoformat(value[:10])
            elif isinstance(value, (date, datetime)):
                doc_date = value if isinstance(value, date) else value.date()
            else:
                raise ValueError(f"Cannot parse date: {value}")
        except ValueError as e:
            return RuleEvaluationResult(
                rule_id=rule_id, rule_name=rule.get("name", rule_id),
                category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
                result=RuleResult.MANUAL_REVIEW,
                computed_value=str(value), threshold_value=None,
                detail=f"Cannot parse date '{value}': {e}",
            )

        is_valid = doc_date >= ref_date
        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if is_valid else RuleResult.FAIL,
            computed_value=doc_date.isoformat(), threshold_value=ref_date.isoformat(),
            detail=(
                f"Date '{doc_date}' is {'valid (not expired)' if is_valid else 'EXPIRED'} "
                f"as of reference date {ref_date}."
            ),
        )

    def _eval_set_membership(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        field_path = rule["field"]
        allowed_values = rule["values"]
        rule_id = rule["rule_id"]

        value = self._get_field(data, field_path)
        if value is None:
            return self._not_found(rule, field_path)

        in_set = str(value).upper() in [str(v).upper() for v in allowed_values]
        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if in_set else RuleResult.FAIL,
            computed_value=str(value), threshold_value=str(allowed_values),
            detail=f"Value '{value}' {'IS' if in_set else 'is NOT'} in allowed set {allowed_values}.",
        )

    def _eval_cross_equality(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        """Check equality of the same field across multiple documents."""
        field_path = rule["field"]
        sources = rule.get("sources", [])
        rule_id = rule["rule_id"]

        values = {}
        for source in sources:
            v = self._get_field(data, f"{source}.{field_path}")
            if v is not None:
                values[source] = str(v).upper().strip()

        if len(values) < 2:
            return RuleEvaluationResult(
                rule_id=rule_id, rule_name=rule.get("name", rule_id),
                category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
                result=RuleResult.MANUAL_REVIEW,
                computed_value=str(values), threshold_value="CONSISTENT",
                detail=f"Insufficient data from multiple sources to verify cross-document consistency.",
            )

        unique_values = set(values.values())
        consistent = len(unique_values) == 1
        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if consistent else RuleResult.FAIL,
            computed_value=str(values), threshold_value="CONSISTENT",
            detail=(
                f"Cross-document field '{field_path}': "
                + (f"consistent (all = '{list(unique_values)[0]}')" if consistent else
                   f"CONFLICT — values differ: {dict(values)}")
            ),
        )

    def _eval_percentage(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        numerator_path = rule["numerator"]
        denominator_path = rule["denominator"]
        op = rule["operator"]
        threshold = rule["threshold"]
        rule_id = rule["rule_id"]

        num = self._get_field(data, numerator_path)
        den = self._get_field(data, denominator_path)

        if num is None or den is None:
            return self._not_found(rule, f"{numerator_path}/{denominator_path}")

        try:
            num_f, den_f = float(num), float(den)
            if den_f == 0:
                raise ZeroDivisionError("Denominator is zero")
            pct = (num_f / den_f) * 100
        except (TypeError, ValueError, ZeroDivisionError) as e:
            return RuleEvaluationResult(
                rule_id=rule_id, rule_name=rule.get("name", rule_id),
                category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
                result=RuleResult.MANUAL_REVIEW,
                computed_value=None, threshold_value=threshold,
                detail=f"Percentage computation error: {e}",
            )

        threshold_f = float(threshold)
        passes = self.OPERATORS.get(op, lambda a, b: False)(pct, threshold_f)
        return RuleEvaluationResult(
            rule_id=rule_id, rule_name=rule.get("name", rule_id),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.PASS if passes else RuleResult.FAIL,
            computed_value=pct, threshold_value=threshold_f,
            detail=f"Percentage = {pct:.2f}% {op} threshold {threshold_f:.2f}%: {'PASS' if passes else 'FAIL'}",
        )

    def _eval_conditional(self, rule: dict, data: dict, verif: dict) -> RuleEvaluationResult:
        """IF condition THEN evaluate sub-rule ELSE return NOT_APPLICABLE."""
        condition = rule.get("condition", {})
        then_rule = rule.get("then", {})
        rule_id = rule["rule_id"]

        # Evaluate condition
        cond_field = condition.get("field")
        cond_op = condition.get("operator", "==")
        cond_value = condition.get("value")

        actual = self._get_field(data, cond_field)
        condition_met = self.OPERATORS.get(cond_op, lambda a, b: a == b)(
            str(actual).upper() if actual else "", str(cond_value).upper()
        )

        if not condition_met:
            return RuleEvaluationResult(
                rule_id=rule_id, rule_name=rule.get("name", rule_id),
                category=rule.get("category", ""), mandatory=False,
                result=RuleResult.NOT_APPLICABLE,
                computed_value=str(actual), threshold_value=str(cond_value),
                detail=f"Condition '{cond_field} {cond_op} {cond_value}' not met — rule NOT APPLICABLE.",
            )

        # Evaluate then-rule
        then_rule["rule_id"] = rule_id
        then_rule["name"] = rule.get("name", rule_id)
        then_rule["category"] = rule.get("category", "")
        then_rule["mandatory"] = rule.get("mandatory", True)
        return self.evaluate_rule(then_rule, data, verif)

    def evaluate_all_rules(
        self,
        rules: List[Dict[str, Any]],
        extracted_data: Dict[str, Any],
        verification_results: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Evaluate all rules and produce a compliance summary."""
        results = []
        mandatory_fails = 0
        mandatory_passes = 0
        total_mandatory = 0
        warnings = []

        for rule_def in rules:
            result = self.evaluate_rule(rule_def, extracted_data, verification_results)
            results.append(result)

            if rule_def.get("mandatory", True):
                total_mandatory += 1
                if result.result == RuleResult.PASS:
                    mandatory_passes += 1
                elif result.result in (RuleResult.FAIL,):
                    mandatory_fails += 1
                elif result.result in (RuleResult.NOT_VERIFIED, RuleResult.MANUAL_REVIEW):
                    warnings.append(f"Rule {result.rule_id}: requires manual review")

        # Overall compliance: FAIL if any mandatory rule fails
        if mandatory_fails > 0:
            overall = RuleResult.FAIL
        elif warnings:
            overall = RuleResult.MANUAL_REVIEW
        elif mandatory_passes == total_mandatory and total_mandatory > 0:
            overall = RuleResult.PASS
        else:
            overall = RuleResult.CONDITIONAL

        # Compliance score: percentage of mandatory rules passing
        compliance_score = (
            (mandatory_passes / total_mandatory * 100) if total_mandatory > 0 else 0.0
        )

        return {
            "overall_result": overall.value,
            "compliance_score": round(compliance_score, 2),
            "total_rules": len(rules),
            "mandatory_rules": total_mandatory,
            "mandatory_passes": mandatory_passes,
            "mandatory_fails": mandatory_fails,
            "warnings": warnings,
            "rule_results": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "category": r.category,
                    "mandatory": r.mandatory,
                    "result": r.result.value,
                    "computed_value": r.computed_value,
                    "threshold_value": r.threshold_value,
                    "detail": r.detail,
                    "confidence": r.confidence,
                }
                for r in results
            ],
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _get_field(self, data: dict, path: str) -> Any:
        """Dot-notation field access."""
        parts = path.split(".")
        current = data
        for part in parts:
            if current is None:
                return None
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _not_found(self, rule: dict, field_path: str) -> RuleEvaluationResult:
        return RuleEvaluationResult(
            rule_id=rule["rule_id"], rule_name=rule.get("name", rule["rule_id"]),
            category=rule.get("category", ""), mandatory=rule.get("mandatory", True),
            result=RuleResult.NOT_VERIFIED,
            computed_value=None, threshold_value=None,
            detail=f"Field '{field_path}' not found in extracted data — NOT VERIFIED / MANUAL REVIEW.",
        )
