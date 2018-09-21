#!/usr/bin/env bash
keyfile=`mktemp`
sudo RGW_ACCESS_KEY_ID=testuser RGW_SECRET_ACCESS_KEY=t0pSecret radosgw-token --encode --ttype=ldap > ${keyfile} 
curdir=`pwd`
retstr=`python ${curdir}/ldap_client.py ${keyfile}`
rm -rf $keyfile
if [[ $retstr == testuser* ]]; then
    exit 0
fi
exit 1

