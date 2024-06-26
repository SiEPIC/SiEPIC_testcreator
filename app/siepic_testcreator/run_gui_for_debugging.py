#%%

import sys
import os
#print(sys.path)

current_dir = os.path.dirname(os.path.abspath(__file__))

print(current_dir)
#module_dir = os.path.join(current_dir, 'sequencecreator')
module_dir = r'C:\Users\Smitt\Documents\GitHub\SiEPIC_testcreator\app\siepic_testcreator'

sys.path.append(module_dir)

from sequencecreator import launch

if __name__ == "__main__":
    launch()


# %%