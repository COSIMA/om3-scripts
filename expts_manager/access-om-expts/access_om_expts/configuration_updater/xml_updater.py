"""
XML Updater for the experiment management.

This module provides utilities for updating XML configuration files. It supports:
- Modifying `<metadata>` elements.
- Updating `<stream_info>` elements with attributes.
- Recursively modifying XML files.
"""

import os
import xml.etree.ElementTree as ET
from access_om_expts.utils.util_functions import (
    get_namelist_group,
    create_nested_dict,
)


class XMLUpdater:
    """
    A utility class to update XML files based on a dictionary input.

    This class supports:
    - Updating `<metadata>` elements.
    - Modifying `<stream_info>` elements based on `name` attributes.
    - Recursively modifying XML files.

    Methods:
        - `update_xml_elements`: Updates XML elements using a dictionary mapping.
        - `_update_xml_recursive`: Recursively processes XML elements for updates.
    """

    @staticmethod
    def update_xml_elements(
        expt_path: str,
        param_dict: dict[str, any],
        filename: str,
        append_group_list: list = None,
        indx: int = None,
        output_file: str = None,
    ) -> None:
        """
        Updates XML elements based on a dictionary input and saves the changes.

        Args:
            expt_path (str): Path to the experiment directory.
            param_dict (dict): Dictionary with `{parent_name: {child_name: new_value}}`.
            filename (str): The XML file name.
            append_group_list (list, optional): List of groups for appending parameters.
            indx (int, optional): Index used for appending to the group name.
            output_file (str, optional): Path to save the modified XML file. If None,
                                         overwrites the original XML file.
        """
        xml_path = os.path.join(expt_path, filename)
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
        element: ET.Element, param_dict: dict[str, dict[str, any]]
    ) -> bool:
        """
        Recursively updates XML elements based on a dictionary input.

        Args:
            element (ET.Element): The current XML element.
            param_dict (dict): Dictionary specifying updates
                               `{parent_name: {child_name: new_value}}`.

        Returns:
            bool: True if at least one update was made, False otherwise.
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
