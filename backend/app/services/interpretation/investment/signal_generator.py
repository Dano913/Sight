from __future__ import annotations

from typing import Any


class SignalGenerator:
    """
    Genera señales macroeconómicas derivadas de la interpretación
    económica estructurada.

    Este componente NO vuelve a interpretar growth, trend, momentum,
    volatility, position, transition o regime.

    Su función es exponer señales explícitas y no ambiguas para las
    capas posteriores.

    Las señales:
        - describen condiciones,
        - no constituyen recomendaciones de inversión,
        - no asignan puntuaciones,
        - no determinan oportunidades o riesgos por sí mismas.

    Importante:
        state describe la situación actual.
        direction describe su evolución.
        transition describe un cambio económico.
        volatility y position se mantienen descriptivas.
    """

    @staticmethod
    def generate(
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
        volatility: dict[str, Any],
        position: dict[str, Any],
        transition: dict[str, Any],
        regime: str,
    ) -> dict[str, Any]:

        return {
            "growth": SignalGenerator._growth_signals(growth),
            "trend": SignalGenerator._trend_signals(trend),
            "momentum": SignalGenerator._momentum_signals(momentum),
            "volatility": SignalGenerator._volatility_signals(volatility),
            "position": SignalGenerator._position_signals(position),
            "transition": SignalGenerator._transition_signals(transition),
            "regime": SignalGenerator._regime_signals(regime),
        }

    @staticmethod
    def _growth_signals(
        growth: dict[str, Any],
    ) -> dict[str, bool]:

        state = growth.get("state") or "unknown"
        direction = growth.get("direction") or "unknown"
        acceleration = growth.get("acceleration") or "unknown"
        dynamic_state = growth.get("dynamic_state") or "unknown"
        reversal = bool(growth.get("reversal", False))

        return {
            "positive": state == "positive",
            "negative": state == "negative",
            "flat": state == "flat",
            "improving": direction == "improving",
            "deteriorating": direction == "deteriorating",
            "stable": direction == "stable",
            "accelerating": dynamic_state == "accelerating",
            "decelerating": dynamic_state == "decelerating",
            "acceleration_positive": acceleration == "positive",
            "acceleration_negative": acceleration == "negative",
            "reversal": reversal,
        }

    @staticmethod
    def _trend_signals(
        trend: dict[str, Any],
    ) -> dict[str, bool]:

        state = trend.get("state") or "unknown"
        direction = trend.get("direction") or "unknown"
        strength = trend.get("strength") or "unknown"
        reversal = bool(trend.get("reversal", False))

        return {
            "bullish": state == "bullish",
            "bearish": state == "bearish",
            "neutral": state == "neutral",
            "mixed": state == "mixed",
            "strengthening": direction == "strengthening",
            "weakening": direction == "weakening",
            "stable": direction == "stable",
            "strong": strength == "strong",
            "moderate": strength == "moderate",
            "weak": strength == "weak",
            "reversal": reversal,
        }

    @staticmethod
    def _momentum_signals(
        momentum: dict[str, Any],
    ) -> dict[str, bool]:

        state = momentum.get("state") or "unknown"
        direction = momentum.get("direction") or "unknown"
        acceleration = momentum.get("acceleration") or "unknown"

        return {
            "positive": state == "positive",
            "negative": state == "negative",
            "neutral": state == "neutral",
            "improving": direction == "improving",
            "deteriorating": direction == "deteriorating",
            "stable": direction == "stable",
            "acceleration_positive": acceleration == "positive",
            "acceleration_negative": acceleration == "negative",
        }

    @staticmethod
    def _volatility_signals(
        volatility: dict[str, Any],
    ) -> dict[str, bool]:

        level = volatility.get("level") or "unknown"
        direction = volatility.get("direction") or "unknown"
        stress = volatility.get("stress") or "unknown"
        shock = bool(volatility.get("shock", False))

        return {
            "normal": level == "normal",
            "high": level == "high",
            "extreme": level == "extreme",
            "rising": direction == "rising",
            "falling": direction == "falling",
            "stable": direction == "stable",
            "stress_normal": stress == "normal",
            "stress_elevated": stress == "elevated",
            "stress_extreme": stress == "extreme",
            "shock": shock,
        }

    @staticmethod
    def _position_signals(
        position: dict[str, Any],
    ) -> dict[str, bool]:

        position_state = position.get("position") or "unknown"
        direction = position.get("direction") or "unknown"
        drawdown_state = position.get("drawdown_state") or "unknown"
        extreme = position.get("extreme") or "none"

        return {
            "upper_extreme": position_state == "upper_extreme",
            "upper": position_state == "upper",
            "middle": position_state == "middle",
            "lower": position_state == "lower",
            "lower_extreme": position_state == "lower_extreme",
            "recovering": direction == "recovering",
            "falling": direction == "falling",
            "mixed": direction == "mixed",
            "stable": direction == "stable",
            "minor_drawdown": drawdown_state == "minor",
            "significant_drawdown": drawdown_state == "significant",
            "severe_drawdown": drawdown_state == "severe",
            "no_drawdown": drawdown_state == "none",
            "extreme": extreme != "none",
        }

    @staticmethod
    def _transition_signals(
        transition: dict[str, Any],
    ) -> dict[str, bool]:

        detected = bool(transition.get("detected", False))
        direction = transition.get("direction") or "unknown"
        state = transition.get("state") or "none"

        return {
            "detected": detected,
            "toward_slowdown": direction == "toward_slowdown",
            "toward_contraction": direction == "toward_contraction",
            "toward_recovery": direction == "toward_recovery",
            "toward_expansion": direction == "toward_expansion",
            "toward_improvement": direction == "toward_improvement",
            "toward_deterioration": direction == "toward_deterioration",
            "mixed": direction == "mixed",
            "unknown": direction == "unknown",
            "early": state == "early",
            "moderate": state == "moderate",
            "strong": state == "strong",
            "none": state == "none",
        }

    @staticmethod
    def _regime_signals(
        regime: str,
    ) -> dict[str, bool]:

        return {
            "expansion": regime == "expansion",
            "late_expansion": regime == "late_expansion",
            "slowdown": regime == "slowdown",
            "stagnation": regime == "stagnation",
            "recovery": regime == "recovery",
            "contraction": regime == "contraction",
            "neutral": regime == "neutral",
        }