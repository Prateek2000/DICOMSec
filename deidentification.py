import pydicom

def anonymise(ds: pydicom.FileDataset):
    anonymized_ds = ds
    #Anonymization code
    #ref https://pydicom.github.io/pydicom/1.0/auto_examples/metadata_processing/plot_anonymize.html#sphx-glr-auto-examples-metadata-processing-plot-anonymize-py
    #it describes how to modify and anonymize tag values

    """
    Odd group numbers are reserved for private data elements.
    Implementations may require communication of information that cannot be contained in Standard Data Elements.
    Private Data Elements are intended to be used to contain such information
    """
    
    #The following function removes Private Data Elements
    def remove_private_elements():
        ds.remove_private_tags()

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

    def remove_patient_details():
        data_elements = ['']
        



    return anonymized_ds





#>>> for x in patient_tags:                
#...     if dcm.data_element(x).tag.is_private:
#...             print(x, ' is private')
#... 

#find out which tags are tagged as private () in pydicom