
import time
import numpy as np
import SiEPIC_TestCreator.sequences.core.sequence as Sequence


class LaserSweep(Sequence.Sequence):
    """
    Wavelength spectrum sweep sequence using tunable laser source and optical power monitor.

    Test setup:
        tunable laser -SMF-> ||DUT|| -SMF-> Power Monitor(s)
    
    mode : String, Optional.
        Sets sweep to continous or stepped. Default is continuous.
    verbose : Boolean, Optional.
        Verbose messages and plots flag. Default is False.
    visual : Boolean, Optional.
        Visualization flag. Default is False.
    """

    def __init__(self, ps, variables, resultsinfo, mode='CONT'):
        super().__init__(ps, variables, resultsinfo)
        self.ps = ps
        self.mf = self.ps.mainframe
        self.tls = self.ps.optprobe.laser # laser
        self.pm = self.ps.optprobe.detector #detector
        self.instruments = self.ps.instruments
        self.file_name = ''
        self.variables = variables
        self.resultsinfo = resultsinfo
        self.external_parameters = None
        self.external_unit = None

        # if user configures only a single power monitor not then make it a list
        if type(self.pm) != list:
            self.pm = [self.pm]

        valid_modes = ['cont', 'step']
        if mode.lower() not in valid_modes:
            TypeError("ERR: Not a valid mode. Valid units are 'cont' and 'step', as str.")
            return

        # sequence default settings
        self.mode = str(mode).lower() # Stepped or Continuous Sweep
        self.wavl_start = 1280  # nm
        self.wavl_stop = 1370  # nm
        self.wavl_pts = 601  # number of points
        self.pwr = 1  # laser power, mW
        self.sweep_speed = 20  # nm/s
        self.upper_limit = 0  # maximum power expected (dbm, -100: existing setting.)

        self.mode = self.variables['mode']
        self.wavl_start = self.variables['wavl_start']
        self.wavl_stop = self.variables['wavl_stop']
        self.wavl_pts = self.variables['wavl_pts']
        self.pwr = self.variables['pwr']
        self.sweep_speed = self.variables['sweep_speed']
        self.upper_limit = self.variables['upper_limit']

    def set_variables(self):

        self.mode = self.variables['mode']
        self.wavl_start = int(self.variables['wavl_start'])
        self.wavl_stop = int(self.variables['wavl_stop'])
        self.wavl_pts = int(self.variables['wavl_pts'])
        self.pwr = int(self.variables['pwr'])
        self.sweep_speed = int(self.variables['sweep_speed'])
        self.upper_limit = int(self.variables['upper_limit'])

    def set_results(self, variables, resultsinfo, routine):
        self.results.resultsinfo = resultsinfo
        self.results.variables = variables
        self.results.routine = routine

    def setup(self):
        """Instruments setting to customizable sequence parameters."""
        # set the detector to the wavelength and units to mW

        for p in self.pm:
            p.set_wavl(self.wavl)
            p.set_pwr_unit('mW', verbose=self.verbose)

        # set the wavelength and power of the laser and turn on
        self.tls.set_wavl(self.wavl)
        self.tls.set_pwr_unit('dBm')
        self.tls.set_pwr(self.pwr)
        self.tls.set_pwr_unit('mW')
        self.tls.set_output(True)

        # set tunable laser to send output trigger
        self.tls.write('TRIG', ':OUTP STF')
        # trigger is looped into mainframe
        self.mf.addr.write('TRIG:CONF LOOP')
        # set power meters to receive trigger (also check if there are multiple pms)
        for p in self.pm:
            p.addr.write('TRIG'+str(p.chan)+':INP SME')

        # Configure tunable laser sweep settings
        # sweep mode, cycle number, start wavl, stop wavl, sweep speed, and step
        # set tunable laser mode to continuous sweep
        if self.mode.upper() == 'STEP':
            self.tls.write('SOUR', ':WAV:SWE:MODE STEP')
        else:
            self.tls.write('SOUR', ':WAV:SWE:MODE CONT')
        
        # set tunable laser sweep cycle number to 1
        self.tls.write('SOUR', ':WAV:SWE:CYCL 1')
        self.tls.set_sweep_start(self.wavl_start)
        self.tls.set_sweep_stop(self.wavl_stop)
        self.tls.set_sweep_speed(self.sweep_speed)
        self.tls.set_sweep_step(self.sweep_step)

        for idx, p in enumerate(self.pm):
            p.set_auto_ranging(0)  # disable auto ranging
            p.set_pwr_range(self.upper_limit)
            p.set_pwr_unit('dBm')
            
            p.set_pwr_logging_par(self.wavl_pts, 0.5*self.sweep_step/self.sweep_speed)

        self.tls.set_wavl_logging_status(True)


    def flatten(self, lis):
        """
        Flatten arrays.

        Args:
            lis (array): 

        Yields:
            array: a flattened array
        """
        for item in lis:
            if isinstance(item, np.ndarray) and item.ndim > 1:
                for sub_item in self.flatten(item):
                    yield sub_item
            else:
                yield item

    def config_external_parameters(self, parameter):
        """
        Set the external_parameters variable to the given parameter.

        Args:
            parameter (_type_): _description_
        """
        self.external_parameters = parameter

    def reset_instruments(self):
        """Resets all instruments.
        """
        for inst in self.instruments:
            if inst.findinst() == 'detector' or inst.findinst() == 'laser' or inst.findinst() == 'Mainframe':
                inst.reset()
            

    def process(self):
        """Instructions of the sequence."""
        if self.verbose:
            print('\nIdentifying instruments . . .')
            for instr in self.instruments:
                print(instr.identify())
            print('\nDone identifying instruments.')

        # for p in self.pm:
        #     p.reset()

        #self.reset_instruments()
        self.set_variables()

        self.wavl = int((self.wavl_stop+self.wavl_start)/2)
        self.sweep_step = (self.wavl_stop-self.wavl_start)/(self.wavl_pts-1)

        self.setup()
        for p in self.pm:
            p.set_pwr_unit('mW')
        print([p.get_pwr_unit() for p in self.pm])
        time_delays = 2.5
        self.tls.set_wavl_logging_status(True)
        for p in self.pm:
            p.set_pwr_logging(True)
        time.sleep(time_delays)

        # start the wavelength sweep
        if self.verbose:
            print("***Starting Wavelength Sweep.***")
        self.tls.set_sweep_run(True)
        time.sleep(time_delays)
        

        while self.tls.get_sweep_run():
            time.sleep(time_delays)  # check every half a sec if the sweep is done
       
        if self.verbose:
            print("***Sweep Finished, fetching.***")
        # fetch the sweep data from the buffers
        if self.mode.upper() == 'STEP':
            # The 81689A cannot log the wavelength (LLOG), hence we infer from our settings.
            rslts_wavl = np.linspace(self.wavl_start, self.wavl_stop, num=self.wavl_pts)
        else:
            rslts_wavl = 1e9*self.tls.get_wavl_logging_data()  # nm

        rslts_pwr = np.zeros((rslts_wavl.size, len(self.pm)))

        for n, p in enumerate(self.pm):
            rslts_pwr[:, n] = 1e3*p.get_pwr_logging_data()  # mW

        # disable power and wavelength logging for power monitor and tunable laser
        for p in self.pm:
            p.set_pwr_logging(False)
            p.set_auto_ranging(1)
            p.addr.write('TRIG'+str(p.chan)+':INP IGN')
        self.tls.set_wavl_logging_status(False)
        self.mf.addr.write('TRIG:CONF PASS')

        self.results.add('rslts_wavl' + str(self.external_parameters), rslts_wavl, self.resultsinfo['xtitle'])
        self.results.add('rslts_pwr' + str(self.external_parameters), rslts_pwr, self.resultsinfo['ytitle'])
        #self.results.create_plot(self.results.resultsdict[pwrkey], self.results.resultsdict[wavlkey])
        wavlkey = 'rslts_wavl' + str(self.external_parameters)
        pwrkey = 'rslts_pwr' + str(self.external_parameters)

        self.results.create_optical_plot(self.results.resultsdict[pwrkey], self.results.resultsdict[wavlkey], self.external_parameters, self.external_unit)

        if self.results.routine == False:
            self.results.local_save(path=self.resultsinfo['save_location'], foldername=self.resultsinfo['foldername'], ps=self.ps, sequencename=self.resultsinfo['plottitle'])


        #self.results.create_optical_plot(self.results.resultsdict[pwrkey], self.results.resultsdict[wavlkey], self.external_parameters)

        # for p in self.pm:
        #     p.reset()



        import matplotlib.pyplot as plt

        if self.visual or self.saveplot:
            # Separate the interleaved data into two datasets
            num_datasets = len(rslts_pwr[0]) 

            # Separate the data into different datasets
            datasets = [np.array([item[i] for item in rslts_pwr]) for i in range(num_datasets)]

            # Plot the data for each instrument
            for idx, pwr_data in enumerate(datasets):
                plt.figure(figsize=(11, 6))
                plt.plot(rslts_wavl, 10*np.log10(pwr_data))
                plt.xlim(min(rslts_wavl), max(rslts_wavl))
                plt.xlabel('Wavelength [nm]')
                plt.ylabel('Optical Power [dBm]')
                plt.legend([f'Detector {idx + 1}'])
                plt.title(f"Result of Wavelength Spectrum Sweep for Detector {idx + 1}.\nLaser power: {self.tls.get_pwr()} {self.tls.get_pwr_unit()}")
                plt.tight_layout()
                plt.show()

                if self.saveplot:
                    print(str(self.file_name) + f"_wavsweep_{idx + 1}.png")
                    plt.savefig(str(self.file_name) + f"_wavsweep_{idx + 1}.png")
                plt.close()

        if self.verbose:
            print("\n***Sequence executed successfully.***")