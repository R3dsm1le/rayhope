import os
import logging
from typing import Any, Dict, List

from phase2.synthetic_generator import generate_synthetic_dataset, save_to_csv, load_from_csv
from phase2.database import init_db, insert_algorithm_outputs
from phase2.profiles import PROFILES

logger = logging.getLogger(__name__)

CSV_PATH = "phase2/synthetic_dataset.csv"

def run_phase2_pipeline() -> List[Dict[str, Any]]:
    """
    Orchestrates the Phase 2 synthetic data pipeline.
    
    Execution Flow:
        1. Initializes the Phase 2 SQLite database.
        2. Checks for the physical CSV artifact.
            - If missing, mathematically generates a new dataset and saves it to CSV.
            - If present, parses it. Checking for an existing CSV before regenerating 
              ensures strict academic reproducibility — the identical dataset is used 
              across all validation runs.
        3. Persists all 1,500 observations into the SQLite database.
        
    Returns:
        List[Dict[str, Any]]: The full dataset ready for downstream evaluation.
    """
    # 1. Ensure Phase 2 Database exists
    init_db()
    
    # 2. Acquire Data (Load or Generate)
    if os.path.exists(CSV_PATH):
        dataset = load_from_csv(CSV_PATH)
        logger.info("Loaded existing synthetic dataset from CSV.")
    else:
        dataset = generate_synthetic_dataset()
        save_to_csv(dataset, CSV_PATH)
        logger.info("Generated new synthetic dataset and saved to CSV.")
        
    # 3. Persist to SQLite
    logger.info("Beginning database insertion for algorithm outputs...")
    for index, observation in enumerate(dataset):
        device_id = observation["entity_id"]
        cluster_label = observation["cluster_label"]
        
        # We pass the full observation dict which inherently contains all 6 feature keys
        insert_algorithm_outputs(device_id, observation, cluster_label)
        
        if (index + 1) % 100 == 0:
            logger.info(f"Inserted {index + 1} records into database...")
            
    logger.info(f"Phase 2 pipeline complete. Processed {len(dataset)} records.")
    return dataset
