from dreamcreator.sequences.core.laser_sweep import LaserSweep

class SetVoltageWavelengthSweep(LaserSweep):
    """
    Sets the voltage and then performs a laser sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):

        self.variables = {
            'Start': 1280,
            'Start_info': 'unit nm',
            'Start_bounds': [1200, 1400],
            'Stop': 1370,
            'Stop_info': 'unit nm',
            'Stop_bounds': [1200, 1400],
            'Step': 1,
            'Step_info': 'unit nm, can also use wavl_pts, if both filled Step will take priority',
            'Step_bounds': [1200, 1400],
            'wavl_pts': 601,
            'wavl_pts_info': 'can also use Step, if both filled Step will take priority',
            'wavl_pts_bounds': [1200, 1400],
            'Power': 1,
            'Power_info': 'unit dBm',
            'Power_bounds': [1200, 1400],
            'Sweep Speed': 20,
            'Sweep Speed_info': 'controls the speed of the sweep, if yaml fails time execution test increase this',
            'Upper Limit': 0,
            'Upper Limit_info': 'set to 0',
            'Upper Limit_bounds': [-30, 0],
            'Mode': 'CONT',
            'Mode_info': 'choose between CONT and STEP',
            'Mode_options': ['CONT', 'STEP'],
            'Laser Output': 'High Power',
            'Laser Output_info': 'choose between High Power and Low SSE',
            'Laser_options': ['High Power', 'Low SSE'],
            'Numscans': 1,
            'Numscans_info': 'choose how many scans for each device, default 1, max 3',
            'Numscans_bounds': [1,3],
            'RangeDec': 20,
            'RangeDec_info': 'default 20',
            'RangeDec_bounds': [0, 100],
            'Voltages': '[0, 1, 2]',
            'Voltages_info': 'Please format the voltages as a list of integers separated by commas ex. [0,1,2]',
            'Voltages_bounds': [-30, 30]
        }

        self.results_info = {
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