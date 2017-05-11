# Install

## Requirements:

### Software

1. Python
1. OpenCV with Python2 binding
1. Qt5 python binding
4. Gradle



- Tips:
1. use ```homebrew``` to install them.
2. use ```virtualenv``` if necessary

### Python Packages

All Required packages are listed in "requirements.txt".

```pip install -r requirements.txt```


## Build

under project root:

1. ```gradle gen```
2. under src, run ```./genui.sh``` to generate .py from .ui (Qt Gui file)

# IO

see ```doc/lpicker.md```

# TODO
1. use docker to automate dev. setting up and deployment