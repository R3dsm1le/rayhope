"""
K-Means Clustering Model

This module implements the core unsupervised learning algorithm for Phase 2.
It consumes the synthetic feature vectors and clusters them into three behavioral
profiles, validating the model's ability to recover the "ground truth" archetypes.
"""

import logging
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score

from phase2.database import get_algorithm_outputs, insert_cluster_assignment

logger = logging.getLogger(__name__)

# The exact order of the six feature vector dimensions
FEATURE_COLUMNS = [
    "transition_efficiency",
    "energy_priority",
    "predictability",
    "optimization_score",
    "total_activity",
    "variability"
]

def load_feature_matrix() -> Tuple[pd.DataFrame, np.ndarray]:
    """
    Retrieves all 1500 stored observations from the database and constructs 
    the feature matrix.
    
    A feature matrix is a 2D mathematical array where rows are observations (devices) 
    and columns are the measurable variables (features). We strictly use only the 
    six analytical dimensions because including raw identifiers (like entity_id) 
    would fundamentally break the distance calculations used by K-Means.
    
    Returns:
        Tuple[pd.DataFrame, np.ndarray]: The full dataframe and the raw 6-column matrix.
    """
    data = get_algorithm_outputs(limit=1500)
    df = pd.DataFrame(data)
    feature_matrix = df[FEATURE_COLUMNS].values
    return df, feature_matrix

def normalize_features(feature_matrix: np.ndarray) -> Tuple[np.ndarray, StandardScaler]:
    """
    Applies zero-mean, unit-variance normalization to the feature matrix.
    
    Normalization is an absolute mathematical necessity before applying K-Means. 
    K-Means relies on Euclidean distance to determine similarity. Without scaling, 
    a dimension with a naturally large range (like transition_efficiency 0-100) 
    would disproportionately dominate the distance calculation over a smaller-range 
    dimension (like energy_priority 1-10), skewing the clusters.
    
    Args:
        feature_matrix (np.ndarray): The raw M x 6 matrix.
        
    Returns:
        Tuple[np.ndarray, StandardScaler]: The scaled matrix and the fitted scaler object.
    """
    scaler = StandardScaler()
    normalized_matrix = scaler.fit_transform(feature_matrix)
    return normalized_matrix, scaler

def run_elbow_analysis(normalized_matrix: np.ndarray) -> Dict[int, float]:
    """
    Calculates K-Means inertia for multiple values of k to determine the optimal 
    number of clusters.
    
    The 'elbow method' plots inertia (within-cluster sum of squares) against k. 
    The ideal k is the point where adding more clusters yields diminishing returns 
    in inertia reduction — creating an "elbow" shape on a graph. Because the 
    synthetic data was explicitly generated using exactly three archetypes, we 
    expect the elbow to manifest strongly at k=3.
    
    Args:
        normalized_matrix (np.ndarray): Scaled feature matrix.
        
    Returns:
        Dict[int, float]: Mapping of k to its corresponding inertia value.
    """
    inertia_map = {}
    for k in range(2, 7):
        # random_state=42 ensures reproducibility of the elbow curve
        kmeans = KMeans(n_clusters=k, init='k-means++', n_init=10, random_state=42)
        kmeans.fit(normalized_matrix)
        inertia_map[k] = float(kmeans.inertia_)
    return inertia_map

def assign_cluster_labels(kmeans_model: KMeans, scaler: StandardScaler) -> Dict[int, str]:
    """
    Dynamically maps internal K-Means cluster indices (0, 1, 2) to the human-readable 
    behavioral archetype names.
    
    Why dynamic assignment? K-Means initializes randomly, meaning it does not 
    guarantee consistent ordering of cluster indices across different runs. Index 0 
    might be "Water Guardians" today and "Conscious Users" tomorrow. We must inspect 
    the actual mathematical centroids to figure out which profile each index represents.
    
    Logic:
        - Water Guardians: Highest transition_efficiency, lowest total_activity.
        - Conscious Users: Lowest predictability, medium transition_efficiency.
        - Green Opportunity: Highest total_activity, lowest transition_efficiency.
        
    Args:
        kmeans_model (KMeans): The fitted clustering model.
        scaler (StandardScaler): The scaler used to normalize the data.
        
    Returns:
        Dict[int, str]: Mapping of integer indices to string profile names.
    """
    # Inverse transform to read centroids in their original units
    centroids_raw = scaler.inverse_transform(kmeans_model.cluster_centers_)
    
    # Indices of specific features based on FEATURE_COLUMNS order
    idx_eff = FEATURE_COLUMNS.index("transition_efficiency")
    idx_act = FEATURE_COLUMNS.index("total_activity")
    idx_pred = FEATURE_COLUMNS.index("predictability")
    
    label_map = {}
    
    for cluster_idx, centroid in enumerate(centroids_raw):
        eff = centroid[idx_eff]
        act = centroid[idx_act]
        pred = centroid[idx_pred]
        
        # Determine archetype based on predefined ground-truth characteristics
        if eff > 70 and act < 10:
            label_map[cluster_idx] = "Water Guardians"
        elif eff < 50 and act > 15:
            label_map[cluster_idx] = "Green Opportunity"
        else:
            label_map[cluster_idx] = "Conscious Users"
            
    # Fallback to ensure unique labels if the simple heuristic overlaps slightly
    if len(set(label_map.values())) < 3:
        logger.warning("Dynamic label heuristics collided. Falling back to rank-based mapping.")
        eff_scores = [(i, c[idx_eff]) for i, c in enumerate(centroids_raw)]
        eff_scores.sort(key=lambda x: x[1], reverse=True) # High to Low
        label_map[eff_scores[0][0]] = "Water Guardians"
        label_map[eff_scores[1][0]] = "Conscious Users"
        label_map[eff_scores[2][0]] = "Green Opportunity"
        
    return label_map

