# Project Title

This package is for use in the UBC Photonics courses, and contains utilities for creating
yaml files which act as guides for tests on the probe stations throughout UBC.

## Description

This software contains a User Interface that easily allows users to create custom YAML files to guide tests on probe stations throughout UBC. It is built using PyQt and leverages the dreamcreator and sequencecreator modules for functionality. To add a new stage setup simply add an additional folder in the sequences directory and populate with formatted sequence files, then reload the UI.

## Getting Started

### Dependencies

* Describe any prerequisites, libraries, OS version, etc., needed before installing program.
* ex. Windows 10
python: 3.10 +
Windows 10 or greater, Linux, or Mac OSX


### Installing

```
pip install SiEPIC_TestCreator
```

### Executing program

* How to run the program, note imports are case sensitive
```
from SiEPIC_TestCreator import sequencecreator as sc
sc.launch()
```

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

Jon Barnes [@JonBarnes](https://twitter.com/JonBarnes)

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

## Acknowledgments

Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46)

## Developers

* Contributions are welcome, via Pull Requests
* Create a fork, and download it using GitHub Desktop to work on your local copy
* Install the package as a symbolic link 
    ```
    pip install -e $HOME/Documents/GitHub/SiEPIC_testcreator
    ```
* Keep your fork and local copy up to date
