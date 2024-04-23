from dreamcreator.sequences.core.smu_sweep import SmuSweep

class CurrentSweep(SmuSweep):
    """
    Current sweep sequence class.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 0, 
            'Start_info': 'Please enter the starting current value',
            'Start_bounds': [-100, 100],
            'Stop': 1,
            'Stop_info': 'Please enter the stopping current value', 
            'Stop_bounds': [-100, 100],
            'Step': 0.1, 
            'Step_info': 'Please enter the step size',
            'Step_bounds': [-100, 100],
            'Center': '',
            'Center_info': 'Please enter the center current value',
            'Center_bounds': [-100, 100],
            'Span': '',
            'Span_info': 'Please enter the span of the sweep',
            'Range': '',
            'Range_info': 'Please enter the range of the sweep',
            'Spacing': '',
            'Spacing_info': 'Please enter the spacing of the sweep',
            'Points': '',
            'Points_info': 'Please enter the number of points in the sweep',
            'Direction': 'UP',
            'Direction_info': 'Please enter the direction of the sweep',
            'Direction_options': ['UP', 'DOWN'],
            'Sweeptype': 'current',
            'Sweeptype_info': 'Please enter the sweep type should be set to current',
            'Upper_limit': 5,
            'Upper_limit_info': 'Please enter the upper limit of the sweep',
            'Upper_limit_bounds': [0, 100],
            'Trans_col': False,
            'Trans_col_info': 'Please enter True or False for the transient column',
            'Trans_col_options': [True, False]
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