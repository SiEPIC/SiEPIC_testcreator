from sequences.core.laser_sweep import LaserSweep

class WavelengthSweepIda(LaserSweep):
    """
    Wavelength sweep sequence class.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 1480,
            'Start_info': 'unit nm',
            'Stop': 1580,
            'Stop_info': 'unit nm',
            'Step': 1,
            'Step_info': 'unit nm, can also use wavl_pts, if both filled Step will take priority',
            'Power': 1,
            'Power_info': 'unit dBm',
            'Sweep Speed': 'auto',
            'Sweep Speed_info': 'controls the speed of the sweep, if yaml fails time execution test increase this, options are 20nm, 10nm, auto',
            'Laser Output': 'High Power',
            'Laser Output_info': 'Set to High Power or Low SSE',
            'Numscans': 1,
            'Numscans_info': 'choose how many scans for each device, default 1, max 3',
            'RangeDec': 20,
            'RangeDec_info': 'default 20',
            'Initialrange': '-20',
            'Initialrange_info': 'default -20'
        }

        self.resultsinfo = {
            'num_plots': 1,
            'visual': True,
            'saveplot': True,
            'plottitle': 'WavelengthSweep',
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
        super().__init__(ps, variables=self.variables, resultsinfo=self.resultsinfo, mode='CONT')
        
    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)
        settings = self.ps.get_settings(self.verbose)
        self.execute()

        self.ps.set_settings(settings)


    
