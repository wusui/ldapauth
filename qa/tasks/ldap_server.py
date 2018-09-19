"""
ldap_server
"""
import logging
import contextlib
import time

from teuthology.orchestra import run
from teuthology import misc

log = logging.getLogger(__name__)

@contextlib.contextmanager
def task(ctx, config):
    """
    Start up an ldap_server in order to test ldap rgw authentication 
    
    Usage
       tasks:
       - ldap_server:
           [client.0]

    Note: the ldap server runs on a teuthology client, so the client
          references in this file are ldap server references.
    """

    log.info('in ldap_server')
    assert isinstance(config, list)
    (client,) = ctx.cluster.only(config[0]).remotes
    system_type = misc.get_system_type(client)
    if system_type == 'rpm':
        install_cmd = ['sudo', 'yum', '-y', 'install', 'ipa-server', 'ipa-server-dns']
        #fix_mod_ssl = ['sudo', 'yum', '-y', 'remove', 'mod_ssl']
    else:
        install_cmd = ['sudo', 'apt-get', '-y', 'install', 'freeipa-server', 'freeipa-server-dns']
        #fix_mod_ssl = []
    client.run(args=install_cmd)
    #if fix_mod_ssl:
    #    client.run(args=fix_mod_ssl)
    #    client.run(args=['sudo', 'systemctl', 'restart', 'messagebus'])
    path_parts = ctx.cluster.remotes.keys()[0].name.split('.')[1:]
    client.run(args=['sudo',
                'ipa-server-install',
                '--realm',
                '.'.join(path_parts),
                '--ds-password',
                't0pSecret',
                '--admin-password',
                't0pSecret',
                '--unattended'])
    time.sleep(120)
    client.run(args=['echo', 
                     't0pSecret',
                     run.Raw('|'),
                     'kinit',
                     'admin'])
    client.run(args=['ipa', 'user-add', 'rgw',
                     '--first', 'rados', '--last', 'gateway'])
    #client.run(args=['ipa', 'user-add', 'ceph',
    #                 '--first', 'rados', '--last', 'gateway'])
    client.run(args=['ipa', 'user-add', 'testuser',
                     '--first', 'new', '--last', 'user'])
    #client.run(args=['echo',
    #                 't0pSecret\nt0pSecret',
    #                 run.Raw('|'),
    #                 'ipa', 
    #                 'user-mod',
    #                 'ceph',
    #                 '--password'])
    client.run(args=['echo',
                     't0pSecret\nt0pSecret',
                     run.Raw('|'),
                     'ipa', 
                     'user-mod',
                     'rgw',
                     '--password'])
    client.run(args=['echo',
                     't0pSecret\nt0pSecret',
                     run.Raw('|'),
                     'ipa',
                     'user-mod',
                     'testuser',
                     '--password'])
    #client.run(args=['sudo', 'useradd', 'ceph'])
    #client.run(args=['echo', 't0pSecret\nt0pSecret', run.Raw('|'), 'sudo',
    #                 'passwd', 'ceph'])
    #client.run(args=['sudo', 'useradd', 'testuser'])
    #client.run(args=['echo', 't0pSecret\nt0pSecret', run.Raw('|'), 'sudo',
    #                 'passwd', 'testuser'])
    try:
        yield
    finally:
        client.run(args=[ 'yes',
                          run.Raw('|'),
                          'sudo',
                          'ipa-server-install',
                          '--uninstall'])
