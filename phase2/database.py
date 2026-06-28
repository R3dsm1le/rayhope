"""
Phase 2 Database Persistence Module

This module implements SQLite persistence specifically for the Phase 2 
synthetic data pipeline. 

GDPR COMPLIANCE NOTE:
This database (`phase2_energy.db`) is physically and logically separated from 
any Phase 1 data. It contains ONLY synthetic, programmatically generated data. 
Because no real personal information or actual behavioral data from the Swedish 
MDU Smart Room is ever written to this file, it remains fully GDPR compliant 
while allowing the system to test and validate long-term storage mechanisms and 
subsequent K-Means clustering.
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = "phase2_energy.db"

@contextmanager
def get_db_connection():
    """Provides a transactional scope around a series of database operations."""
    conn = sqlite3.connect(DB_PATH)
    # Configure to return dict-like rows
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction failed: {e}")
        raise
    finally:
        conn.close()

def init_db() -> None:
    """
    Creates all four essential Phase 2 tables if they do not already exist.
    
    Tables created:
        - sensor_records: Stores raw device state variables.
        - what_frequency: State-transition matrix for the WHAT Markov chain.
        - algorithm_outputs: The 6-D feature vector outputs for each analysis window.
        - cluster_assignments: Validation outputs from the K-Means model (Iteration 5).
        
    Called once at application startup or at the beginning of the Phase 2 pipeline.
    """
    logger.info("Initializing Phase 2 SQLite database schema...")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. sensor_records
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensor_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                device_id TEXT NOT NULL,
                brightness REAL NOT NULL,
                color TEXT,
                estimated_power REAL NOT NULL
            )
        """)
        
        # 2. what_frequency
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS what_frequency (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                count INTEGER DEFAULT 1,
                UNIQUE(device_id, from_state, to_state)
            )
        """)
        
        # 3. algorithm_outputs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS algorithm_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                device_id TEXT NOT NULL,
                transition_efficiency REAL NOT NULL,
                energy_priority REAL NOT NULL,
                predictability REAL NOT NULL,
                optimization_score REAL NOT NULL,
                total_activity INTEGER NOT NULL,
                variability REAL NOT NULL,
                cluster_label TEXT
            )
        """)
        
        # 4. cluster_assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cluster_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                device_id TEXT NOT NULL,
                cluster_label TEXT NOT NULL,
                silhouette_score REAL,
                davies_bouldin_score REAL
            )
        """)
    logger.info(f"Phase 2 database initialized at {DB_PATH}.")

def insert_algorithm_outputs(device_id: str, outputs_dict: Dict[str, Any], cluster_label: Optional[str] = None) -> None:
    """
    Inserts a single computed feature vector (and optional true cluster label) 
    into the database.
    
    Args:
        device_id (str): The unique synthetic entity identifier.
        outputs_dict (Dict[str, Any]): Dictionary containing the 6 computed metrics.
        cluster_label (Optional[str]): The ground-truth archetype profile name.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO algorithm_outputs (
                timestamp, device_id, transition_efficiency, energy_priority, 
                predictability, optimization_score, total_activity, variability, cluster_label
            ) VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            device_id,
            outputs_dict["transition_efficiency"],
            outputs_dict["energy_priority"],
            outputs_dict["predictability"],
            outputs_dict["optimization_score"],
            outputs_dict["total_activity"],
            outputs_dict["variability"],
            cluster_label
        ))

def get_algorithm_outputs(limit: int = 1500) -> List[Dict[str, Any]]:
    """
    Retrieves stored algorithm feature vectors.
    
    This function will be consumed by the K-Means model in Iteration 5 to fetch 
    the accumulated synthetic dataset for clustering validation.
    
    Args:
        limit (int): Max number of rows to return (default 1500).
        
    Returns:
        List[Dict[str, Any]]: The dataset as a list of dictionaries.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM algorithm_outputs 
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
    return [dict(row) for row in rows]

def insert_cluster_assignment(device_id: str, cluster_label: str, silhouette_score: Optional[float] = None, davies_bouldin_score: Optional[float] = None) -> None:
    """
    Stores the final categorization resulting from the K-Means algorithm.
    
    This table explicitly links a device's windowed behaviors to a designated profile, 
    storing standard clustering validation metrics (Silhouette, Davies-Bouldin) 
    if available.
    
    Args:
        device_id (str): The unique synthetic entity identifier.
        cluster_label (str): The assigned archetype name.
        silhouette_score (Optional[float]): Metric indicating cluster cohesion.
        davies_bouldin_score (Optional[float]): Metric indicating cluster separation.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cluster_assignments (
                timestamp, device_id, cluster_label, silhouette_score, davies_bouldin_score
            ) VALUES (datetime('now'), ?, ?, ?, ?)
        """, (
            device_id, cluster_label, silhouette_score, davies_bouldin_score
        ))

def get_all_cluster_assignments() -> List[Dict[str, Any]]:
    """
    Retrieves all historical cluster assignments.
    
    Returns:
        List[Dict[str, Any]]: The assignments as a list of dictionaries.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cluster_assignments ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        
    return [dict(row) for row in rows]

def get_algorithm_outputs_with_labels() -> List[Dict[str, Any]]:
    """
    Retrieves all algorithm outputs joined with their K-Means cluster assignments.
    
    This pairs the 'ground truth' labels (from algorithm_outputs) with the 
    'predicted' labels (from cluster_assignments) for use in Iteration 6 
    validation reporting.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing entity_id, the 
        six feature values, ground_truth_label, and predicted_label.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                a.device_id as entity_id,
                a.transition_efficiency,
                a.energy_priority,
                a.predictability,
                a.optimization_score,
                a.total_activity,
                a.variability,
                a.cluster_label as ground_truth_label,
                c.cluster_label as predicted_label
            FROM algorithm_outputs a
            INNER JOIN cluster_assignments c ON a.device_id = c.device_id
            ORDER BY a.id ASC
        """)
        rows = cursor.fetchall()
        
    return [dict(row) for row in rows]
