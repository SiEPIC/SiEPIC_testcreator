from setuptools import find_packages, setup
from app.SiEPIC_TestCreator.config import MYAPP

with open("app/README.md", "r") as f:
    long_description = f.read()


setup(
    name = "SiEPIC_TestCreator",
    version = MYAPP.version,
    description = "A tool for creating YAML files for use in Dream Photonics and edx course",
    package_dir = {"": "app"},
    packages = find_packages(where="app"),
    entry_points={
            'console_scripts': [
                'siepic_testcreator=SiEPIC_TestCreator.__main__:main'
            ]
        },
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/SiEPIC/SiEPIC_testcreator.git",
    author = "Jonathan Barnes",
    author_email = "jonathanyorkbarnes@gmail.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[    
        'numpy>=1.26.3',
        'pandas>=2.2.0',
        'pillow>=10.2.0',
        'pkginfo==1.10.0',
        'PyQt5>=5.15.10',
        'PyQt5-Qt5>=5.15.2',
        'PyQt5-sip>=12.13.0',
        'pywin32-ctypes>=0.2.2',
        'PyYAML>=6.0.1',
        'scipy>=1.12.0',
        'twine>=5.0.0',
        'watchdog>=3.0.0',
        'matplotlib>=3.8.2'
    ],
    python_requires='>=3.10',
)