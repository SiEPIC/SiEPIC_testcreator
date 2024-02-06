from sequences.core.laser_sweep import LaserSweep

class SetVoltageWavelengthSweep(LaserSweep):
    """
    Sets the voltage and then performs a laser sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):

        self.variables = {
            'Start': 1480,
            'Start_info': 'Please enter a value for the start wavelength in nm',
            'Stop': 1580,
            'Stop_info': 'Please enter a value for the stop wavelength in nm',
            'Step': 1,
            'Step_info': 'Please enter a value for the step size in nm',
            'wavl_pts': 101,
            'wavl_pts_info': 'Please enter a value for the number of points in the wavelength sweep',
            'Power': 1,
            'Power_info': 'Please enter a value for the power in dBm',
            'Sweep Speed': 20,
            'Sweep Speed_info': 'Please enter a value for the sweep speed in nm/s',
            'Upper Limit': 0,
            'Upper Limit_info': 'Please enter a value for the upper limit of the sweep in dBm',
            'Mode': 'CONT',
            'Mode_info': 'Please select a mode from the following options: CONT, STEP, RAMP, SINE, SQUARE, TRIANGLE',
            'Voltages': '[0, 1, 2]',
            'Voltages_info': 'Please format the voltages as a list of integers separated by commas ex. [0,1,2]'
        }

        self.resultsinfo = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Set Voltage Wavelength Sweep',
            'save_location': '',
            'foldername': '',
            'xtitle': 'Wavelength (nm)',
            'ytitle': 'Power (dBm)',
            'xscale': 1,
            'yscale': 1,
            'legend': True,
            'csv': True,
            'pdf': True,
            'mat': True,
            'pkl': False
        }
        super().__init__(variables=self.variables, resultsinfo=self.resultsinfo, ps=ps)

    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)
        """Executes a wavelength sweep for each given voltage."""

        settings = self.ps.get_settings(self.verbose)
        
        for volt in self.variables['voltages']:
            self.ps.elecprobe.smuchannels[0].set_current_mode()
            self.ps.elecprobe.smuchannels[0].set_voltage(volt)
            self.ps.elecprobe.smuchannels[0].set_output(True)
        
            self.external_parameters = volt
            self.external_unit = 'V'
            self.execute()

            self.ps.elecprobe.smuchannels[0].set_output(False)

        self.ps.set_settings(settings)