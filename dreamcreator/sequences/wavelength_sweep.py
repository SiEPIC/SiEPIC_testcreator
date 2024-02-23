from sequences.core.laser_sweep import LaserSweep

class WavelengthSweep(LaserSweep):
    """
    Wavelength sweep sequence class.

    Args:
        ps (Dreams Lab probe station object): the probe station performing the sweep.
    """
    def __init__(self, ps):
        self.variables = {
            'Start': 1280,
            'Start_info': 'unit nm',
            'Stop': 1370,
            'Stop_info': 'unit nm',
            'Step': 1,
            'Step_info': 'unit nm, can also use wavl_pts, if both filled Step will take priority',
            'wavl_pts': 601,
            'wavl_pts_info': 'can also use Step, if both filled Step will take priority',
            'Power': 1,
            'Power_info': 'unit dBm',
            'Sweep Speed': 20,
            'Sweep Speed_info': 'controls the speed of the sweep, if yaml fails time execution test increase this',
            'Upper Limit': 0,
            'Upper Limit_info': 'set to 0',
            'Mode': 'CONT',
            'Mode_info': 'choose between CONT and STEP',
            'Laser Output': 'High Power',
            'Laser Output_info': 'choose between CONT and STEP',
            'Numscans': 1,
            'Numscans_info': 'choose between CONT and STEP',
            'RangeDec': '20',
            'RangeDec_info': 'choose between CONT and STEP'
        
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
            'pkl': True
        }
        super().__init__(ps, variables=self.variables, resultsinfo=self.resultsinfo, mode='CONT')
        
    def run(self, routine=False):
        self.set_results(variables=self.variables, resultsinfo = self.resultsinfo, routine=routine)
        settings = self.ps.get_settings(self.verbose)
        self.execute()

        self.ps.set_settings(settings)


    