def run_kmeans(normalized_matrix: np.ndarray) -> Tuple[KMeans, np.ndarray]:
    """
    Executes the K-Means algorithm to partition the dataset.
    
    KMeans++ initialization spreads out the initial cluster centers strategically 
    rather than randomly, accelerating convergence and preventing poor clustering. 
    n_init=10 forces the algorithm to run 10 separate times with different 
    initializations and keep the result with the lowest inertia, preventing it 
    from getting trapped in a local minimum.
    
    Args:
        normalized_matrix (np.ndarray): Scaled feature matrix.
        
    Returns:
        Tuple[KMeans, np.ndarray]: The fitted model and the array of cluster indices.
    """
    kmeans = KMeans(n_clusters=3, init='k-means++', n_init=10, random_state=42)
    cluster_assignments = kmeans.fit_predict(normalized_matrix)
    return kmeans, cluster_assignments

def evaluate_clustering(normalized_matrix: np.ndarray, cluster_assignments: np.ndarray) -> Dict[str, float]:
    """
    Calculates mathematically rigorous validation metrics for the clustering output.
    
    - Silhouette Coefficient (-1 to 1): Measures how similar each point is to its 
      own cluster compared to neighboring clusters. Higher is better. Target > 0.5.
    - Davies-Bouldin Index (0 to infinity): Measures the ratio of within-cluster 
      scatter to between-cluster separation. Lower is better. Target < 1.0.
      
    Args:
        normalized_matrix (np.ndarray): Scaled feature matrix.
        cluster_assignments (np.ndarray): The predicted cluster indices.
        
    Returns:
        Dict[str, float]: The calculated metrics.
    """
    silhouette = float(silhouette_score(normalized_matrix, cluster_assignments))
    davies_bouldin = float(davies_bouldin_score(normalized_matrix, cluster_assignments))
    
    return {
        "silhouette_coefficient": silhouette,
        "davies_bouldin_index": davies_bouldin
    }

def run_full_clustering() -> Dict[str, Any]:
    """
    Orchestrates the complete Phase 2 K-Means clustering pipeline.
    
    From extracting raw vectors from the database, through normalization, execution, 
    evaluation, and finally persisting the predicted assignments back to SQLite.
    
    Returns:
        Dict[str, Any]: A comprehensive summary dictionary for the API endpoint.
    """
    logger.info("Starting Phase 2 K-Means validation pipeline...")
    
    df, feature_matrix = load_feature_matrix()
    if df.empty:
        logger.error("No algorithm outputs found in DB. Run the generation pipeline first.")
        return {"error": "No data available."}
        
    normalized_matrix, scaler = normalize_features(feature_matrix)
    
    # 1. Elbow Analysis
    elbow_results = run_elbow_analysis(normalized_matrix)
    logger.info(f"Elbow Analysis Inertia: {elbow_results}")
    
    # 2. Run Clustering
    kmeans_model, assignments = run_kmeans(normalized_matrix)
    
    # 3. Dynamic Labeling
    label_map = assign_cluster_labels(kmeans_model, scaler)
    logger.info(f"Dynamic Cluster Mapping: {label_map}")
    
    # 4. Evaluation
    metrics = evaluate_clustering(normalized_matrix, assignments)
    logger.info(f"Validation Metrics: {metrics}")
    
    # 5. Persist Assignments and Calculate Counts
    cluster_counts = {"Water Guardians": 0, "Conscious Users": 0, "Green Opportunity": 0}
    
    logger.info("Persisting cluster assignments to database...")
    for i, row in df.iterrows():
        entity_id = row["device_id"]
        predicted_idx = int(assignments[i])
        predicted_label = label_map[predicted_idx]
        
        cluster_counts[predicted_label] += 1
        
        insert_cluster_assignment(
            device_id=entity_id,
            cluster_label=predicted_label,
            silhouette_score=metrics["silhouette_coefficient"],
            davies_bouldin_score=metrics["davies_bouldin_index"]
        )
        
    return {
        "silhouette_coefficient": metrics["silhouette_coefficient"],
        "davies_bouldin_index": metrics["davies_bouldin_index"],
        "cluster_label_map": label_map,
        "cluster_counts": cluster_counts,
        "elbow_analysis": elbow_results
    }
