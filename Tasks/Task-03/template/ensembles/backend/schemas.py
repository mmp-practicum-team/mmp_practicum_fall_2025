from pathlib import Path

from pydantic import BaseModel


class ExistingExperimentsResponse(BaseModel):
    """
    Response model for existing experiments.

    Attributes:
        location (Path): The directory path where the experiments are stored.
        experiment_names (list[str]): A list of names of the existing experiments. Defaults to an empty list.
        abs_paths (list[Path]): A list of absolute paths to the experiment directories. Defaults to an empty list.
    """

    location: Path
    experiment_names: list[str] = []
    abs_paths: list[Path] = []
