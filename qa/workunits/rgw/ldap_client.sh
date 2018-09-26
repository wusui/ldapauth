#!/usr/bin/env bash
exit 0
keyfile=`mktemp`
sudo RGW_ACCESS_KEY_ID=testuser RGW_SECRET_ACCESS_KEY=t0pSecret radosgw-token --encode --ttype=ldap > ${keyfile} 
curdir=`pwd`
retstr=`python ${curdir}/ldap_client.py ${keyfile}`
rm -rf $keyfile
if [[ $retstr == testuser* ]]; then
    echo "LDAP authentication worked"
    exit 0
fi
exit 1
