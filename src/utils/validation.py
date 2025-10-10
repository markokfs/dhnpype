from typing import Union, Tuple, List


# Validating data type 
def validate_damage(mode: str, percent: Union[float, int, List[Union[float, int]]]) -> Tuple[Union[float, None], Union[List[float], None]]:
    """
    Validates and processes the insulation damage percentage input.

    Parameters
    ----------
    mode : str
        The mode of damage input ('average' or 'element').

    percent : float, int, or list
        The value(s) representing insulation damage percentage.

    Returns
    -------
    tuple
        (average_percent, element_percent_list)

    Raises
    ------
    TypeError, ValueError
    """
    if mode == "average":
        if not isinstance(percent, (float, int)):
            raise TypeError(f"The format of the values is {type(percent).__name__}. When damage mode is 'average', values must be float or int.")
        if not (0 <= percent <= 1):
            raise ValueError("Damage percent must be between 0 and 1.")
        return float(percent), None

    elif mode == "element":
        if not isinstance(percent, list):
            raise TypeError("When damage mode is 'per_element', values must be a list of floats or ints.")
        if not all(isinstance(x, (float, int)) for x in percent):
            raise TypeError("All elements in the damage list must be floats or ints.")
        if any(x < 0 or x > 1 for x in percent):
            raise ValueError("All values in the damage list must be between 0 and 1.")
        return None, percent
    
    else:
        raise ValueError("Invalid damage mode. Use 'average' or 'element'.")


