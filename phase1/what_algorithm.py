import logging
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level in-memory frequency table
# ---------------------------------------------------------------------------
# This dictionary persists for the lifetime of the Python process (the session)
# and is NEVER written to disk, in strict compliance with GDPR Phase 1.
#
# Structure:
#   frequency_table[entity_id][current_state][next_state] = count (int)
#
# Example:
#   {"light.desk": {"on": {"off": 4, "on": 1}, "off": {"on": 3, "off": 2}}}
# ---------------------------------------------------------------------------
frequency_table: Dict[str, Dict[str, Dict[str, int]]] = {}


def update_frequency_table(entity_id: str, state_sequence: List[str]) -> None:
    """
    Updates the in-memory frequency table with state-transition counts observed
    in the given state sequence for a specific device.

    **What this implements (first-order Markov chain):**
    A first-order Markov chain models the probability of transitioning from one
    state to another based solely on the CURRENT state — it has no memory of
    states before the current one.  Here each consecutive pair of states in the
    sequence (s_i → s_{i+1}) is counted as one observed transition.  Over many
    windows, the table accumulates an empirical distribution of how this device
    tends to behave.

    **Why session-only storage (Phase 1 — GDPR):**
    The MDU Smart Room data originates in Sweden and is subject to GDPR.
    Writing per-device behavioural history to disk would constitute persistent
    profiling of identifiable smart-home occupants.  By keeping the frequency
    table in RAM only, all data is automatically erased when the process ends,
    eliminating any storage of personal behavioural patterns.

    Args:
        entity_id (str): The unique identifier of the light device.
        state_sequence (List[str]): Ordered list of states recorded in the window.
    """
    if entity_id not in frequency_table:
        frequency_table[entity_id] = {}

    device_table = frequency_table[entity_id]

    for i in range(len(state_sequence) - 1):
        current_state = state_sequence[i]
        next_state = state_sequence[i + 1]

        if current_state not in device_table:
            device_table[current_state] = {}

        device_table[current_state][next_state] = (
            device_table[current_state].get(next_state, 0) + 1
        )

    logger.debug(
        f"Frequency table updated for '{entity_id}' "
        f"from sequence of length {len(state_sequence)}."
    )


def predict_next_state(entity_id: str, current_state: str) -> float:
    """
    Looks up the in-memory frequency table to predict the most probable next
    state for the given device and returns a confidence percentage.

    If no transition history exists for the device or for the current state,
    returns 50.0 — a neutral prior indicating maximum uncertainty (equivalent
    to a coin flip between 'on' and 'off').

    **Why 50.0 as the neutral prior:**
    Without any observed data, assuming equal probability for each possible
    next state is the maximum-entropy (least-biased) prior.  It prevents the
    algorithm from making confident — and potentially wrong — recommendations
    before sufficient data has accumulated.

    Args:
        entity_id (str): The unique identifier of the light device.
        current_state (str): The device's most recently observed state.

    Returns:
        float: Confidence percentage in the range [0.0, 100.0].
               Represents the probability that the device will transition to
               its historically most likely next state.
    """
    if entity_id not in frequency_table:
        logger.debug(
            f"No history for '{entity_id}' — returning neutral prior 50.0."
        )
        return 50.0

    device_table = frequency_table[entity_id]

    if current_state not in device_table:
        logger.debug(
            f"No transitions observed from state '{current_state}' "
            f"for '{entity_id}' — returning neutral prior 50.0."
        )
        return 50.0

    transitions = device_table[current_state]
    total_transitions = sum(transitions.values())

    if total_transitions == 0:
        return 50.0

    # Most probable next state
    best_next_state = max(transitions, key=lambda s: transitions[s])
    confidence = (transitions[best_next_state] / total_transitions) * 100.0

    logger.debug(
        f"'{entity_id}' from '{current_state}' → predicted '{best_next_state}' "
        f"with confidence {confidence:.2f}%."
    )
    return round(confidence, 4)


def calculate_predictability(entity_id: str, state_sequence: List[str]) -> float:
    """
    Orchestrates the WHAT algorithm for a single device in one window:
    first updates the frequency table with newly observed transitions, then
    queries it to return a predictability confidence score.

    **What predictability represents:**
    A high score means the device follows consistent, repeatable on/off patterns —
    the system can anticipate its next state with confidence.  A low score means
    erratic, hard-to-predict behaviour, which is often associated with wasteful
    usage (lights left on without purpose, or toggled randomly).

    Args:
        entity_id (str): The unique identifier of the light device.
        state_sequence (List[str]): Ordered list of states from the current window.

    Returns:
        float: Predictability confidence score in the range [0.0, 100.0].
               50.0 indicates no historical data (session start neutral prior).
    """
    update_frequency_table(entity_id, state_sequence)

    if not state_sequence:
        return 50.0

    current_state = state_sequence[-1]
    return predict_next_state(entity_id, current_state)
