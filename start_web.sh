#!/bin/sh
echo '. env/bin/activate;pserve --daemon development.ini' | scl enable python27 -

