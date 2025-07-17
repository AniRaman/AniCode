#!/usr/bin/bash
NOT_INSTALLED="$(which python 2>&1 | grep 'no python in')"
if [ -z "$NOT_INSTALLED" ]; then
    VERSION="$(py --list | grep '3\.12')"
    if [ -n "$VERSION" ]; then
        python -m venv venv
        if [ "$OSTYPE" = "msys" ]; then
            . venv/Scripts/activate
        fi

        if [[ $OSTYPE == 'darwin'* ]]; then
            source venv/bin/activate
        fi
        pip install -r requirements.txt
        cd ./xslt_generator/main/XSLT_Manager
        streamlit run xslt_manager.py
    else 
        echo "Please install version 3.12 of python first"
    fi
else
    echo "Please install version 3.12 of python first"
fi
# Check Python version
# Can use Poetry as well?
