"""
Synthetic Data Generation Module

This module implements a bottom-up parameterized synthetic data generation approach.
Following the methodology described by Diaz Ramirez et al. (2024) for residential
energy datasets, this generator uses multivariate normal distributions centered around
pre-defined theoretical archetypes to construct a ground-truth dataset for K-Means validation.
"""

import csv
import logging
import os
from typing import Any, Dict, List
import numpy as np

from phase2.profiles import PROFILES

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# A fixed random seed ensures the dataset is exactly reproducible across runs.
# This is a strict requirement for academic validation and peer review, guaranteeing
# that changes in clustering metrics are due to algorithm improvements, not data drift.
np.random.seed(42)

OBSERVATIONS_PER_ARCHETYPE = 500


def _clip(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(value, max_val))


def generate_synthetic_dataset() -> List[Dict[str, Any]]:
    """
    Generates a synthetic dataset of 1500 observations (500 per archetype) using
    multivariate normal sampling based on the ground-truth profile definitions.
    
    Values are mathematically clipped to their valid logical bounds to simulate
    real-world physics (e.g. percentages cannot exceed 100%).
    
    Returns:
        List[Dict[str, Any]]: The generated dataset.
    """
    dataset = []
    
    # Feature vector keys in order
    dimensions = [
        "transition_efficiency",
        "energy_priority",
        "predictability",
        "optimization_score",
        "total_activity",
        "variability"
    ]
    
    for profile_name, params in PROFILES.items():
        # Build mean vector and diagonal covariance matrix
        means = [params[dim]["mean"] for dim in dimensions]
        # Diagonal matrix: std^2 on the diagonal, 0 elsewhere
        cov_matrix = np.diag([params[dim]["std"] ** 2 for dim in dimensions])
        
        # Sample observations for this archetype
        samples = np.random.multivariate_normal(means, cov_matrix, OBSERVATIONS_PER_ARCHETYPE)
        
        for i, sample in enumerate(samples):
            # Clip generated values to valid ranges
            transition_efficiency = _clip(sample[0], 0.0, 100.0)
            energy_priority = round(_clip(sample[1], 1.0, 10.0))
            predictability = _clip(sample[2], 0.0, 100.0)
            optimization_score = _clip(sample[3], 0.0, 10.0)
            total_activity = round(_clip(sample[4], 0.0, 50.0))
            variability = _clip(sample[5], 0.0, 100.0)
            
            entity_id = f"synthetic_{profile_name.lower().replace(' ', '_')}_{i+1:03d}"
            
            observation = {
                "entity_id": entity_id,
                "cluster_label": profile_name,
                "transition_efficiency": round(transition_efficiency, 4),
                "energy_priority": int(energy_priority),
                "predictability": round(predictability, 4),
                "optimization_score": round(optimization_score, 4),
                "total_activity": int(total_activity),
                "variability": round(variability, 4)
            }
            dataset.append(observation)
            
    logger.info(f"Successfully generated {len(dataset)} synthetic observations.")
    return dataset


def save_to_csv(dataset: List[Dict[str, Any]], filepath: str) -> None:
    """
    Writes the dataset to a CSV file.
    
    The CSV serves as a physical, verifiable artifact of the synthetic dataset
    required for thesis documentation and external auditing purposes.
    
    Args:
        dataset (List[Dict[str, Any]]): The list of observation dictionaries.
        filepath (str): The destination file path.
    """
    if not dataset:
        return
        
    keys = [
        "entity_id", "cluster_label", "transition_efficiency", 
        "energy_priority", "predictability", "optimization_score", 
        "total_activity", "variability"
    ]
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(dataset)
        
    logger.info(f"Dataset securely physicalized to CSV artifact at {filepath}")


def load_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """
    Reads the CSV file and reconstructs the strongly-typed dataset dictionary.
    
    Loading from CSV rather than regenerating on the fly ensures absolute consistency — 
    the exact same 1500 observations are used across all subsequent validation runs 
    and model iterations.
    
    Args:
        filepath (str): Path to the synthetic CSV dataset.
        
    Returns:
        List[Dict[str, Any]]: The parsed dataset.
    """
    dataset = []
    
    with open(filepath, mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            observation = {
                "entity_id": row["entity_id"],
                "cluster_label": row["cluster_label"],
                "transition_efficiency": float(row["transition_efficiency"]),
                "energy_priority": int(row["energy_priority"]),
                "predictability": float(row["predictability"]),
                "optimization_score": float(row["optimization_score"]),
                "total_activity": int(row["total_activity"]),
                "variability": float(row["variability"])
            }
            dataset.append(observation)
            
    logger.info(f"Loaded {len(dataset)} observations from existing CSV artifact.")
    return dataset
