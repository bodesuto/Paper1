from datasets import load_dataset
import pandas as pd
import os
from typing import Optional


def load_hotpot_dataset(
    split: str = "train",
    question_type: Optional[str] = None,
    level: Optional[str] = None,
    size: Optional[int] = None,
    output_path: Optional[str] = None,
) -> pd.DataFrame:
    """
    Load and filter HotPotQA dataset.

    Args:
        split: Dataset split ('train' or 'validation')
        question_type: Filter by type ('bridge', 'comparison', or None for all)
        level: Filter by level ('hard', 'medium', or None for all)
        size: Maximum number of samples to return (None for all)
        output_path: Path to save CSV file (None to skip saving)

    Returns:
        pd.DataFrame: Filtered dataset as pandas DataFrame
    """
    # Load the HotPotQA dataset with fullwiki context
    dataset = load_dataset("hotpot_qa", "fullwiki")
    data = dataset[split]

    # Apply filters
    if question_type:
        data = data.filter(lambda x: x["type"] == question_type)
    if level:
        data = data.filter(lambda x: x["level"] == level)

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Limit size if specified
    if size:
        df = df.head(size)

    # Save if output path is provided
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")

    return df

