import SiEPIC_TestCreator

def test_create_dict_from_dir():
    import os
    foldername = 'sequences'
    yaml_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), foldername)
    dirdict = SiEPIC_TestCreator.sequencetracker.DirectoryDict(yaml_file_path)
    finaldict = dirdict.create_dict_from_dir()
    pass

if __name__ == "__main__":

    #import os
    #filename = 'EBeam_heaters_mustafah_tests.yaml'
    #yaml_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    #print('Yaml test path: %s' % yaml_file_path )
    test_create_dict_from_dir()