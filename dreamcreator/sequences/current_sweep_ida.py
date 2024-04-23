from dreamcreator.sequences.core.smu_sweep import SmuSweep

class CurrentSweepIda(SmuSweep):
    """
    Current sweep sequence class.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter start current (mA)',
            'Stop': 1, 
            'Stop_info': 'Please enter stop current (mA)',
            'Step': 0.1, 
            'Step_info': 'Please enter stepsize (mA)',
            'IV': 'True',
            'IV_info': 'Please enter True if you want an IV curve if not enter False',
            'RV': 'True',
            'RV_info': 'Please enter True if you want an RV curve if not enter False',
            'PV': 'True',
            'PV_info': 'Please enter True if you want a PV curve if not enter False',
            'Channel A': 'True',
            'Channel A_info': 'Please enter True to use Channel A if not enter False',
            'Channel B': 'False',
            'Channel B_info': 'Please enter True to use Channel B if not enter False'
        }

        self.resultsinfo = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Current Sweep',
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
        
        super().__init__(variables=self.variables,sweeptype='current', resultsinfo=self.resultsinfo, ps=ps)

        
    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)
        settings = self.ps.get_settings(self.verbose)
        self.execute()
        self.ps.set_settings(settings)