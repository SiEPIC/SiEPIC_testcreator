from SiEPIC_TestCreator.sequences.core.smu_sweep import SmuSweep
import time

class SetWavelengthVoltageSweepIda(SmuSweep):
    """
    Sets the wavelength then performs a voltage sweep.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter start voltage (V)',
            'Start_bounds': [-50, 50],
            'Stop': 1, 
            'Stop_info': 'Please enter stop voltage (V)',
            'Stop_bounds': [-50, 50],
            'Step': 0.1, 
            'Step_info': 'Please enter step voltage (V)',
            'Step_bounds': [0.01, 100],
            'IV': 'True',
            'IV_info': 'True if current vs voltage plot needed',
            'IV_options': ['True', 'False'],
            'RV': 'True',
            'RV_info': 'True if ressiatnce vs voltage plot needed',
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
            'plottitle': 'Set Wavelength Voltage Sweep',
            'save_location': '',
            'foldername': '',
            'xtitle': 'Voltage (V)',
            'ytitle': 'Current (A)',
            'xscale': 1,
            'yscale': 1,
            'legend': True,
            'csv': True,
            'pdf': True,
            'mat': True,
            'pkl': False
        }

        super().__init__(variables=self.variables, resultsinfo=self.resultsinfo, sweeptype='voltage', ps=ps)

    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)

        settings = self.ps.get_settings(self.verbose)

        for wav in self.variables['wavelengths']:
            self.ps.optprobe.laser.set_wavl(wav)
            self.ps.optprobe.laser.set_pwr_unit('dBm')
            self.ps.optprobe.laser.set_pwr(self.variables['pwr'])
            self.ps.optprobe.laser.set_pwr_unit('mW')
            self.ps.optprobe.laser.set_output(True)
            time.sleep(3)
        
            self.execute()

            self.ps.optprobe.laser.set_output(False)

        
        self.ps.set_settings(settings)