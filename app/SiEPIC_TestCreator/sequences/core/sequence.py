from dreamcreator.sequences.core.results import Results

class Sequence:

    """Operations sequence abstraction class.

    Args:
        ps (Dreams Lab ProbeStation object): probe station to perform sequence.
        variables (_type_): _description_
        visual (bool, optional): display results. Defaults to False.
        verbose (bool, optional): print progress. Defaults to False.
        saveplot (bool, optional): save the plots. Defaults to False.
    """

    def __init__(
        self, ps, variables, resultsinfo, visual=False, verbose=False, saveplot=False
    ):
        self.verbose = verbose
        self.visual = visual
        self.saveplot = saveplot
        self.results = Results(variables, resultsinfo)
        self.instruments = []
        self.external_parameters = ""
        self.ps = ps
        return

    def set_results(self, variables, resultsinfo, routine):
        self.results.resultsinfo = resultsinfo
        self.results.variables = variables
        self.results.routine = routine

    def execute(self):
        """
        Executes the sequence on a set of settings obtained from a probe station.
        Although the method implementation is incomplete, the basic workflow involves fetching the
        initial settings, processing them and then resetting the settings to their initial states.
        """
        # get the initial state of the experiment

        # self.ps.reset_instruments()

        # settings = self.ps.GetSettings(self.verbose)

        # add the instrument state to the results file
        # self.results.add('instruments', [instr.identify() for instr in self.instruments])

        # for idx, state in enumerate(settings):
        #     self.results.data['state_'+self.instruments[idx].identify()
        #                       ] = str(state.GetState())

        self.process()

        # reset the experiment state to the initial state
        #self.ps.SetSettings(settings)


    def saveconfig(self, location, saveplot=True):
        """
        Placeholder method for saving the routine configuration.
        Although the method implementation is incomplete, the basic idea is to save the routine
        configuration to a YAML file at a specified location (path).

        Args:
            location (str): The path where the configuration will be saved.
            saveplot (bool, optional): State indicating whether to save the plot. Defaults to True.
        """
        pass
        # save the routine configuration to a file
        # with open(location, 'w') as f:
        #     yaml.dump(self.routine, f

    def save(self):
        """
        Placeholder method for saving the sequence data and plots.
        Although the method implementation is incomplete, the basic idea is to set up a save location,
        export raw data to a CSV file, generate plots, and then save the plots.
        """
        pass
        # setup save location
        # save raw data to csv
        # create plots
        # save plots
