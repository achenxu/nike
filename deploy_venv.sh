#!/bin/bash
set -e
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Creating virtualenv .venv"
    virtualenv .venv
    source .venv/bin/activate
else
    echo "Virtualenv $VIRTUAL_ENV currently active. Using it."
fi
pip install -r requirements.txt
echo "Now you are in virtual environment, enjoy!"
if [ -e "/bin/zsh" ]; then 
    /bin/zsh
else 
    /bin/bash
fi
