"""
Output Writer Module for ERH Simulation
Handles saving simulation results and metadata to structured formats (JSON, CSV).
"""

import json
import csv
import os
from datetime import datetime
from typing import Dict, Any, List

def save_json_result(result: Dict[str, Any], output_dir: str, file_prefix: str = "sim_result") -> str:
    """
    Save simulation result dictionary to a JSON file.
    Returns the path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct filename
    # Try to get config info for filename, otherwise use timestamp
    config = result.get("config", {})
    dist = config.get("complexity_dist", "unknown")
    n = config.get("num_actions", 0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{file_prefix}_{dist}_N{n}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2)
        
    return filepath

def save_csv_summary(results: List[Dict[str, Any]], output_path: str):
    """
    Save a list of simulation results to a CSV summary file.
    """
    if not results:
        return
        
    # Flatten the dictionary for CSV
    flat_results = []
    for r in results:
        flat = {}
        flat['timestamp'] = r.get('timestamp')
        
        # Config
        config = r.get('config', {})
        for k, v in config.items():
            flat[f"config_{k}"] = v
            
        # Metrics
        metrics = r.get('metrics', {})
        for k, v in metrics.items():
            flat[f"metric_{k}"] = v
            
        flat_results.append(flat)
        
    keys = flat_results[0].keys()
    
    # Write CSV
    mode = 'w'
    if os.path.exists(output_path):
        mode = 'a' # Append if exists? For now overwrite or assume new list
        
    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(flat_results)
