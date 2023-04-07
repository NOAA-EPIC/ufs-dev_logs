<h1 align="center">
UFS Weather Model Regression Test Log Extraction Application
</h1>

<p align="center">
    <img src="images/Wall_Times_Stacked.png" width="1200" height="450">
    <img src="images/Resident_Sizes_Stacked.png" width="1200" height="450">
    <img src="images/CommonRegTests_Wall_Times_Grouped_ZoomedOut.png" width="1200" height="450">

</p>

<h5 align="center">
    
[About](#About) • [Prerequisites](#Prerequisites) • [Quick Start](#Quick-Start) • [Environment Setup](#Environment-Setup) • [What's Included](#What's-Included) • [Status](#Status) • [Version](#Version) • [Documentation](#Documentation) 

</h5>

# About

__Introduction:__

Currently, the NOAA development teams' code managers, users & developers are analyzing the UFS-WM RT's log metrics for each regression test performed for each RDHPCS within individual text files via regularly opening these text files & reading the metrics to check if UFS-WM regression tests has passed/failed.

__Purpose:__

The purpose of this script is to parse, extract, summarize, & display the metrics presented within the UFS-WM RT logs into plot figures -- while extracting the most recent revisions of the UFS-WM RT logs made to the UFS-WM developemnt branch. As developmeny continues, the application will be integrated with Jenkins to automate the conversion of the logs into visuals.

__Capabilities:__

This script will be able to perform the following actions:
* Extract content of the most recent revisions of the UFS-WM RT logs (For development purposes, the application will extract the logs from /NOAA-EPIC
/ufs-dev_logs repo/tests at this time -- which are the log files of  the UFS-WM RT repository's develop branch /tests/logs log files.)
* Parse, summarize, & display the metrics presented within the UFS-WM RT logs into plot figures
* Generates plot figures containing the metrics within the logs

__Future Capabilities:__

Could be integrated with another script, which will provide a user-friendly dashboard. Currently, the demo provides a prototype of a dashboard that features the log metrics. Further development on the dashboard is TBD. 

# Prerequisites
* [![Version badge](https://img.shields.io/badge/Python-3.9-blue.svg)](https://shields.io/)

# Dataset
* N/A

# Quick Start
* For demonstration purposes, refer to 'UFS-WM RT Log Files DashboardV7-Bootstrap.ipynb'

# Environment Setup:

* Install miniconda on your machine. Note: Miniconda is a smaller version of Anaconda that only includes conda along with a small set of necessary and useful packages. With Miniconda, you can install only what you need, without all the extra packages that Anaconda comes packaged with:
Download latest Miniconda (e.g. 3.9 version):

    * wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.9.2-Linux-x86_64.sh

* Check integrity downloaded file with SHA-256:

    * sha256sum Miniconda3-py39_4.9.2-Linux-x86_64.sh

Reference SHA256 hash in following link: https://docs.conda.io/en/latest/miniconda.html

* Install Miniconda in Linux:

    * bash Miniconda3-py39_4.9.2-Linux-x86_64.sh

* Next, Miniconda installer will prompt where do you want to install Miniconda. Press ENTER to accept the default install location i.e. your $HOME directory. If you don't want to install in the default location, press CTRL+C to cancel the installation or mention an alternate installation directory. If you've chosen the default location, the installer will display “PREFIX=/var/home//miniconda3” and continue the installation.

* For installation to take into effect, run the following command:

source ~/.bashrc

* Next, you will see the prefix (base) in front of your terminal/shell prompt. Indicating the conda's base environment is activated.

* Once you have conda installed on your machine, perform the following to create a conda environment:

    * To create a new environment (if a YAML file is not provided)

        * conda create -n [Name of your conda environment you wish to create]

(OR)

    * To ensure you are running Python 3.9:

        * conda create -n myenv Python=3.9

(OR)

* To create a new environment from an existing YAML file (if a YAML file is provided):

    * conda env create -f environment.yml

*Note: A .yml file is a text file that contains a list of dependencies, which channels a list for installing dependencies for the given conda environment. For the code to utilize the dependencies, you will need to be in the directory where the environment.yml file lives.

### Activate the new environment via:

conda activate [Name of your conda environment you wish to activate]

* Verify that the new environment was installed correctly via:

    * conda info --env

*Note:

* From this point on, must activate conda environment prior to .py script(s) or jupyter notebooks execution using the following command: conda activate
    * To deactivate a conda environment:
        * conda deactivate

### Link Home Directory to Dataset Location on RDHPCS Platform

* Unfortunately, there is no way to navigate to the "/work/" filesystem from within the Jupyter interface when working on the remote server, Orion. The best way to workaround is to create a symbolic link in your home folder that will take you to the /work/ filesystem. Run the following command from a linux terminal on Orion to create the link:

    * ln -s /work /home/[Your user account name]/work

* Now, when you navigate to the /home/[Your user account name]/work directory in Jupyter, it will take you to the /work folder. Allowing you to obtain any data residing within the /work filesystem that you have permission to access from Jupyter. This same procedure will work for any filesystem available from the root directory.

*Note: On Orion, user must sym link from their home directory to the main directory containing the datasets of interest.

## Open & Run Application on Jupyter Notebook

* Open OnDemand has a built-in file explorer and file transfer application available directly from its dashboard via:

    * Login to https://orion-ood.hpc.msstate.edu/

* In the Open OnDemand Interface, select Interactive Apps > Jupyter Notbook

### Additonal Information

To create a .yml file, execute the following commands:

* Activate the environment to export:

    * conda activate myenv

* Export your active environment to a new file:

    * conda env export > [ENVIRONMENT FILENAME].yml

# What's Included
Within the download, you will find the following directories and files:
* Demo:
    > UFS-WM RT Log Files DashboardV7-Bootstrap.ipynb
* Scripts:
    > UFS-WM RT Log Files DashboardV7-Bootstrap.ipynb
    
    > init_setup.py
* List of Dependencies: 
    > log_tracker.yml

# Documentation
* Refer to UFS-WM RT Log Files DashboardV7-Bootstrap.ipynb

# Status
    
This repository is under development and has not yet been released to the public. Interested parties are welcome to explore the code and see what we are working on. However, user support is not available for this tool, and outside contributions to the repository are not being accepted at this time. We look forward to providing user support after a future public release (date TBD), at which point, community contributions will also be welcome. In the meantime, users may use this application at their own risk.

DISCLAIMER

The United States Department of Commerce (DOC) GitHub project code is provided on an “as is” basis and the user assumes responsibility for its use. DOC has relinquished control of the information and no longer has a responsibility to protect the integrity, confidentiality, or availability of the information. Any claims against the Department of Commerce stemming from the use of its GitHub project will be governed by all applicable Federal laws. Any reference to specific commercial products, processes, or services by service mark, trademark, manufacturer, or otherwise, does not constitute or imply their endorsement, recommendation, or favoring by the Department of Commerce. The Department of Commerce seal and logo, or the seal and logo of a DOC bureau, shall not be used in any manner to imply endorsement of any commercial product or activity by DOC or the United States Government.

[![Development badge](https://img.shields.io/badge/development-passing-green)](https://shields.io/)
[![Build badge](https://img.shields.io/badge/build-passing-blue)](https://shields.io/)

# Version:
* Draft as of 06/17/22

