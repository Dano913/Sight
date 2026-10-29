from __future__ import annotations

from typing import Any


class RegimeClassifier:
    @staticmethod
    def classify(
        *,
        growth: dict[str, Any],
        trend: dict[str, Any],
        momentum: dict[str, Any],
        volatility: dict[str, Any],
        position: dict[str, Any],
        transition: dict[str, Any],
    ) -> str:
        growth_state = growth.get("state", "unknown")
        growth_direction = growth.get("direction", "unknown")

        trend_state = trend.get("state", "unknown")
        trend_direction = trend.get("direction", "unknown")

        momentum_state = momentum.get("state", "unknown")
        momentum_direction = momentum.get("direction", "unknown")

        drawdown_state = position.get(
            "drawdown_state",
            "unknown",
        )

        transition_detected = bool(
            transition.get("detected", False)
        )
        transition_direction = transition.get(
            "direction",
            "unknown",
        )
        transition_state = transition.get(
            "state",
            "none",
        )

        growth_negative = growth_state == "negative"
        growth_positive = growth_state == "positive"

        trend_bearish = trend_state == "bearish"
        trend_bullish = trend_state == "bullish"

        momentum_negative = momentum_state == "negative"
        momentum_positive = momentum_state == "positive"

        growth_improving = growth_direction == "improving"
        trend_improving = trend_direction == "improving"
        momentum_improving = momentum_direction == "improving"

        growth_deteriorating = (
            growth_direction == "deteriorating"
        )
        trend_deteriorating = (
            trend_direction == "deteriorating"
        )
        momentum_deteriorating = (
            momentum_direction == "deteriorating"
        )

        # ---------------------------------------------------------
        # RECOVERY
        # ---------------------------------------------------------
        #
        # Recovery requires either:
        #   - two negative components that are improving, or
        #   - a detected moderate/strong transition toward recovery.
        #
        # However, explicit deterioration of negative growth
        # represents an active contraction and has priority.
        #

        recovery_components = sum(
            [
                growth_negative and growth_improving,
                trend_bearish and trend_improving,
                momentum_negative and momentum_improving,
            ]
        )

        recovery_from_components = (
            recovery_components >= 2
        )

        recovery_from_transition = (
            transition_detected
            and transition_direction == "toward_recovery"
            and transition_state in {
                "moderate",
                "strong",
            }
        )

        recovery_signal = (
            recovery_from_components
            or recovery_from_transition
        )

        # ---------------------------------------------------------
        # CONTRACTION
        # ---------------------------------------------------------
        #
        # Explicit deterioration while growth is already negative
        # defines an active contraction.
        #
        # This deliberately has priority over recovery.
        #

        explicit_contraction = (
            growth_negative
            and growth_deteriorating
            and (
                trend_bearish
                or momentum_negative
            )
        )

        if explicit_contraction:
            return "contraction"

        if recovery_signal:
            return "recovery"

        # A fully negative environment with no recovery signal
        # remains contraction.
        full_contraction = (
            growth_negative
            and trend_bearish
            and momentum_negative
        )

        if full_contraction:
            return "contraction"

        # ---------------------------------------------------------
        # SLOWDOWN
        # ---------------------------------------------------------
        #
        # Slowdown requires current evidence of deterioration.
        # A transition toward slowdown alone does not change the
        # current regime.
        #

        slowdown_components = sum(
            [
                growth_positive and growth_deteriorating,
                trend_bullish and trend_deteriorating,
                momentum_positive and momentum_deteriorating,
            ]
        )

        slowdown_from_components = (
            slowdown_components >= 2
        )

        if slowdown_from_components:
            return "slowdown"

        # ---------------------------------------------------------
        # LATE EXPANSION
        # ---------------------------------------------------------
        #
        # The economy is still expansionary, but at least one
        # component is deteriorating.
        #
        # A detected transition toward slowdown reinforces this
        # interpretation but does not independently create a
        # slowdown regime.
        #

        positive_environment = (
            growth_positive
            and trend_bullish
            and momentum_positive
        )

        some_deterioration = (
            growth_deteriorating
            or trend_deteriorating
            or momentum_deteriorating
        )

        late_expansion_signal = (
            positive_environment
            and some_deterioration
        )

        if late_expansion_signal:
            return "late_expansion"

        if (
            positive_environment
            and transition_detected
            and transition_direction == "toward_slowdown"
            and transition_state in {
                "moderate",
                "strong",
            }
        ):
            return "late_expansion"

        # ---------------------------------------------------------
        # EXPANSION
        # ---------------------------------------------------------

        directions_compatible_with_expansion = all(
            direction in {
                "improving",
                "stable",
                "unknown",
            }
            for direction in (
                growth_direction,
                trend_direction,
                momentum_direction,
            )
        )

        if (
            growth_positive
            and trend_bullish
            and momentum_positive
            and directions_compatible_with_expansion
        ):
            return "expansion"

        # ---------------------------------------------------------
        # STAGNATION
        # ---------------------------------------------------------

        stagnation_components = 0

        if growth_state in {
            "flat",
            "unknown",
        }:
            stagnation_components += 1

        if trend_state in {
            "mixed",
            "neutral",
            "unknown",
        }:
            stagnation_components += 1

        if momentum_state in {
            "neutral",
            "unknown",
        }:
            stagnation_components += 1

        if (
            growth_positive
            and growth_direction == "stable"
        ):
            stagnation_components += 1

        if (
            stagnation_components >= 2
            and drawdown_state != "severe"
        ):
            return "stagnation"

        # ---------------------------------------------------------
        # NEUTRAL
        # ---------------------------------------------------------

        return "neutral"