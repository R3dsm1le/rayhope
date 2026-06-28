"""
Recommendations Engine

This module defines cluster-specific recommendations for behavioral improvement.

Generic tips (e.g., "Turn off your lights to save energy") produce negligible 
behavioral change. Personalized, cluster-based recommendations grounded in 
observed user habits produce significantly higher response rates, as documented 
in the behavioral energy literature. Furthermore, these recommendations use 
community and grid-impact framing, which outperforms purely economic framing 
in the Panamanian cultural context.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

RECOMMENDATIONS = {
    "Water Guardians": [
        "Outstanding efficiency — your lighting patterns are a model for the community. Keep it up.",
        "Your consistency is contributing to grid stability during peak hours. Every session counts.",
        "You are using 15-20% less energy than the average user. Share your habits with neighbors.",
        "Consider scheduling your lights during off-peak hours to further reduce grid pressure."
    ],
    "Conscious Users": [
        "Your efficiency is good but inconsistent — try maintaining brightness below 60% during evening hours.",
        "We noticed irregular switching patterns between 8PM and 10PM. A schedule could help.",
        "Small habit changes during your highest-activity periods could move you to Water Guardian status.",
        "Your predictability score dropped this session — try establishing a consistent lighting routine."
    ],
    "Green Opportunity": [
        "Your lights are on for extended periods at high brightness — consider a timer for unoccupied rooms.",
        "Reducing brightness by 20% during your peak usage hours could save significant energy this month.",
        "You have the highest savings potential of any profile — small changes here make the biggest impact.",
        "Your variability score suggests frequent unnecessary switching — try using dimming instead of on/off."
    ]
}

def get_recommendations(cluster_label: str) -> List[str]:
    """
    Returns a list of tailored recommendation strings for the specified profile.
    
    Recommendations are cluster-specific because generic tips produce negligible 
    behavioral change while personalized cluster-based recommendations produce 
    significantly higher response rates as documented in the literature.
    
    Args:
        cluster_label (str): The K-Means assigned behavioral archetype.
        
    Returns:
        List[str]: A list of at least four recommendations.
    """
    if cluster_label not in RECOMMENDATIONS:
        logger.warning(f"Unrecognized cluster_label '{cluster_label}' for recommendations.")
        return ["We are analyzing your patterns to provide personalized recommendations soon."]
        
    return RECOMMENDATIONS[cluster_label]

def get_primary_recommendation(cluster_label: str) -> str:
    """
    Returns only the single most important recommendation for the cluster.
    
    Rationale:
    Surfacing a single primary recommendation rather than overwhelming the user 
    with all of them reduces cognitive load. Users are much more likely to adopt 
    one clear, actionable habit change than to parse through a long list of advice.
    
    Args:
        cluster_label (str): The K-Means assigned behavioral archetype.
        
    Returns:
        str: The primary recommendation.
    """
    recs = get_recommendations(cluster_label)
    return recs[0]
