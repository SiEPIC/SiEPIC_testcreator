from sequences.core.smu_sweep import SmuSweep

class SetWavelengthCurrentSweep(SmuSweep):
    """
    Sets the wavelength then performs a current sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):

        self.variables = {
            'Start': 0,
            'Start_info': 'Please enter start value',
            'Stop': 1, 
            'Stop_info': 'Please enter stop value',
            'Step': 0.1, 
            'Step_info': 'Please enter step value',
            'Center': '',
            'Center_info': 'Please enter center value',
            'Span': '',
            'Span_info': 'Please enter span value',
            'Range': '',
            'Range_info': 'Please enter range value',
            'Spacing': '',
            'Spacing_info': 'Please enter spacing value',
            'Points': '',
            'Points_info': 'Please enter points value',
            'Direction': 'UP',
            'Direction_info': 'Please enter direction value',
            'Sweeptype': 'current',
            'Sweeptype_info': 'Please enter sweep type',
            'Wavelengths': [1480, 1500, 1580],
            'Wavelengths_info': 'Please enter wavelengths value'
        }
        self.resultsinfo = {
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