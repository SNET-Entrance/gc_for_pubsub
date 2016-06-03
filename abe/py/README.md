# ABE client modules

requirement: install charm
* git clone https://github.com/JHUISI/charm.git
* install followning the instructions: https://github.com/JHUISI/charm
* notes for MAC OS X using mac-ports as installer (which is installing software in: /opt/local/) :
** install python3.x , py-parsing, GMP, PBC, OPENSSL
** ./configure.sh --enable-darwin --prefix=/opt/local --enable-docs --python=/opt/local/bin/python3.4
