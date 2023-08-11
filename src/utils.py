from typing import Any, Dict, List, Union

NestedDict = Dict[str, Union["NestedDict", int]]


def filter_nested_dict(
    input_dict: Dict[str, Any], keys_to_include: List[str]
) -> Dict[str, Any]:
    filtered_dict = {}
    for key, value in input_dict.items():
        if key in keys_to_include:
            if isinstance(value, dict):
                filtered_value = filter_nested_dict(value, keys_to_include)
                if filtered_value:
                    filtered_dict[key] = filtered_value
            else:
                filtered_dict[key] = value
    return filtered_dict
