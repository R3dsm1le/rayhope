"""
Gamification Engine

This module handles points, savings calculations, and leaderboard generation.
Gamification mechanisms (competence signals via points, and social comparison via 
leaderboards) are proven to drive sustainable behavioral changes in residential 
energy consumption.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

OPTIMIZATION_THRESHOLD = 6.0
POINTS_PER_WINDOW = 10
ASSUMED_RATED_WATTAGE = 10.0
BASELINE_BRIGHTNESS = 70.0
ASEP_TARIFF_USD_PER_KWH = 0.180


def calculate_points(optimization_score: float) -> int:
    """
    Calculates points earned based on the optimization score.
    
    Points satisfy the competence dimension of Self-Determination Theory (SDT). 
    They signal to the user that their behavior meets an efficiency standard, 
    intrinsically motivating them to maintain good habits.
    
    Args:
        optimization_score (float): The WHY algorithm score.
        
    Returns:
        int: POINTS_PER_WINDOW if threshold met, else 0.
    """
    if optimization_score >= OPTIMIZATION_THRESHOLD:
        return POINTS_PER_WINDOW
    return 0


def calculate_savings(brightness: float, duration_on_minutes: float) -> Dict[str, float]:
    """
    Calculates energy and monetary savings relative to a baseline behavior.
    
    Savings are calculated relative to a baseline brightness rather than zero 
    consumption because the goal is behavioral improvement, not complete disuse 
    (which would compromise comfort). The ASEP tariff grounds the calculation in 
    Panama's actual residential electricity cost.
    
    Args:
        brightness (float): The actual brightness used (0-100).
        duration_on_minutes (float): Total minutes the device was on.
        
    Returns:
        Dict[str, float]: 'savings_kwh' and 'savings_usd'. Returns zeros if negative.
    """
    actual_power = ASSUMED_RATED_WATTAGE * (brightness / 100.0)
    baseline_power = ASSUMED_RATED_WATTAGE * (BASELINE_BRIGHTNESS / 100.0)
    
    savings_kwh = (baseline_power - actual_power) * (duration_on_minutes / 60.0) / 1000.0
    
    if savings_kwh < 0:
        # Do not penalize users who consume more than baseline
        return {"savings_kwh": 0.0, "savings_usd": 0.0}
        
    savings_usd = savings_kwh * ASEP_TARIFF_USD_PER_KWH
    
    return {
        "savings_kwh": round(savings_kwh, 6),
        "savings_usd": round(savings_usd, 6)
    }


def calculate_leaderboard_entry(entity_id: str, optimization_score: float, cluster_label: str) -> Dict[str, Any]:
    """
    Constructs a single entry for the gamification leaderboard.
    
    Includes an injunctive_norm boolean. Pairing leaderboard position with a 
    positive signal for efficient behavior (the injunctive norm) prevents the 
    boomerang effect, where low-consuming users increase their consumption upon 
    seeing they already perform well compared to others.
    
    Args:
        entity_id (str): The device identifier.
        optimization_score (float): The current optimization score.
        cluster_label (str): The current cluster assignment.
        
    Returns:
        Dict[str, Any]: The leaderboard entry.
    """
    points = calculate_points(optimization_score)
    injunctive_norm = optimization_score >= OPTIMIZATION_THRESHOLD
    
    return {
        "entity_id": entity_id,
        "optimization_score": optimization_score,
        "cluster_label": cluster_label,
        "points_earned": points,
        "injunctive_norm": injunctive_norm
    }


def build_leaderboard(entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sorts and ranks leaderboard entries.
    
    Social comparison via leaderboard ranking is the single most cost-effective 
    behavioral mechanism documented at scale in the energy efficiency literature.
    
    Args:
        entries (List[Dict[str, Any]]): The raw list of entry dictionaries.
        
    Returns:
        List[Dict[str, Any]]: Sorted and ranked list.
    """
    # Sort descending by optimization_score
    sorted_entries = sorted(entries, key=lambda x: x["optimization_score"], reverse=True)
    
    # Assign ranks
    for i, entry in enumerate(sorted_entries):
        entry["rank"] = i + 1
        
    return sorted_entries
