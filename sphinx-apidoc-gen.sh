#!/bin/bash

# Deletes all previous *.rsta files to clean the documentation
echo Deleting all previous *.auto_rst files
rm doc/*.auto_rst

# Generates code from source files with the *.rsta file extension
sphinx-apidoc --no-toc -s auto_rst -f -o doc/ .
