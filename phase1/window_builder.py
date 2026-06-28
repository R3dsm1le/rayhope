import logging
import statistics
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _group_by_entity(records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groups a flat list of device records by their entity_id.

    This is a helper that partitions the list returned by data_parser.parse_data()
    so that each device's records can be analysed independently.

    Args:
        records (List[Dict[str, Any]]): Flat list of clean device dictionaries.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Mapping of entity_id → list of records
                                         for that device, preserving insertion order.
    """
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        eid = record["entity_id"]
        grouped.setdefault(eid, []).append(record)
    return grouped


def _compute_window_metrics(device_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes pre-calculated window metrics for a single device's records.

    Metrics are gathered over the current 60-minute analysis window represented
    by the records passed in.  No timestamps are written to disk; all values
    remain in memory.

    Computed metrics:
        transition_count  (int)   — number of state-change events.
        duration_on_minutes (float) — total minutes the device was 'on'.
        brightness_mean   (float) — mean normalised brightness (0-100) during
                                    'on' periods; 0.0 if device was never on.
        brightness_std    (float) — standard deviation of brightness values;
                                    0.0 when fewer than 2 'on' readings exist.
        state_sequence    (list)  — ordered list of states for the WHAT algorithm.
        brightness_values (list)  — ordered brightness values for the HOW algorithm.

    Args:
        device_records (List[Dict[str, Any]]): Ordered records for one device.

    Returns:
        Dict[str, Any]: Dictionary containing the six window metrics listed above.
    """
    transition_count = 0
    on_brightness_values: List[float] = []
    all_brightness_values: List[float] = []
    state_sequence: List[str] = []

    prev_state: str | None = None
    on_record_count = 0  # used to estimate on-time within the window

    for record in device_records:
        current_state = record["state"]
        brightness = record["brightness"]

        state_sequence.append(current_state)
        all_brightness_values.append(brightness)

        # Count a transition whenever the state changes from the previous record
        if prev_state is not None and current_state != prev_state:
            transition_count += 1

        if current_state == "on":
            on_brightness_values.append(brightness)
            on_record_count += 1

        prev_state = current_state

    # Estimate on-duration: assume records are evenly distributed across 60 mins.
    # Each record represents (60 / total_records) minutes; on-records sum to on-time.
    total_records = len(device_records)
    if total_records > 0 and on_record_count > 0:
        minutes_per_record = 60.0 / total_records
        duration_on_minutes = round(on_record_count * minutes_per_record, 2)
    else:
        duration_on_minutes = 0.0

    # Mean brightness during on-periods only
    if on_brightness_values:
        brightness_mean = round(statistics.mean(on_brightness_values), 4)
    else:
        brightness_mean = 0.0

    # Standard deviation of all brightness values (population std; 0.0 if < 2 values)
    if len(all_brightness_values) >= 2:
        brightness_std = round(statistics.stdev(all_brightness_values), 4)
    else:
        brightness_std = 0.0

    return {
        "transition_count": transition_count,
        "duration_on_minutes": duration_on_minutes,
        "brightness_mean": brightness_mean,
        "brightness_std": brightness_std,
        "state_sequence": state_sequence,
        "brightness_values": all_brightness_values,
    }


def build_windows(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Groups parsed device records into 60-minute analysis windows and
    computes per-device metrics ready for algorithm consumption.

    This function is the entry point for the windowing layer.  It accepts the
    output of data_parser.parse_data() and returns one metrics dictionary per
    device, keyed by entity_id.

    Args:
        records (List[Dict[str, Any]]): Clean, normalised device records from
                                        data_parser.parse_data().

    Returns:
        Dict[str, Dict[str, Any]]: Mapping of entity_id → window metrics dict.
                                   Returns an empty dict if records is empty or None.
    """
    if not records:
        logger.warning("build_windows received an empty or None records list.")
        return {}

    grouped = _group_by_entity(records)
    windows: Dict[str, Dict[str, Any]] = {}

    for entity_id, device_records in grouped.items():
        logger.info(
            f"Building window for '{entity_id}' ({len(device_records)} records)."
        )
        windows[entity_id] = _compute_window_metrics(device_records)

    logger.info(f"Windows built for {len(windows)} device(s).")
    return windows
