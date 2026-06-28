from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from phase1.api_connector import fetch_states
from phase1.data_parser import parse_data
from phase1.window_builder import build_windows
from phase1.algorithm_runner import run_algorithms
from recommendations import get_recommendations, get_primary_recommendation
from gamification import calculate_points, calculate_savings, calculate_leaderboard_entry, build_leaderboard

# Phase 2 — Synthetic data pipeline. Home Assistant API connector is intentionally not called in Phase 2 to maintain GDPR compliance.
from phase2.pipeline import run_phase2_pipeline
from phase2.kmeans_model import run_full_clustering
from phase2.database import get_algorithm_outputs_with_labels, get_all_cluster_assignments
from phase2.validation_suite import (
    test_cluster_consistency,
    test_noise_tolerance,
    test_elbow_analysis,
    test_ground_truth_accuracy,
    test_feature_vector_validity,
    run_full_validation_suite,
)
import os
import time
import logging

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)



@app.get("/api/lights")
def read_lights():
    """
    Returns the current list of parsed and normalised light entity states.
    This endpoint is unchanged from Iteration 1.
    """
    states = fetch_states()
    clean_states = parse_data(states)
    return clean_states


@app.get("/api/metrics")
def read_metrics():
    """
    Runs the full algorithm pipeline and returns the six-component feature vector
    for every active light device.

    Pipeline:
        1. Fetch current entity states from Home Assistant API.
        2. Parse and normalise records (data_parser).
        3. Group records into 60-minute analysis windows (window_builder).
        4. Run HOW / WHEN / WHAT / WHY algorithms in parallel for each device
           (algorithm_runner).
        5. Return a list of per-device result dictionaries.

    Returns:
        List[Dict]: One entry per device, each containing:
            entity_id, transition_efficiency, energy_priority,
            predictability, optimization_score, total_activity, variability.
    """
    states = fetch_states()
    clean_states = parse_data(states)

    if not clean_states:
        return []

    windows = build_windows(clean_states)
    results = []

    for entity_id, window_metrics in windows.items():
        algo_output = run_algorithms(entity_id, window_metrics)
        results.append({"entity_id": entity_id, **algo_output})

    return results

@app.post("/api/phase2/run")
def run_phase2():
    """
    Triggers the Phase 2 synthetic data pipeline.
    
    Generates or loads the synthetic dataset, persists it to the SQLite database, 
    and returns a summary of the operation. This is intended for manual 
    triggering during development and thesis demonstrations.
    """
    csv_existed = os.path.exists("phase2/synthetic_dataset.csv")
    
    # Run the pipeline
    dataset = run_phase2_pipeline()
    
    total_processed = len(dataset)
    archetype_counts = {}
    for obs in dataset:
        label = obs["cluster_label"]
        archetype_counts[label] = archetype_counts.get(label, 0) + 1
        
    return {
        "status": "success",
        "data_source": "Loaded existing CSV" if csv_existed else "Generated new dataset",
        "total_records_processed": total_processed,
        "records_per_archetype": archetype_counts
    }

@app.post("/api/phase2/cluster")
def run_clustering():
    """
    Triggers Phase 2 K-Means validation.
    
    Reads the stored synthetic feature vectors from the SQLite database, 
    runs the K-Means clustering algorithm, persists the dynamic assignments, 
    and returns comprehensive validation metrics.
    """
    result = run_full_clustering()
    return result

@app.get("/api/recommendations/{entity_id}")
def read_recommendations(entity_id: str):
    """
    Returns personalized recommendations for a specific device based on its cluster.
    """
    assignments = get_all_cluster_assignments()
    # Find the most recent assignment for this device
    device_assignments = [a for a in assignments if a["device_id"] == entity_id]
    
    if not device_assignments:
        return {
            "primary": "Run clustering in Phase 2 Validation to unlock personalized recommendations",
            "all": []
        }
        
    latest_assignment = device_assignments[0]
    cluster_label = latest_assignment["cluster_label"]
    
    return {
        "primary": get_primary_recommendation(cluster_label),
        "all": get_recommendations(cluster_label)
    }

