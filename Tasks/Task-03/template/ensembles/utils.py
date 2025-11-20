from typing import TypedDict

import numpy as np
import numpy.typing as npt


class ConvergenceHistory(TypedDict):
    """
    TypedDict to store the convergence history of training and validation losses.

    Attributes
    ----------
    train : list[float]
        A list of training losses over epochs.
    val : list[float] | None, optional
        A list of validation losses over epochs. Defaults to None.
    """

    train: list[float]
    val: list[float] | None = None


def rmsle(y: npt.NDArray[np.float64], z: npt.NDArray[np.float64]) -> np.float64:
    """
    Calculate the Root Mean Squared Logarithmic Error (RMSLE) between two arrays.

    RMSLE is a metric that is often used in regression problems where the target variable
    is continuous and non-negative. It is particularly useful when the target variable
    spans several orders of magnitude.

    Args
    ----
    y : npt.NDArray[np.float64]
        The true values.
    z : npt.NDArray[np.float64]
        The predicted values.

    Returns
    -------
    float
        The RMSLE value.
    """
    res = np.sqrt(np.mean((np.log1p(y) - np.log1p(z)) ** 2))
    return float(res)


def whether_to_stop(convergence_history: ConvergenceHistory, patience: int) -> bool:
    """
    Determine whether to stop training based on the convergence history.

    This function checks if the training or validation loss has not improved for a
    specified number of epochs (patience). If the validation loss history is provided,
    it is used for the decision; otherwise, the training loss history is used.

    Args
    ----
    convergence_history : ConvergenceHistory
        A dictionary containing the training loss history and optionally the validation
        loss history.
    patience : int
        The number of epochs to wait after the last time the loss improved before
        stopping the training.

    Returns
    -------
    bool
        True if training should be stopped, False otherwise.

    Raises
    ------
    KeyError
        If neither 'train' nor 'val' key is present in the convergence_history.
    """
    
    ...