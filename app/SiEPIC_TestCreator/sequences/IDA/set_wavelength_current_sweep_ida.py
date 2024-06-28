from siepic_testcreator.sequences.core.smu_sweep import SmuSweep

class SetWavelengthCurrentSweepIda(SmuSweep):
    """
    Sets the wavelength then performs a current sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):

        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter start current (mA)',
            'Start_bounds': [-1000, 1000],
            'Stop': 1, 
            'Stop_info': 'Please enter stop current (mA)',
            'Stop_bounds': [-1000, 1000],
            'Step': 0.1, 
            'Step_info': 'Please enter step current (mA)',
            'Step_bounds': [0.01, 1000],
            'IV': 'True',
            'IV_info': 'True if current vs voltage plot needed',
            'IV_options': ['True', 'False'],
            'RV': 'True',
            'RV_info': 'True if resistance vs voltage plot needed',
            'RV_options': ['True', 'False'],
            'PV': 'True',
            'PV_info': 'True if power vs voltage plot needed',
            'PV_options': ['True', 'False'],
            'Channel A': 'True',
            'Channel A_info': 'Please enter True to use Channel A if not enter False',
            'Channel A_options': ['True', 'False'],
            'Channel B': 'False',
            'Channel B_info': 'Please enter True to use Channel B if not enter False',
            'Channel B_options': ['True', 'False'],
            'Wavelengths': '1480, 1550, 1580',
            'Wavelengths_info': 'Set wavelengths in form x, x1, x2 with unit nm',
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