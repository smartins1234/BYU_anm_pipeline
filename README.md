# BYU_anm_pipeline
Pipeline Managment

## Description
This is a heavily modified version of the previous DCC pipe https://github.com/byu-animation/dccpipe.  

The BYU_anm_pipeline is designed to run on the Fedora operating system and allow for communication between several content creation softwares.  A major modification is that this pipe is built on a USD backbone https://github.com/PixarAnimationStudios/USD rather than a purely Alembic-based structure.  This referenced file system allows for adjustments to flow up and down the pipeline instead of the traditional waterfall pipelines.

## Install Instructions
### Basic install for developers
To install all development packages, execute the following in a bash terminal:
```
git clone https://github.com/jasonwadewilliams/BYU_anm_pipeline.git
cd BYU_anm_pipeline
source setup/install.sh --dev
```
To activate and test the virtual environment:
```
source launch/env.sh
python
>>import PySide2
>>import pipe.tools
```

### Release/update in production directory
```
git clone https://github.com/jasonwadewilliams/BYU_anm_pipeline.git
cd BYU_anm_pipeline
source setup/install.sh --clean
```

### Optional Arguments
#### --dev/-d
Installs all development packages
```
source config/unix/fedora/install.sh --dev
```

#### --clean/-c
Cleans the previous installation by deleting .venv folder
```
source config/unix/fedora/install.sh --clean
```

#### --installmissing/-im
Installs missing packages with pip/yum. Note: if you are missing an rpm, you must run this as root. If you are only missing pip packages, you can run this as a normal user.
```
sudo config/unix/fedora/install.sh --installmissing
```

## Create Project:
1. run project initialization script:
    python create_project.py nameOfProject nicknameOfProject
2. Check that application launching icons were created (Maya, Houdini, Substance Painter, Nuke)
3. Check that production directory was created with several subdirectories inside
4. If 2 and 3 look right, you're good to go!


## Compatibility
This project is based off of the previous BYU Animation pipeline. [DCC Pipe.](https://github.com/byu-animation/dccpipe) That, in turn, succeeeded the previous pipeline repositories [BYU Animation Tools](https://github.com/byu-animation/byu-animation-tools) and [BYU Pipeline Tools](https://github.com/byu-animation/byu-pipeline-tools). This pipeline was created with a very specific use case, and is not intended to be used outside of the BYU Center for Animation labs. However, the pipeline is designed so that other distros/operating systems can be supported in a future release, given appropriate modifications.

### System Requirements
### FIXME: update

| Requirements    | Description                                                                         |
|:----------------|:------------------------------------------------------------------------------------|
| Fedora 27/RHEL  | The current Linux distro at BYU. (RHEL distros should be supported.)                |
| Python 2.7.5    | Most DCCs depend on Python 2.7 for the time being, so by extension, so does DCCPipe |
| pip*            | Required for pipenv                                                                 |
| pipenv*         | Virtualenv manager for python dependencies                                          |                                 
| qt-qtbase-devel*| Required for PySide2                                                                |
| libxml2-devel*  | Required for PySide2                                                                |

\* Will be automatically installed using the `--installmissing/-im` flag.

### Supported DCC's
### FIXME: update

| DCC                             | Version | Module          |
|:--------------------------------|--------:|:----------------|
| Autodesk Maya                   | 2019    | pipe.tools.maya |
| SideFX Houdini                  | 18.0    | pipe.tools.hou  |
| Foundry Nuke                    | 11.3    | pipe.tools.nuke |
| Allegorithmic Substance Painter | 2018.3  | pipe.tools.sbs  |

### Packages Managed by Pipenv
### FIXME: update
Note: All packages will be installed in the project's directory in the .venv folder.

| Pipenv Package | `--dev` only |
|:---------------|:----------:|
| [pyside2](https://pypi.org/project/PySide2/)*      | no |
| [shiboken2](https://pypi.org/project/shiboken2/)*  | no |
| [qt-py](https://github.com/mottosso/Qt.py)         | no |
| [termgraph](https://github.com/mkaz/termgraph)     | yes |
| [loguru](https://github.com/Delgan/loguru)         | yes |
| [pytest](https://github.com/pytest-dev/pytest)     | yes |
| [sphinx](https://github.com/sphinx-doc/sphinx)     | yes |

\* Due to a virtualenv limitation, pyside2 and shiboken2 will be installed to user, and then copied into the project directory. The script that handles this is `config/unix/fedora/install_pyside.sh`
