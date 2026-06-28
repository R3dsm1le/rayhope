import logging
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Weight configuration — comfort is prioritised over raw consumption reduction
_COMFORT_WEIGHT = 0.7
_CONSUMPTION_WEIGHT = 0.3

# Minimum brightness level considered comfortable for occupied residential spaces.
# Based on the IESNA (Illuminating Engineering Society of North America) guideline
# of ≥ 200 lux for general residential use, which maps roughly to ≥ 40% on the
# 0-100 normalised brightness scale used by this system.
_MIN_COMFORTABLE_BRIGHTNESS = 40.0

# Total minutes in a single analysis window
_WINDOW_MINUTES = 60.0


def _compute_comfort_score(brightness_mean: float) -> float:
    """
    Computes a comfort preservation score from the mean brightness during on-periods.

    A score of 1.0 means brightness was comfortably above the minimum threshold.
    A score of 0.0 means the device was dark (brightness at or below threshold).

    The score scales linearly between 0 and the minimum threshold, then stays at
    1.0 for any brightness above the threshold, rewarding adequate lighting without
    penalising brighter settings (a dimly lit room reduces comfort, not vice versa).

    Args:
        brightness_mean (float): Mean normalised brightness (0-100 scale).

    Returns:
        float: Comfort score in the range [0.0, 1.0].
    """
    if brightness_mean >= _MIN_COMFORTABLE_BRIGHTNESS:
        return 1.0
    # Linear ramp from 0.0 to 1.0 as brightness approaches the comfortable threshold
    return round(brightness_mean / _MIN_COMFORTABLE_BRIGHTNESS, 6)


def _compute_consumption_score(duration_on_minutes: float) -> float:
    """
    Computes a consumption reduction score from the device's on-duration.

    A higher score means less time on (less energy consumed relative to the full
    window).  The score is the complement of the fraction of the window spent on.

    Score = 1.0 → device was off the entire window (zero consumption).
    Score = 0.0 → device was on for the full 60-minute window.

    Args:
        duration_on_minutes (float): Minutes the device was in the 'on' state.

    Returns:
        float: Consumption reduction score in the range [0.0, 1.0].
    """
    fraction_on = min(duration_on_minutes / _WINDOW_MINUTES, 1.0)
    return round(1.0 - fraction_on, 6)


def calculate_optimization_score(window_metrics: Dict[str, Any]) -> float:
    """
    Computes a weighted optimization score that balances user comfort against
    energy consumption reduction for a single device in one analysis window.

    **Component weights and rationale:**
        - Comfort preservation weight: 0.7 (70%)
        - Consumption reduction weight: 0.3 (30%)

    **Why comfort is weighted higher than consumption reduction:**
    The thesis addresses energy demand-side management, not energy deprivation.
    Recommendations that force users into uncomfortable lighting conditions will
    be ignored or will cause the system to be disabled entirely — the worst
    possible outcome.  Behavioural research (Abrahamse et al., 2005; Fischer,
    2008) consistently shows that energy-saving interventions succeed only when
    they preserve perceived quality of life.  Weighting comfort at 0.7 ensures
    the system recommends reductions that are genuinely achievable and acceptable,
    while still rewarding efficient usage patterns (0.3 consumption weight).

    **Score interpretation:**
        0.0 — very low comfort AND very high consumption (worst case).
        5.0 — balanced: adequate comfort with moderate consumption.
       10.0 — comfortable lighting AND minimal consumption (best case).

    Args:
        window_metrics (Dict[str, Any]): Pre-computed metrics from window_builder.

    Returns:
        float: Optimization score in the range [0.0, 10.0].
               Higher scores indicate better energy-aware behaviour.
    """
    brightness_mean = window_metrics.get("brightness_mean", 0.0)
    duration_on_minutes = window_metrics.get("duration_on_minutes", 0.0)

    comfort_score = _compute_comfort_score(brightness_mean)
    consumption_score = _compute_consumption_score(duration_on_minutes)

    # Weighted combination of both components (each in [0.0, 1.0])
    combined = (
        _COMFORT_WEIGHT * comfort_score
        + _CONSUMPTION_WEIGHT * consumption_score
    )

    # Scale to [0.0, 10.0] for a more intuitive output
    final_score = round(combined * 10.0, 4)

    logger.debug(
        f"WHY score: comfort={comfort_score:.4f} (×{_COMFORT_WEIGHT}), "
        f"consumption={consumption_score:.4f} (×{_CONSUMPTION_WEIGHT}) "
        f"→ final={final_score}"
    )
    return final_score
