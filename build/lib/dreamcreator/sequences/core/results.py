from datetime import datetime
import os
import pickle
import matplotlib.pyplot as plt
import pandas as pd
from scipy.io import savemat
import numpy as np
import random
from typing import List
import csv

# WAYS TO SAVE
# PCKLE FILES
# CSV
#
import yaml
import pickle


class Results:
    """Measurement results abstraction class."""

    def __init__(self, variables, resultsinfo):
        self.resultsdict = dict()
        self.resultsinfo = resultsinfo
        self.plots = []
        self.rawdata = []
        self.device = None
        self.DeviceID = ""
        self.chipID = ""
        self.variables = variables

        self.data = dict()
        return

    def add(self, name, data, title):
        """
        Add dataset to the results.

        Example
        ----------
            voltage = [1,2,3]
            current = [1,2,3]
            results = siepiclab.measurements.results()
            results.add('voltage', voltage)
            results.add('current', current)

        Parameters
        ----------
        name : string
            Name of the data to add.
        data : Any
            Content of the data.

        Returns
        -------
        None.

        """
        try:
            test = self.resultsdict[str(name)]
            raise KeyError(
                "Key in results data dictionary already exists. \
                Use another key name to avoid inadvertently overwriting    \
                existing data of the same key name or use update() method."
            )
        except KeyError:
            self.resultsdict[str(name)] = [data, title]

    def update(self, name, data):
        """
        Update data already in results dataset.

        Example
        ----------
            voltage = [1,2,3] \n
            current = [1,2,3] \n
            results = siepiclab.measurements.results() \n
            results.add('voltage', voltage1) \n
            results.add('voltage', voltage2) \n
            >> Accidently overwrites voltage (no explicit intent). \n
            results.update('voltage', voltage2) \n
            >> Intentional overwriting of data. \n

        Parameters
        ----------
        name : string
            Name of the data to add.
        data : Any
            Content of the data.

        Returns
        -------
        None.

        """
        try:
            self.data[str(name)] = data
        except KeyError:
            raise KeyError(
                "Key does not already exist in data dictionary. \
                Use the add() method when creating new entries."
            )

    def local_save(self, path, foldername, ps, sequencename):
        # create folder in locaiton of path
        folder_path = os.path.join(path, foldername)

        if bool(self.resultsinfo["csv"]) == True:
            self.save_csv(folder_path, self.resultsdict, ps, sequencename)
        if bool(self.resultsinfo["pdf"]) == True:
            self.save_pdf(folder_path=folder_path, plots_list=self.plots, seqname=sequencename)
        if bool(self.resultsinfo["mat"]) == True:
            self.save_mat(folder_path, plots_list=self.plots, seqname=sequencename)
        if bool(self.resultsinfo["pkl"]) == True:
            self.save_pkl(folder_path)

        self.plots = []
        self.resultsdict = dict()

    def replace_negatives_with_random(self, lst, m, n):
        """
        Replace all negative numbers in the list with a random number between m and n.

        Parameters:
        lst (list): The list of numbers.
        m (int): The lower bound for the random number.
        n (int): The upper bound for the random number.

        Returns:
        list: The list with negative numbers replaced.
        """
        return [random.uniform(m, n) if x < 0 else x for x in lst]

    def make_all_positive(self, lst: List[float]) -> List[float]:
        """
        Returns a new list where all negative numbers in the input list are turned to positive.

        Parameters:
            lst (List[float]): The input list containing numerical values.

        Returns:
            List[float]: A new list with all negative numbers turned to positive.
        """
        return [abs(x) for x in lst]

    def create_optical_plot(
        self, depresults, indepresults, external_parameter, external_unit, devname=None
    ):
        # using matplotlib create a plot using depresults and indepresults
        # Create a new figure
        plt.figure(figsize=(11, 6))

        # Transpose dep_data to get individual datasets
        dep_data_transposed = list(map(list, zip(*depresults[0])))

        indepresultstemp = []
        for i, x in enumerate(indepresults[0]):
            x = float(self.resultsinfo["xscale"]) * float(x)
            indepresultstemp.append(x)

        # Plot each dependent dataset against the independent data
        for i, dep in enumerate(dep_data_transposed):
            # dep = self.replace_negatives_with_random(dep, 0.0000001, 0.000001)
            dep = self.make_all_positive(dep)
            plt.plot(
                indepresultstemp,
                float(self.resultsinfo["yscale"]) * 10 * np.log10(dep),
                label=f"Detector {i+1}",
            )

        # Add title and labels
        if external_parameter == None:
            title = str(self.resultsinfo["plottitle"])
        else:
            title = (
                str(self.resultsinfo["plottitle"])
                + " at "
                + str(external_parameter)
                + str(external_unit)
            )
        plt.title(title)
        plt.xlabel(indepresults[1])
        plt.ylabel(depresults[1])

        # Add a legend
        if bool(self.resultsinfo["legend"]):
            plt.legend()

        self.plots.append([plt.gcf(), title])

        # self.plots.append(plt.gcf())

        # if self.resultsinfo['saveplot']:
        #     if devname == None:
        #         self.local_save(path=self.resultsinfo['save_location'], foldername=self.resultsinfo['foldername'])
        #     else:
        #         self.local_save(path=self.resultsinfo['save_location'], foldername=devname)

        if bool(self.resultsinfo["visual"]):
            plt.show()

    def create_plot(
        self, depresults, indepresults, external_parameter=None, external_unit=None
    ):
        # using matplotlib create a plot using depresults and indepresults
        # Create a new figure
        plt.figure(figsize=(11, 6))

        # Transpose dep_data to get individual datasets
        # dep_data_transposed = list(map(list, zip(*depresults[0])))

        # Plot each dependent dataset against the independent data
        # for i, dep in enumerate(dep_data_transposed):
        indepresulttemp = []

        for i, x in enumerate(indepresults[0]):
            x = self.resultsinfo["xscale"] * float(x)
            indepresulttemp.append(x)

        depresulttemp = [float(x) for x in depresults[0]]

        # dep_data_transposed = list(map(list, zip(*depresulttemp)))

        # for i, dep in enumerate(dep_data_transposed):
        depresultstemp = [y * self.resultsinfo["yscale"] for y in depresulttemp]
        plt.plot(indepresulttemp, depresultstemp, label=f"Channel {1}")

        # Add title and labels
        if external_parameter != None:
            title = str(self.resultsinfo["plottitle"])
        else:
            title = (
                str(self.resultsinfo["plottitle"])
                + " at "
                + str(external_parameter)
                + str(external_unit)
            )
        plt.title(title)
        plt.xlabel(indepresults[1])
        plt.ylabel(depresults[1])

        # Add a legend
        plt.legend()

        self.plots.append([plt.gcf(), title])
        # self.plots.append(plt.gcf())

        if self.resultsinfo["visual"]:
            plt.show()

    def separate_datasets(self, data):
        """Separates the data into multiple datasets based on the inner lists."""
        # Transposing the data to separate it into individual datasets
        separated_data = list(zip(*data))
        return [list(dataset) for dataset in separated_data]

    def save_csv(self, folder_path, results, ps, seqname):
        """
        Exports a dictionary to a CSV file. Each key in the dictionary gets its own cell in the CSV,
        and the cells beneath it contain the data from the list associated with that key.

        Parameters:
        - dictionary: The dictionary to export. Each key should map to a list of values.
        - file_path: The path where the CSV file should be saved.
        """

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        file_path = folder_path = os.path.join(folder_path, seqname)
        file_path = file_path + ".csv"

        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)

            # Write the metadata
            csv_writer.writerow(["# Test:\t" + seqname])
            csv_writer.writerow(["# User:\t" + "DreamLab"])
            csv_writer.writerow(["# Settings:"])
            csv_writer.writerow(["# Laser:\t" + ps.laser.identify()])
            csv_writer.writerow(["# Detector:\t" + ps.detector[0].identify()])
            csv_writer.writerow(
                ["# Sweep Speed\t:" + str(self.variables["sweep_speed"])]
            )
            csv_writer.writerow(["# Laser Power:\t" + str(self.variables["pwr"])])
            csv_writer.writerow(
                [
                    "# Wavelength step:\t"
                    + str(
                        (int(self.variables["wavl_stop"]) - int(self.variables["wavl_start"]))
                        / (int(self.variables["wavl_pts"]) - 1)
                    )
                ]
            )
            csv_writer.writerow(
                ["# Start Wavlength\t:" + str(self.variables["wavl_start"])]
            )
            csv_writer.writerow(
                ["# Stop Wavlength\t:" + str(self.variables["wavl_stop"])]
            )
            csv_writer.writerow(
                ["# Stitch Count\t:" + str(self.variables["wavl_start"])]
            )
            csv_writer.writerow(
                ["# Init Range\t:" + str(self.variables["upper_limit"])]
            )
            csv_writer.writerow(
                [
                    "# New sweepplot behaviour replace \t:"
                    + str(self.variables["wavl_start"])
                ]
            )
            csv_writer.writerow(["# Turn off laser when done\t:" + "yes"])
            csv_writer.writerow(["# Skip sweep if finealign fails\t:" + "no"])
            csv_writer.writerow(["Metric\t:" + "value"])

            for key, (values, name) in self.resultsdict.items():
                if values is None or len(values) == 0:
                    continue

                # Check if the first item in values is itself a list (assuming all are similar)
                if isinstance(values[0], list):
                    for channel, inner_values in enumerate(zip(*values)):
                        row = [f"{name} (channel {channel})"] + [
                            str(v) for v in inner_values
                        ]
                        csv_writer.writerow(row)
                else:
                    row = [name] + [str(v) for v in values]
                    csv_writer.writerow(row)

    def save_pdf(self, folder_path, plots_list, seqname):
        """
        Save the provided list of Matplotlib plots as separate PDFs at the specified location.

        Args:
        - folder_path (str): The path to the folder where the PDFs should be saved.
        - filename_prefix (str): The desired filename prefix for the PDFs.
        - plots_list (list): List of Matplotlib plots to be saved.

        Returns:
        - full_paths (list): List of full paths to the saved PDFs.
        """
        # Ensure the directory exists

        filename = "plot"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        full_paths = []

        for i, plot in enumerate(plots_list, 1):
            # Define the full path for the PDF
            filename = str(seqname) + '_' + str(plot[1])
            full_path = os.path.join(folder_path, f"{filename}_{i}.pdf")

            # Save the plot as a PDF
            plot[0].savefig(full_path)

            # Close the plot to free up resources
            # plt.close(plot)

            full_paths.append(full_path)

        if self.resultsinfo['mat'] == False:
            self.plots = []

        return full_paths

    def save_mat(self, folder_path, plots_list, seqname):
        # save the given matplot to a mat file at the location folder_path

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


        for i, plot in enumerate(plots_list, 1):
            # Define the full path for the PDF
            filename = str(seqname) + '_' + str(plot[1])


            # Initialize a dictionary to hold data
            all_data = {}

            # Loop through all axes in the figure
            for ii, ax in enumerate(plot[0].get_axes()):
                # Loop through all line objects in the axes
                for j, line in enumerate(ax.get_lines()):
                    # Extract the x and y data from the line object
                    x_data = line.get_xdata()
                    y_data = line.get_ydata()
                    # Store the data in the dictionary
                    all_data[f'x_data_axis{ii}_line{j}'] = x_data
                    all_data[f'y_data_axis{ii}_line{j}'] = y_data

            # Save the plot data to a .mat file
            savemat(os.path.join(folder_path, f"{filename}_{i}.mat"), all_data)
        
        self.plots = []

    def save_pkl(self, folder_path, file_name=None, timestamp=False):
        """
        Export the results to a pickle file (.pkl).

        Parameters
        ----------
        file_name : string, optional
            File name and directory of the file to save. The default is None.
                Current timestamp will be used if filename is None.
        timestamp : Boolean, optional
            Flag to add a timestamp in the format of YYYYMMDDHHMMSS format.

        Returns
        -------
        None.

        """
        if timestamp or file_name is None:
            if file_name is None:
                file_name = str(datetime.now().strftime("%Y%m%d%H%M%S")) + ".yaml"
            else:
                file_name = (
                    str(datetime.now().strftime("%Y%m%d%H%M%S"))
                    + "_"
                    + file_name
                    + "yaml"
                )

        with open(str(file_name) + ".pkl", "wb") as f:
            pickle.dump(self.data, f)

    def load(self, file_name):
        """
        Import previousily exported results pickle file (.pkl).

        Parameters
        ----------
        file_name : string, optional
            File name and directory of the file to save.

        Returns
        -------
        Dictionary
            Dictionary containing the loaded data results.

        """
        with open(str(file_name) + ".pkl", "rb") as f:
            return pickle.load(f)
