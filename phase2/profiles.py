"""
Behavioral Archetype Definitions

This module defines the three behavioral archetypes used to generate synthetic data
for Phase 2 of the Energy Awareness System.

METHODOLOGICAL DECISION:
These parameters were defined top-down BEFORE any data generation occurred. This is a
deliberate methodological choice following Diaz Ramirez et al. (2024) for residential 
energy datasets. The profiles serve as the "ground truth" representing theoretically 
distinct consumer behaviors. They are not inferred from existing data; rather, the 
data is generated to reflect these theoretical constructs to validate the K-Means 
model's ability to recover them.
"""

PROFILES = {
    "Water Guardians": {
        # High efficiency, consistent behavior, low energy waste.
        # High predictability because their habits are rigid and repeatable.
        # Low activity because they turn lights on only when needed and leave them.
        "transition_efficiency": {"mean": 90.0, "std": 6.0},
        "energy_priority": {"mean": 2.0, "std": 0.5},
        "predictability": {"mean": 88.0, "std": 6.0},
        "optimization_score": {"mean": 9.0, "std": 0.6},
        "total_activity": {"mean": 3.0, "std": 2.0},
        "variability": {"mean": 6.0, "std": 5.0},
    },
    "Conscious Users": {
        # Medium efficiency, inconsistent patterns, targeted recommendations.
        # Low predictability specifically because their behavior fluctuates based on
        # external factors rather than strict routines.
        "transition_efficiency": {"mean": 58.0, "std": 6.0},
        "energy_priority": {"mean": 5.0, "std": 0.5},
        "predictability": {"mean": 52.0, "std": 6.0},
        "optimization_score": {"mean": 5.0, "std": 0.6},
        "total_activity": {"mean": 13.0, "std": 2.0},
        "variability": {"mean": 28.0, "std": 5.0},
    },
    "Green Opportunity": {
        # Low efficiency, high activity, highest savings potential.
        # High activity and high variability because they toggle lights frequently
        # and leave them on at arbitrary, often unnecessary, brightness levels.
        "transition_efficiency": {"mean": 22.0, "std": 6.0},
        "energy_priority": {"mean": 8.0, "std": 0.5},
        "predictability": {"mean": 28.0, "std": 6.0},
        "optimization_score": {"mean": 2.0, "std": 0.6},
        "total_activity": {"mean": 25.0, "std": 2.0},
        "variability": {"mean": 52.0, "std": 5.0},
    }
}