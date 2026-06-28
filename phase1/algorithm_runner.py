import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Dict

from phase1.how_algorithm import calculate_transition_efficiency
from phase1.when_algorithm import calculate_energy_priority
from phase1.what_algorithm import calculate_predictability
from phase1.why_algorithm import calculate_optimization_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def run_algorithms(entity_id: str, window_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the four analytical algorithms (HOW, WHEN, WHAT, WHY) in parallel
    for a single device and assembles their outputs into the six-component
    feature vector used downstream by the K-Means clustering model.

    **Why parallel execution is used:**
    Each of the four algorithms is computationally independent — HOW only needs
    brightness_values, WHEN only needs window_metrics, WHAT only needs the
    state_sequence, and WHY only needs window_metrics.  Running them sequentially
    would mean the total execution time = t_HOW + t_WHEN + t_WHAT + t_WHY.
    Using a ThreadPoolExecutor, all four run concurrently, so the effective
    elapsed time ≈ max(t_HOW, t_WHEN, t_WHAT, t_WHY).  As the number of devices
    and windows scales in Phase 2 (synthetic data), this parallelism becomes
    critical to keeping API response times acceptable.

    **What the six output values represent together:**
    These six values form the feature vector for K-Means clustering (Step 7):
        - transition_efficiency (float, 0-100): HOW — quality of brightness
          transitions; low values indicate abrupt, inefficient dimming behaviour.
        - energy_priority (int, 1-10): WHEN — urgency of energy-saving action;
          high values flag devices that need attention now.
        - predictability (float, 0-100): WHAT — how consistently the device
          follows historical on/off patterns; low values indicate erratic use.
        - optimization_score (float, 0-10): WHY — combined comfort-vs-consumption
          balance; low values indicate poor overall energy behaviour.
        - total_activity (int): Raw count of state transitions; a direct
          measure of how actively the device is being used.
        - variability (float): Standard deviation of brightness; high values
          indicate inconsistent brightness management.

    Args:
        entity_id (str): The unique identifier of the light device.
        window_metrics (Dict[str, Any]): Pre-computed metrics from window_builder.

    Returns:
        Dict[str, Any]: Dictionary with six feature vector components:
            {
                "transition_efficiency": float,
                "energy_priority": int,
                "predictability": float,
                "optimization_score": float,
                "total_activity": int,
                "variability": float,
            }
    """
    brightness_values = window_metrics.get("brightness_values", [])
    state_sequence = window_metrics.get("state_sequence", [])

    logger.info(f"Running algorithms in parallel for '{entity_id}'.")

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all four algorithms concurrently
        future_how: Future = executor.submit(
            calculate_transition_efficiency, brightness_values
        )
        future_when: Future = executor.submit(
            calculate_energy_priority, window_metrics
        )
        future_what: Future = executor.submit(
            calculate_predictability, entity_id, state_sequence
        )
        future_why: Future = executor.submit(
            calculate_optimization_score, window_metrics
        )

        # Collect results — .result() blocks until each future is resolved
        transition_efficiency = future_how.result()
        energy_priority = future_when.result()
        predictability = future_what.result()
        optimization_score = future_why.result()

    # Two additional feature vector components derived directly from window metrics
    total_activity: int = window_metrics.get("transition_count", 0)
    variability: float = window_metrics.get("brightness_std", 0.0)

    result = {
        "transition_efficiency": transition_efficiency,
        "energy_priority": energy_priority,
        "predictability": predictability,
        "optimization_score": optimization_score,
        "total_activity": total_activity,
        "variability": variability,
    }

    logger.info(f"Algorithms complete for '{entity_id}': {result}")
    return result