@app.get("/api/gamification/{entity_id}")
def read_gamification(entity_id: str):
    """
    Calculates points and savings for a specific device based on the latest metrics.
    """
    all_outputs = get_algorithm_outputs_with_labels()
    device_outputs = [o for o in all_outputs if o["entity_id"] == entity_id]
    
    if not device_outputs:
        return {
            "points_earned": 0,
            "savings_kwh": 0.0,
            "savings_usd": 0.0,
            "optimization_score": 0.0,
            "cluster_label": "Unknown"
        }
        
    latest_output = device_outputs[-1] # assuming order by id asc means last is newest
    
    # We estimate duration on. In a real system this comes from window_metrics.
    # For Phase 2 we use an approximation based on total_activity just to demonstrate the math.
    duration_on = latest_output["total_activity"] * 5.0 
    
    # We estimate brightness. 
    # For Phase 2 we use a constant derived from transition efficiency.
    brightness = max(10, 100 - latest_output["transition_efficiency"])
    
    points = calculate_points(latest_output["optimization_score"])
    savings = calculate_savings(brightness, duration_on)
    
    return {
        "points_earned": points,
        "savings_kwh": savings["savings_kwh"],
        "savings_usd": savings["savings_usd"],
        "optimization_score": latest_output["optimization_score"],
        "cluster_label": latest_output["predicted_label"]
    }

@app.get("/api/leaderboard")
def read_leaderboard():
    """
    Builds the global leaderboard for all devices with injunctive norms.
    """
    all_outputs = get_algorithm_outputs_with_labels()
    
    # Get latest output per device
    latest_per_device = {}
    for output in all_outputs:
        latest_per_device[output["entity_id"]] = output
        
    entries = []
    for entity_id, output in latest_per_device.items():
        if output["predicted_label"]:
            entry = calculate_leaderboard_entry(
                entity_id, 
                output["optimization_score"], 
                output["predicted_label"]
            )
            entries.append(entry)
            
    ranked = build_leaderboard(entries)
    return ranked


# ---------------------------------------------------------------------------
# Thesis Validation Suite — Phase 2 academic validation endpoints.
# Isolated from production pipeline. All endpoints are read-only.
# ---------------------------------------------------------------------------

def _timed_endpoint(name: str, fn):
    """Helper that logs timing for a validation endpoint call."""
    t0 = time.time()
    logger.info(f"Validation endpoint called: {name}")
    result = fn()
    elapsed = round(time.time() - t0, 3)
    logger.info(f"Validation endpoint {name} completed in {elapsed}s")
    return result


@app.get("/api/validation/feature-validity")
def validate_feature_validity():
    """
    Confirms all six algorithm outputs are within valid ranges and non-degenerate.
    Read-only — does not write to the database.
    """
    return _timed_endpoint("feature-validity", test_feature_vector_validity)


@app.get("/api/validation/cluster-consistency")
def validate_cluster_consistency():
    """
    Measures K-Means assignment stability across five independent runs with
    different random seeds. Read-only — does not write to the database.
    """
    return _timed_endpoint("cluster-consistency", test_cluster_consistency)


@app.get("/api/validation/elbow-analysis")
def validate_elbow_analysis():
    """
    Confirms k=3 is the statistically optimal cluster count using inertia
    reduction. Read-only — does not write to the database.
    """
    return _timed_endpoint("elbow-analysis", test_elbow_analysis)


@app.get("/api/validation/noise-tolerance")
def validate_noise_tolerance():
    """
    Tests model robustness when Gaussian noise is added to the feature matrix.
    Read-only — does not write to the database.
    """
    return _timed_endpoint("noise-tolerance", test_noise_tolerance)


@app.get("/api/validation/ground-truth-accuracy")
def validate_ground_truth_accuracy():
    """
    Compares K-Means predicted profiles to synthetic generator ground truth labels.
    Read-only — does not write to the database.
    """
    return _timed_endpoint("ground-truth-accuracy", test_ground_truth_accuracy)


@app.post("/api/validation/run-full-suite")
def validate_full_suite():
    """
    Runs all five validation tests sequentially and returns the complete
    thesis validation report. Read-only — does not write to the database.
    """
    return _timed_endpoint("run-full-suite", run_full_validation_suite)