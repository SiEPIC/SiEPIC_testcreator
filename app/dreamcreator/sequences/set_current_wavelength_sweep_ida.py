from dreamcreator.sequences.core.laser_sweep import LaserSweep

class SetCurrentWavelengthSweepIda(LaserSweep):
    """
    Sets the current and then performs a laser sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):

        self.variables = {
            'Start': 1480,
            'Start_info': 'Please enter the start wavelength in nm',
            'Stop': 1580,
            'Stop_info': 'Please enter the stop wavelength in nm',
            'Step': 1,
            'Step_info': 'Please enter the step size in nm',
            'Power': 1,
            'Power_info': 'Please enter the power in dBm',
            'Sweep Speed': 'auto',
            'Sweep Speed_info': 'controls the speed of the sweep, if yaml fails time execution test increase this, options are 20nm, 10nm, auto',
            'Laser Output': 'High Power',
            'Laser Output_info': 'Set to High Power or Low SSE',
            'Numscans': 1,
            'Numscans_info': 'choose how many scans for each device, default 1, max 3',
            'RangeDec': 20,
            'RangeDec_info': 'default 20',
            'Initialrange': '-20',
            'Initialrange_info': 'default -20',
            'Channel A': 'True',
            'Channel A_info': 'Please enter True to use Channel A if not enter False',
            'Channel B': 'False',
            'Channel B_info': 'Please enter True to use Channel B if not enter False',
            'Currents': '0, 1, 2',
            'Currents_info': 'Please format the currents in units (A) as a list of integers separated by commas ex. 0, 1, 2'
        }
        self.resultsinfo = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Set Current Wavelength Sweep',
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

        settings = self.ps.get_settings(self.verbose)

        for current in self.currents:
            self.ps.elecprobe.smuchannels[0].set_voltage_mode()
            self.ps.elecprobe.smuchannels[0].set_current(current)
            self.ps.elecprobe.smuchannels[0].set_output(True)
        
            self.execute()

            self.ps.elecprobe.smuchannels[0].set_output(False)

        self.ps.set_settings(settings)

