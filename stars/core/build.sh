#!/usr/bin/env bash 

MOD_NAME=$1

swig -c++ -python -o ${MOD_NAME}_wrap.cpp ${MOD_NAME}.i 

python setup.py build_ext --inplace

#gcc -c++ -fPIC -c ${MOD_NAME}.cpp -o ${MOD_NAME}.o -I/usr/include/python2.5 -I/usr/lib/python2.5

#gcc -c++ -fPIC -c ${MOD_NAME}_wrap.cpp -o ${MOD_NAME}_wrap.o -I/usr/include/python2.5 -I/usr/lib/python2.5 

#gcc -bundle -flat_namespace -undefined suppress -o _${MOD_NAME}.so ${MOD_NAME}.o ${MOD_NAME}_wrap.o 
