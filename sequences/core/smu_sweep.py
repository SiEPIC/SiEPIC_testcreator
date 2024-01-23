
import sequences.core.sequence as Sequence
import time

class SmuSweep(Sequence.Sequence):
    def __init__(self, sweeptype, ps, variables, resultsinfo):
        super(SmuSweep, self).__init__(ps, variables, resultsinfo)
        self.variables = variables
        self.start = self.variables['start'] 
        self.stop = self.variables['stop']
        self.step = self.variables['step']
        self.center = self.variables['center']
        self.span = self.variables['span']
        self.range = self.variables['range']
        self.spacing = self.variables['spacing']
        self.points = self.variables['points']
        self.direction = self.variables['direction']
        self.upper_limit = self.variables['upper_limit']
        self.tranmission_collection = self.variables['trans_col']
        self.sweeptype = sweeptype
        self.sweep_settings = {'sweeptype': self.sweeptype, 'start': self.start, 'stop': self.stop,'step': self.step,'center': self.center,'span': self.span,'range': self.range,'spacing': self.spacing, 'points': self.points,'direction': self.direction, 'transmission_collection': self.tranmission_collection}
        self.depresults = []
        self.indepresults = []
        self.resultsinfo = resultsinfo
        self.external_parameters = ''

        self.ps = ps
        self.channels = 1
        self.PV = False
        self.RV = False
        self.IV = False
        self.state = {'sweeptype': self.sweeptype, 'output_a': [], 'volt_a': [], 'curr_a': [], 'curr_lim_a': [], 'volt_lim_a': [], 'output_b': [], 'volt_b': [], 'curr_b': [], 'curr_lim_b': [], 'volt_lim_b': []}
        self.smu = self.ps.elecprobe.smuchannels
        self.instruments = self.ps.instruments

    def set_variables(self):

        if self.variables['start'] != '':
            self.start = float(self.variables['start']) 
        else:
            self.start = self.variables['start']    
        if self.variables['stop'] != '':
            self.stop = float(self.variables['stop']) 
        else:
            self.stop = self.variables['stop']  
        if self.variables['step'] != '':
            self.step = float(self.variables['step']) 
        else:
            self.step = self.variables['step']  
        if self.variables['center'] != '':
            self.center = float(self.variables['center'])
        else:
            self.center = self.variables['center']
        if self.variables['span'] != '':    
            self.span = float(self.variables['span'])
        else:
            self.span = self.variables['span']
        
        self.range = self.variables['range']
        self.spacing = self.variables['spacing']

        if self.variables['points'] != '':  
            self.points = float(self.variables['points'])
        else:
            self.points = self.variables['points']
        self.direction = self.variables['direction']
        self.upper_limit = float(self.variables['upper_limit'])
        self.tranmission_collection = float(self.variables['trans_col'])


    def setup(self):
        "setup SMU for sweep"
        for chan in self.smu:
            #chan.SetState(self.state)
            chan.set_sweep_settings(self.sweep_settings)

    def process(self):
        self.results.resultsinfo = self.resultsinfo
        self.set_variables()
        self.sweep_settings = {'sweeptype': self.sweeptype, 'start': self.start, 'stop': self.stop,'step': self.step,'center': self.center,'span': self.span,'range': self.range,'spacing': self.spacing, 'points': self.points,'direction': self.direction, 'limit': self.upper_limit, 'tranmission_collection': self.tranmission_collection}
        
        self.state = {'type': self.sweeptype, 'output_a': [], 'volt_a': [], 'curr_a': [], 'curr_lim_a': [], 'volt_lim_a': [], 'output_b': [], 'volt_b': [], 'curr_b': [], 'curr_lim_b': [], 'volt_lim_b': []}
        self.setup()

        self.indepresults = []
        self.depresults = []
        

        if not self.sweep_settings['tranmission_collection']:
            for chan in self.smu:
                indepresults, depresults = chan.set_sweep_run()
                self.indepresults.extend(indepresults)
                self.depresults.extend(depresults)

            # Transpose the results using zip and convert back to lists
            if len(self.smu) > 1:
                self.indepresults = [list(x) for x in zip(*self.indepresults)]
                self.depresults = [list(x) for x in zip(*self.depresults)]

            if self.sweeptype == 'voltage':
                self.dep_title = 'current'
            elif self.sweeptype == 'current':
                self.dep_title = 'voltage'

            depkey = str(self.dep_title) + str(self.external_parameters)
            indepkey = str(self.sweeptype) + str(self.external_parameters)

            self.results.resultsdict[depkey]  = []
            self.results.resultsdict[indepkey] = []

            self.results.add(depkey, self.depresults, self.resultsinfo['ytitle'])
            self.results.add(indepkey, self.indepresults, self.resultsinfo['xtitle'])
           
           
            self.results.create_plot(self.results.resultsdict[depkey], self.results.resultsdict[indepkey], self.external_parameters)
            
            if self.results.routine == False:
                self.results.local_save(path=self.resultsinfo['save_location'], foldername=self.resultsinfo['foldername'], ps=self.ps, sequencename=self.resultsinfo['plottitle'])



        else:

            sweeplist = list(range(self.sweep_settings['start'], self.sweep_settings['stop'], self.sweep_settings['step']))
            all_dep_results = [] 
            
            for chan in self.smu:
                for n in sweeplist:
                    self.indepresults.append(n)
                    chan.set_voltage(n)
                    time.sleep(0.1)
                    #add code to get all detector readings
                    chan_dep_results = []
                    for det in self.ps.detector:
                        chan_dep_results.append(det.get_pwr())
                    all_dep_results.append(chan_dep_results)

            self.depresults = [list(x) for x in zip(*all_dep_results)]

            self.results.add('depresults', self.depresults)
            self.results.add('indepresults', self.indepresults) 

            self.results.add(str(self.dep_title) + str(self.external_parameters), self.depresults, self.resultsinfo['xtitle'])
            self.results.add(str(self.sweeptype) + str(self.external_parameters), self.indepresults, self.resultsinfo['ytitle'])
           
           
            depkey = str(self.dep_title) + str(self.external_parameters)
            indepkey = str(self.sweeptype) + str(self.external_parameters)
           
           
            self.results.create_plot(self.results.resultsdict[depkey], self.results.resultsdict[indepkey])

            if self.results.routine == False:
                self.results.local_save(path=self.resultsinfo['save_location'], foldername=self.resultsinfo['foldername'], ps=self.ps, sequencename=self.resultsinfo['plottitle'])

            
    
            


        #self.smu.setSweepRun(type=self.type, minVar=self.Min, maxVar=self.Max, res=self.Res)

        #self.smu.setSweepRun(type=self.type, minVar=self.Min, maxVar=self.Max, res=self.Res)