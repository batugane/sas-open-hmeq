"""
Score CSV data using a MAS-deployed model via sasctl's microanalytic_score service.
"""

import argparse
import logging

import pandas as pd
from sasctl import Session
from sasctl.services import microanalytic_score

from src.utils.auth_utils import get_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_modules():
    """List all available MAS modules"""
    modules = microanalytic_score.list_modules()
    if modules is None:
        raise ValueError("No modules found")
    return [module['name'] for module in modules]


def get_module_info(module_name):
    """Get detailed information about a module including its steps and inputs"""
    try:
        module = microanalytic_score.get_module(module_name)
        logger.info(f"=== Module '{module_name}' Details ===")
        
        # Get steps for this module
        steps = microanalytic_score.list_module_steps(module_name)
        if steps is None:
            raise ValueError("No steps found")
        for step in steps:
            step_id = getattr(step, 'id', 'N/A') if hasattr(step, 'id') else 'N/A'
            logger.info(f"Step ID: {step_id}")
            inputs = getattr(step, 'inputs', []) if hasattr(step, 'inputs') else []
            if inputs:
                logger.info("Inputs:")
                for inp in inputs:
                    inp_name = inp.get('name', 'N/A')
                    inp_type = inp.get('type', 'N/A')
                    logger.info(f"  - {inp_name}: {inp_type}")
        logger.info("=" * 40)
        
        return module, steps
    except Exception as e:
        logger.error(f"Failed to get module info: {e}")
        raise


def score_records(module_name, records):
    """Score records using sasctl's microanalytic_score service"""
    try:
        module, steps = get_module_info(module_name)
        
        # Find the score step (or use the first step if no 'score' step exists)
        score_step = None
        for step in steps:
            step_id = getattr(step, 'id', None)
            if step_id and step_id.lower() == 'score':
                score_step = step_id
                break
        
        if not score_step and steps:
            score_step = getattr(steps[0], 'id', None)
            logger.info(f"No 'score' step found, using '{score_step}' instead")
        
        if not score_step:
            raise RuntimeError(f"No steps found for module '{module_name}'")
        
        # Score each record
        all_results = []
        for i, record in enumerate(records):
            logger.info(f"Scoring record {i+1}/{len(records)}")
            
            # Convert record keys to lowercase to match module expectations
            record_lower = {k.lower(): v for k, v in record.items()}
            
            # Execute the module step
            result = microanalytic_score.execute_module_step(
                module_name, 
                score_step, 
                return_dict=True,
                **record_lower
            )
            
            # Combine inputs and outputs
            result_row = {}
            # Add outputs
            if isinstance(result, dict):
                result_row.update(result)
            # Add original inputs
            result_row.update(record_lower)
            
            all_results.append(result_row)
        
        return all_results
        
    except Exception as e:
        logger.error(f"Failed to score records: {e}")
        raise


def main():
    p = argparse.ArgumentParser("Score CSV via sasctl microanalytic_score service")
    p.add_argument('-H', '--host',       required=True, help='Viya host, e.g. https://create.demo.sas.com')
    p.add_argument('-m', '--module',     required=True, help='MAS module name')
    p.add_argument('-i', '--input-csv',  required=True, help='Path to input CSV file')
    p.add_argument('-o', '--output-csv', required=True, help='Path to output CSV file')
    args = p.parse_args()

    # Get authentication token
    token = get_token()
    
    # Create sasctl session
    try:
        with Session(args.host, token=token, protocol='https') as session:
            # List available modules
            modules = list_modules()
            logger.info(f"Available modules: {modules}")
            
            # Verify the requested module exists
            if args.module not in modules:
                logger.error(f"Module '{args.module}' not found. Available modules: {modules}")
                return
            
            # Read CSV data
            df = pd.read_csv(args.input_csv)
            records = df.to_dict(orient='records')
            logger.info(f"Read {len(records)} records from {args.input_csv}")
            
            # Score the records
            scored = score_records(args.module, records)
            
            # Save results
            result_df = pd.DataFrame(scored)
            result_df.to_csv(args.output_csv, index=False)
            logger.info(f"Scored data written to {args.output_csv}")
            
    except Exception as e:
        logger.error(f"Session error: {e}")
        raise


if __name__ == '__main__':
    main() 