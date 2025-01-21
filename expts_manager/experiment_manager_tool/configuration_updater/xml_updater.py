import os
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from experiment_manager_tool.utils.util_functions import (
    get_namelist_group,
    create_nested_dict,
)


class XMLUpdater:
    """
    A class to update XML files based on a dictionary input.
    Supports updating metadata elements and stream_info elements with name attributes.
    """

    @staticmethod
    def update_xml_elements(
        expt_path: str,
        param_dict: Dict[str, Any],
        parameter_block: str,
        append_group_list: list = None,
        indx: int = None,
        output_file: Optional[str] = None,
    ) -> None:
        """
        Recursive updates to XML elements based on a dictionary input and saves the changes.

        Args:
        - xml_path (str): Path to the XML file.
        - param_dict (dict): Dictionary with {parent_name: {child_name: new_value}}.
        - output_file (str, optional): Path to save the modified XML file. If None, overwrites the original xml.
        """

        xml_path = os.path.join(expt_path, parameter_block)
        tree = ET.parse(xml_path)
        root = tree.getroot()

        if indx is not None:
            nml_group = get_namelist_group(append_group_list, indx)
            param_dict = create_nested_dict(nml_group, param_dict)

        updated = XMLUpdater._update_xml_recursive(root, param_dict)

        if updated:
            output_path = output_file if output_file else xml_path
            tree.write(output_path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _update_xml_recursive(
        element: ET.Element, param_dict: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Recursively updates XML elements based on a dictionary input.

        Parameters:
        - element (ET.Element): The current XML element
        - param_dict (dict): The dictionary specifying updates {parent_name: {child_name: new_value}}.

        Returns:
        - bool: True if at least one update was made, False otherwise.
        """
        updated = False

        # Get the tag name without namespace, e.g., "{sss}metadata"
        e_tag = element.tag.split("}")[-1]

        # <metadata> (no attributes)
        if e_tag == "metadata" and "metadata" in param_dict:
            for child_name, new_value in param_dict["metadata"].items():
                child = element.find(child_name)
                if child is not None:
                    child.text = new_value
                    updated = True

        # <stream_info> (with attributes)
        elif e_tag == "stream_info":
            stream_name = element.get("name")
            if stream_name in param_dict:
                for child_name, new_value in param_dict[stream_name].items():
                    child = element.find(child_name)
                    if child is not None:
                        child.text = new_value
                        updated = True

        # Recursively process child elements
        for child in element:
            if XMLUpdater._update_xml_recursive(child, param_dict):
                updated = True

        return updated
