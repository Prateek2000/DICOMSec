import pydicom
from helper import anonymization_dict, generate_random
import re


def anonymise(dataset: pydicom.FileDataset):
    # Anonymization code
    # ref https://pydicom.github.io/pydicom/1.0/auto_examples/metadata_processing/plot_anonymize.html#sphx-glr-auto-examples-metadata-processing-plot-anonymize-py
    # it describes how to modify and anonymize tag values

    """
    Odd group numbers are reserved for private data elements.
    Implementations may require communication of information that cannot be contained in Standard Data Elements.
    Private Data Elements are intended to be used to contain such information
    """
    # The following function removes Private Data Elements
    def remove_private_elements(dataset):
        dataset.remove_private_tags()
        return dataset

    """
    For any implementation to claim conformance to the Basic Application 
    Level Confidentiality Profile, they must anonymise data as stated in 
    the csv file.
    (zero length value refers to "unknown" or "")
    D: replace with non zero dummy value consistent to VR
    Z: same as D but zero length value allowed
    X: remove
    U: replace with non zero length UID that is consistent with set of instances
    Z/D: if Type 1 then replace with non zero dummy, else zero length value allowed
    X/Z: if Type 2 then replace with zero length/non zero dummy, else remove
    X/D: if Type 1 then replace with non zero dummy, else delete
    X/Z/D: if T1 keep non zero dummy, T2 zero or dummy, T3 delete
    X/Z/U: remove unless replace with consistent UID if T1, else if T2 put zero
    Find which type the tags are
    """
    # callback function using dataset.walk(function_name) traverses all data elements in metadata

    def remove_patient_details_callback(dataset, data_element):
        # group_length_tag_regex = re.compile('\([0-9]*, 0000\)')
        # if not(group_length_tag_regex.match(str(data_element.tag))):
        handling_technique = anonymization_dict.get(str(data_element.tag), 0)
        if handling_technique:
            # print("Success:", str(data_element.tag), ": ", handling_technique)
            if re.compile("X").search(handling_technique):
                # print("Deleting", dataset[data_element.tag])
                del dataset[data_element.tag]
            elif re.compile("Z").search(handling_technique):
                # print("Modifying to unknown", dataset[data_element.tag])
                data_element.value = "Unknown"
            elif re.compile("D").search(handling_technique):
                data_element.value = generate_random(data_element.VR)
                # print("Successful custom replace of type ", data_element.VR)
            elif re.compile("U").search(handling_technique):
                data_element.value = generate_random("UI")
            else:
                # Dont know how to handle this handling technique
                # Stub -  add exceptions if any are found later
                print(
                    "Error: Dont know how to handle handling technique ",
                    handling_technique,
                )
        else:
            # print("Unspecified tag found:", str(data_element.tag))
            # Given tag doesn't have a specified handling technique
            pass

    anonymized_dataset = remove_private_elements(dataset)
    anonymized_dataset.walk(remove_patient_details_callback)
    return anonymized_dataset