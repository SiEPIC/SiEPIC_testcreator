from dreamcreator.sequences.core.smu_sweep import SmuSweep

class SetWavelengthCurrentSweep(SmuSweep):
    """
    Sets the wavelength then performs a current sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):

        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter start voltage (V)',
            'Start_bounds': [-10, 10],
            'Stop': 1, 
            'Stop_info': 'Please enter stop voltage (V)',
            'Stop_bounds': [-10, 10],
            'Step': 0.1, 
            'Step_info': 'Please enter stepsize (V)',
            'Step_bounds': [-10, 10],
            'Center': '',
            'Center_info': 'Please enter center voltage',
            'Center_bounds': [0, 100],
            'Span': '',
            'Span_info': 'Please enter span voltage',
            'Span_bounds': [0, 100],
            'Range': '',
            'Range_info': 'Please enter range voltage',
            'Range_bounds': [0, 100],
            'Spacing': '',
            'Spacing_info': 'Please enter spacing voltage',
            'Spacing_bounds': [0, 100],
            'Points': '',
            'Points_info': 'Please enter points voltage',
            'Points_bounds': [0, 1000],
            'Direction': 'UP',
            'Direction_info': 'Please enter direction voltage',
            'Direction_options': ['UP', 'DOWN'],
            'Sweeptype': 'current',
            'Sweeptype_info': 'Please enter sweep type',
            'Sweeptype_options': ['current'],
            'Wavelengths': [1480, 1500, 1580],
            'Wavelengths_info': 'Please enter wavelengths value',
            'Wavelengths_bounds': [[1270, 1480], [1350, 1580]]
        }
        self.results_info = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Set Wavelength Current Sweep',
            'save_location': '',
            'foldername': '',
            'xtitle': 'Current (A)',
            'ytitle': 'Voltage (V)',
            'xscale': 1,
            'yscale': 1,
            'legend': True,
            'csv': True,
            'pdf': True,
            'mat': True,
            'pkl': False
        }

        super().__init__(variable=self.variables, resultsinfo=self.resultsinfo, type='current', ps=ps)

    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)

        settings = self.ps.get_settings(self.verbose)

        for wav in self.wavelengths:
            self.ps.optprobe.laser.set_wavl(wav)
            self.ps.optprobe.laser.set_pwr_unit('dBm')
            self.ps.optprobe.laser.set_pwr(self.pwr)
            self.ps.optprobe.laser.set_pwr_unit('mW')
            self.ps.optprobe.laser.set_output(True)
        
            self.execute()

            self.tls.set_output(False)

        self.ps.set_settings(settings)