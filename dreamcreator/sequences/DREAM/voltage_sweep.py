from dreamcreator.sequences.core.smu_sweep import SmuSweep

class VoltageSweep(SmuSweep):
    """
    Voltage sweep sequence class.

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
            'Sweeptype': 'voltage',
            'Sweeptype_info': 'Please enter sweep type',
            'Sweeptype_options': ['voltage'],
            'Upper Limit': 5,
            'Upper Limit_info': 'Please enter upper limit voltage',
            'Upper Limit_bounds': [0, 100],
            'Trans_col': 'False',
            'Trans_col_info': 'Please enter transition eitehr True or False',
            'Trans_col_options': ['True', 'False']
        }

        self.results_info = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'Voltage Sweep',
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
            'pkl': True
        }
        
        super().__init__(variables=self.variables,sweeptype='voltage', resultsinfo=self.resultsinfo, ps=ps)

        

    def run(self,routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)
        settings = self.ps.get_settings(self.verbose)
        self.execute()
        self.ps.set_settings(settings)
