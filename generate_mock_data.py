import pandas as pd
import numpy as np
import os

def generate_mock_data():
    # Mock Block Model
    n_blocks = 1000
    block_data = {
        'LITOLOGIA': np.random.choice(['MINERAL', 'ESTÉRIL', 'ALTO_TEOR'], n_blocks),
        'RECURSO': np.random.choice(['MEDIDO', 'INDICADO', 'INFERIDO'], n_blocks),
        'TONELAGEM': np.random.uniform(100, 500, n_blocks),
        'VOLUME': np.random.uniform(50, 200, n_blocks),
        'Fe_pct': np.random.uniform(30, 70, n_blocks),
        'SiO2_pct': np.random.uniform(1, 10, n_blocks),
        'g1': np.random.choice([0, 10, 20], n_blocks),
        'g2': np.random.choice([0, 5, 15], n_blocks),
    }
    # Add some nulls and zeros
    df_blocks = pd.DataFrame(block_data)
    df_blocks.loc[np.random.choice(n_blocks, 50), 'Fe_pct'] = np.nan
    df_blocks.loc[np.random.choice(n_blocks, 30), 'g1'] = 0
    
    df_blocks.to_csv('mock_block_model.csv', index=False)
    print("Generated mock_block_model.csv")

    # Mock Database
    n_samples = 200
    db_data = {
        'LITO': np.random.choice(['MINERAL', 'ESTÉRIL', 'ALTO_TEOR'], n_samples),
        'FE': np.random.uniform(25, 75, n_samples),
        'SIO2': np.random.uniform(0.5, 12, n_samples),
    }
    df_db = pd.DataFrame(db_data)
    df_db.to_csv('mock_database.csv', index=False)
    print("Generated mock_database.csv")

if __name__ == "__main__":
    generate_mock_data()
