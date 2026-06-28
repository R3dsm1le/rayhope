import heapq
import logging
from typing import Any, Dict, List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Thresholds used to detect energy-saving opportunities
_LONG_DURATION_THRESHOLD_MINUTES = 45.0   # on for ≥ 45 min flags a duration opportunity
_HIGH_BRIGHTNESS_THRESHOLD = 70.0         # brightness ≥ 70 flags an intensity opportunity
_UNOCCUPIED_BRIGHTNESS_THRESHOLD = 50.0   # brightness above this during likely unoccupied periods


def _detect_opportunities(window_metrics: Dict[str, Any]) -> List[Tuple[float, str]]:
    """
    Inspects the window metrics and builds a list of energy-saving opportunities,
    each paired with a composite priority score.

    **How priority scores are assigned:**
    Each opportunity is scored as a weighted combination of urgency (driven by
    duration_on_minutes — the longer a device has been on, the more urgent the
    saving) and estimated efficiency gain (driven by brightness_mean — brighter
    devices have more headroom to reduce consumption).

    A LOWER score means HIGHER priority (MinHeap convention).  This mirrors how a
    task scheduler assigns priority: the most critical item is served first.

    Args:
        window_metrics (Dict[str, Any]): Pre-computed metrics from window_builder.

    Returns:
        List[Tuple[float, str]]: List of (priority_score, description) tuples.
    """
    opportunities: List[Tuple[float, str]] = []

    duration = window_metrics.get("duration_on_minutes", 0.0)
    brightness = window_metrics.get("brightness_mean", 0.0)
    transitions = window_metrics.get("transition_count", 0)

    # Opportunity 1 — Extended on-duration
    if duration >= _LONG_DURATION_THRESHOLD_MINUTES:
        # Urgency increases with duration; efficiency gain increases with brightness.
        # Lower score → higher priority (MinHeap).
        urgency = duration / 60.0               # normalised to [0, 1] over 60-min window
        gain = brightness / 100.0               # normalised brightness
        priority = round(1.0 - (0.6 * urgency + 0.4 * gain), 6)
        opportunities.append((priority, "Extended on-duration detected"))

    # Opportunity 2 — Sustained high brightness
    if brightness >= _HIGH_BRIGHTNESS_THRESHOLD:
        urgency = duration / 60.0
        gain = brightness / 100.0
        priority = round(1.0 - (0.4 * urgency + 0.6 * gain), 6)
        opportunities.append((priority, "Sustained high brightness detected"))

    # Opportunity 3 — Erratic switching (many transitions suggest occupancy uncertainty)
    if transitions >= 5:
        urgency = min(transitions / 20.0, 1.0)  # cap at 20 transitions
        gain = brightness / 100.0
        priority = round(1.0 - (0.5 * urgency + 0.5 * gain), 6)
        opportunities.append((priority, "Frequent state transitions detected"))

    return opportunities


def _map_priority_to_scale(raw_priority: float) -> int:
    """
    Converts a raw MinHeap priority score (lower = more urgent) into an
    intuitive 1-10 integer scale (higher = more savings potential).

    A raw score near 0.0 means very high urgency → maps to 10.
    A raw score near 1.0 means low urgency → maps to 1.

    Args:
        raw_priority (float): The raw composite priority score from the MinHeap.

    Returns:
        int: Energy priority score in the range [1, 10].
    """
    score = round((1.0 - raw_priority) * 10)
    return max(1, min(10, score))


def calculate_energy_priority(window_metrics: Dict[str, Any]) -> int:
    """
    Uses a MinHeap priority queue to identify and rank the highest-priority
    energy-saving opportunity detected in the current analysis window.

    **What the MinHeap does:**
    A MinHeap is a data structure where the item with the SMALLEST value always
    sits at the top and is retrieved in O(1) time.  Here, we assign lower scores
    to more urgent opportunities, so the MinHeap always surfaces the most
    critical saving first — exactly like a hospital triage system.

    **Why priority-based scheduling is used:**
    In a real smart home, multiple devices may simultaneously show inefficiencies.
    Rather than treating all issues equally, a priority queue ensures the system
    directs user attention to the action that will save the most energy NOW.
    This mimics how real-time operating systems schedule CPU tasks: the highest-
    priority job runs first.

    **Algorithm:**
        1. Inspect window metrics and generate a list of detected opportunities.
        2. Push each opportunity onto a Python MinHeap (heapq).
        3. Pop the top item — the highest-priority (lowest raw score) opportunity.
        4. Convert its raw score to a 1-10 integer scale and return it.
        5. If no opportunities are detected, return a baseline score of 1.

    Args:
        window_metrics (Dict[str, Any]): Pre-computed metrics from window_builder.

    Returns:
        int: Energy priority score in the range [1, 10].
             10 = highest savings urgency, 1 = no significant opportunity detected.
    """
    opportunities = _detect_opportunities(window_metrics)

    if not opportunities:
        logger.debug("No energy-saving opportunities detected. Returning baseline score 1.")
        return 1

    # Build the MinHeap from detected opportunities
    heap: List[Tuple[float, str]] = []
    for item in opportunities:
        heapq.heappush(heap, item)

    # Pop the highest-priority (lowest raw score) item
    top_priority, description = heapq.heappop(heap)
    logger.debug(f"Top opportunity: '{description}' with raw priority {top_priority:.4f}")

    return _map_priority_to_scale(top_priority)
