import logging
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def calculate_transition_efficiency(brightness_values: List[float]) -> float:
    """
    Calculates how smoothly and efficiently a light device transitions between
    brightness levels during the analysis window.

    **What linear interpolation means here:**
    Given the FIRST and LAST brightness values recorded for a device, we draw
    an imaginary straight line between them — the theoretically optimal, most
    energy-efficient path a dimmer could take to go from start to end.
    Every intermediate observed reading is then compared against the point on
    that straight line at the same relative position.  The closer each observed
    reading is to the ideal straight-line value, the more efficient the
    transition was.

    **Why this measures efficiency:**
    Abrupt jumps to full brightness followed by sudden drops waste energy and
    reduce lamp lifespan.  A gradual, linear dimming curve minimises peak power
    draw and smooths the load on the electrical circuit.  A device that
    perfectly follows the linear path scores 100; one that spikes or dips
    erratically scores closer to 0.

    Algorithm:
        1. If fewer than 2 readings exist there is no transition to evaluate —
           return 100.0 (perfect by default, no penalty).
        2. Build the ideal linear path between index 0 and index n-1.
        3. For each intermediate index i, compute the absolute deviation of the
           observed value from the ideal value.
        4. Normalise each deviation against the maximum possible deviation
           (the full 0-100 brightness range).
        5. Average the normalised deviations and subtract from 100.

    Args:
        brightness_values (List[float]): Ordered brightness readings (0-100 scale)
                                         from the current analysis window.

    Returns:
        float: Transition efficiency score in the range [0.0, 100.0].
               Higher is better.  100.0 means a perfectly linear transition.
    """
    n = len(brightness_values)

    if n < 2:
        logger.debug(
            "Fewer than 2 brightness readings — returning perfect efficiency (100.0)."
        )
        return 100.0

    start = brightness_values[0]
    end = brightness_values[-1]

    # If start and end are identical there is no net transition; score is 100.
    if n == 2 or start == end:
        return 100.0

    total_deviation = 0.0
    intermediate_count = n - 2  # exclude first and last points

    for i in range(1, n - 1):
        # Ideal value at position i along the straight line from start to end
        ideal = start + (end - start) * (i / (n - 1))
        deviation = abs(brightness_values[i] - ideal)
        # Normalise: max possible deviation is the full 100-point range
        total_deviation += deviation / 100.0

    mean_normalised_deviation = total_deviation / intermediate_count
    efficiency = round(max(0.0, 100.0 - (mean_normalised_deviation * 100.0)), 4)

    logger.debug(f"Transition efficiency calculated: {efficiency:.2f}")
    return efficiency
