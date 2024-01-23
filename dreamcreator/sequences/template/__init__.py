#from sequences.core.<choose either smu_sweep or smu_sweep import SMUSweep

# class VoltageSweep(SMUSweep):
#     def __init__(self, ps):
#         super().__init__(sweeptype='voltage', ps=ps)
#         self.variables = {
#             'start': '', 
#             'stop': '', 
#             'step': '', 
#             'center': '',
#             'span': '',
#             'range': '',
#             'spacing': '',
#             'points': '',
#             'direction': '',
#             'sweeptype': ''
#         }
#         self.resultsinfo = {
#             'num_plots': 1,
#             'x-axis': [
#                 ['voltage (V)', self.indepresults]],
#             'y-axis': [
#                 ['current (A)', self.depresults]],
#             'legend': True,
#             'csv': True,
#             'pdf': True,
#             'mat': True,
#             'pkl': True
#         }

#     def instructions(self):
#         self.execute()