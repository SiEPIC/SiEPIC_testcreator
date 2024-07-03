"""
unit tests for the package.
needs better testing to test each module, method, and class.
"""

import SiEPIC_TestCreator

'''
def test_gui():
    # run the GUI, and close it.
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    ex = siepic_testcreator.sequencecreator.GUI()
    ex.show()
    ex.close()
    return ex
'''

def test_yaml_check():
    import os
    filename = 'EBeam_heaters_mustafah_tests.yaml'
    yaml_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    SiEPIC_TestCreator.yamlcheck.yaml_check(yaml_file_path)

def test_sequence_runtime_check():
    import os
    filename = 'EBeam_heaters_mustafah_tests.yaml'
    yaml_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    t = SiEPIC_TestCreator.yamlcheck.sequence_runtime_check(yaml_file_path)
    assert t == 25

if __name__ == "__main__":

    #import os
    #filename = 'EBeam_heaters_mustafah_tests.yaml'
    #yaml_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    #print('Yaml test path: %s' % yaml_file_path )
    test_yaml_check()
    test_sequence_runtime_check()

    # test_gui()
