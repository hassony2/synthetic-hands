
# How to use

First, generate your config file

`python3 settings.py`

This will create a config.ini file at the root of the folder where the folder structure is stored
(each folder has it's absolute path as value in the folders section of the config)

Mainly, this allows the dataset generation scripts and the training scripts to share the data folder structure.

Change the absolute_root in the blender-scripts files to your path to the project.
 
## Requirements

### [Blender](https://www.blender.org/)

Version : 2.78c

## Python

Version : 3.5

### Packages

- matplotlib
- numpy
- opencv-python (to read .exr files)

