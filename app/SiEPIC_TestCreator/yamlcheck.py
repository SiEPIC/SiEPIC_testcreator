import yaml


def get_key_at_position(some_dict, position=1):
    """
    Retrieves the key at a specified position from a dictionary.

    Args:
    some_dict (dict): The dictionary from which to retrieve the key.
    position (int): Position of the key to retrieve, 1-based indexing. Default is 1.

    Returns:
    The key at the specified position, or None if the position is out of range.
    """
    if 1 <= position <= len(some_dict):
        return list(some_dict)[position - 1]
    return None


def yaml_check(yaml_file_path):
    """
    Reads a YAML file and converts it to a dictionary.

    Args:
    yaml_file_path (str): Path to the YAML file.

    Returns:
    dict: Dictionary representation of the YAML file.
    """
    errorflag = False
    with open(yaml_file_path, "r") as file:
        try:
            yaml_dict = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
            errorflag = True
            print("Error in YAML file. Please check the file and try again.")
            return None

    try:
        deviceflag = get_key_at_position(yaml_dict, 1)
        sequenceflag = get_key_at_position(yaml_dict, 2)
    except:
        errorflag = True
        print("Error in YAML file. Please check the file and try again.")
        return None

    if deviceflag != "Devices":
        errorflag = True
        print("Error in YAML file. Please check the file and try again.")
        return None

    if sequenceflag != "Sequences":
        errorflag = True
        print("Error in YAML file. Please check the file and try again.")
        return None

    #

    # check for sequence runtime errors
    runtime = sequence_runtime_check(yaml_dict, True)
    print("Sequence runtime: ", runtime)
    return runtime

def sequence_runtime_check(yaml_file_path, dict=None, debug=False):
    """
    Checks the runtime of a sequence.
    """
    if dict == None:
        with open(yaml_file_path, "r") as file:
            try:
                yaml_dict = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                print(exc)
                errorflag = True
                print("Error in YAML file. Please check the file and try again.")
                return None
    else:
        yaml_dict = yaml_file_path

    sequences = yaml_dict["Sequences"]
    # calculate wavlength sweep runtime

    wavelength_constant = 0.25
    smu_constant = 0.5

    sequencetypes = [
        "wavelength_sweep",
        "current_sweep",
        "voltage_sweep",
        "set_current_wavelength_sweep",
        "set_voltage_wavelength_sweep",
        "set_wavelength_current_sweep",
        "set_wavelength_voltage_sweep",
        "wavelength_sweep_ida",
        "current_sweep_ida",
        "voltage_sweep_ida",
        "set_current_wavelength_sweep_ida",
        "set_voltage_wavelength_sweep_ida",
        "set_wavelength_current_sweep_ida",
        "set_wavelength_voltage_sweep_ida",
    ]

    runtime = 0
    
    if debug:
        print("Sequences: %s" %sequences)
    
    for sequence in sequences:
        if debug:
            print("Sequence: %s" %sequence)
            print("  details: %s" % sequences[sequence])
        variables = sequences[sequence]["variables"]
        if sequencetypes[6] in sequence or sequencetypes[13] in sequence:

            runtime += (
                (
                    (float(variables["Stop"]) - float(variables["Start"]))
                )
                * smu_constant
                * (variables["Wavelengths"].count(",") + 1)
            )
        elif sequencetypes[5] in sequence or sequencetypes[12] in sequence:
            runtime += (
                (
                    (float(variables["Stop"]) - float(variables["Start"]))
                    / float(variables["Step"])
                )
                * smu_constant
                * (variables["Wavelengths"].count(",") + 1)
            )
        elif sequencetypes[4] in sequence or sequencetypes[11] in sequence:
            runtime += (
                (float(variables["Stop"]) - float(variables["Start"]))
                * wavelength_constant
                * (variables["Voltages"].count(",") + 1)
            )
        elif sequencetypes[3] in sequence or sequencetypes[10] in sequence:
            runtime += (
                (float(variables["Stop"]) - float(variables["Start"]))
                * wavelength_constant
                * (variables["Currents"].count(",") + 1)
            )
        elif sequencetypes[2] in sequence or sequencetypes[9] in sequence:
            runtime += (
                (float(variables["Stop"]) - float(variables["Start"]))
                / float(variables["Step"])
            ) * smu_constant
        elif sequencetypes[1] in sequence or sequencetypes[8] in sequence:
            runtime += (
                (float(variables["Stop"]) - float(variables["Start"]))
                / float(variables["Step"])
            ) * smu_constant
        elif sequencetypes[0] in sequence or sequencetypes[7] in sequence:
            runtime += (
                (float(variables["Stop"]) - float(variables["Start"]))
                * wavelength_constant
            )
        else:
            print("Error in predicting runtime. Please check sequence type and parameters.")
            return None

    return runtime


# Example usage
# yaml_dict = yaml_check(r'D:\Work\Github_repo\DreamLab\Examples\test.yaml')
