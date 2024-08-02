# om3-scripts

A place for scripts related to ACCESS-OM3.

For now, this serves as a location for storing scripts that are useful for the creation/manipulation of ACCESS-OM3 configuration files. This is to prevent having multiple copies of the same script across configuration repos. In the future, these scripts may be packaged together for convenience. 

# Guidelines

When contributing scripts to this repo, please follow these guidelines where it makes sense to do so:

- [x] Add your script via a pull request so that it can be reviewed by someone else.
- [x] Don't just dump your script to the base directory. Instead, create or use a subdirectory with a name that describes what your script is for or related to. Try to also name your script in a way that makes it clear what it does.
- [x] Include documentation with your script. For example, a README explaining what the script is for, how to use it, what it can/can't do etc.
- [x] Any outputs from your script should include metadata that allows someone in the future to track down the exact version of the script used to create that output. Any easy way to do this is to include as metadata the url and commit hash of the script on GitHub. See existing scripts for examples of how to do this.
- [x] Consider including information about the dependencies or environment required to run your script, e.g. a conda-lock file describing your conda environment.

Python scripts are formatted using the [black formatter](https://github.com/psf/black). This is enforced using a github action running on pull requests. You will need to have _pre-commit_ and _black_ installed in your python environment. It is included in the _conda/analysis_ enviornments in _hh5_, otherwise it can be installed through pip or conda. Then run `pre-commit install` once to ensure your commits have black run on them before committing.