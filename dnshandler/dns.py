#!/usr/bin/env python

import subprocess
from logging import getLogger
import config_loader as loader
import os

logger = getLogger(__name__)

def add_entry(zone, domain, IP_addr, dns_server=None):
    result = {}
    try: 
        command = __update_dns("add", "A", zone, domain, IP_addr, dns_server)
        p = subprocess.Popen(command, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate()
        retcode = p.returncode
        if retcode != 0:
            raise Exception("could not add A entry. "+err)
        else:
            command = __update_dns("add", "PTR", zone, domain, IP_addr, dns_server)
            p = subprocess.Popen(command, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = p.communicate()
            retcode = p.returncode
            if retcode != 0:
                command2 = __update_dns("delete", "A", zone, domain, IP_addr,dns_server)
                p2 = subprocess.Popen(command2, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out2,err2 = p2.communicate()
                retcode2 = p2.returncode
                if retcode2 !=0:
                    raise Exception("could not add PTR entry. "+err+"Could not execute rollback. "+err2)
                else:
                    raise Exception("could not add PTR entry. "+err)
            else:
                result['status'] = 'success'
                result['message'] = "entry added successfully"
                result['data'] = None
                
    except Exception, e:
        logger.error(e)
        result['status'] = 'error'
        result['message'] = e
        result['data'] = None
    finally:
        return result
        

            
def delete_entry(zone, domain, IP_addr,dns_server=None):
    result = {}
    try:
        command = __update_dns("delete", "A", zone, domain, IP_addr, dns_server)
        p = subprocess.Popen(command, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate()
        retcode = p.returncode
        if retcode != 0:
            raise Exception("could not delete A entry. "+err)
        else:
            command = __update_dns("delete", "PTR", zone,  domain, IP_addr, dns_server)
            p = subprocess.Popen(command, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out,err = p.communicate()
            retcode = p.returncode
            if retcode != 0:
                command2 = __update_dns("add", "A", zone, domain, IP_addr, dns_server)
                p2 = subprocess.Popen(command2, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out2,err2 = p2.communicate()
                retcode2 = p2.returncode
                if retcode2 !=0:
                    raise Exception("could not delete PTR entry. "+err+"Could not execute rollback"+err2)
                else:
                    raise Exception("could not delete PTR entry. "+err)
            else:
                result['status'] = 'success'
                result['message'] = "entry deleted successfully"
                result['data'] = None
    except Exception, e:
        logger.error(e)
        result['status'] = 'error'
        result['message'] = e
        result['data'] = None
    finally:
        return result
        


def get_address(host):
    result = {}
    try: 
        p = subprocess.Popen("host "+host, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate()
        retcode = p.returncode
        if retcode != 0:
            raise Exception("could not get address. "+err)
        else:
            addr = out.split()[-1]
            result['status'] = 'success'
            result['message'] = None
            result['data'] = addr
    except Exception, e:
        logger.error(e)
        result['status'] = 'error'
        result['message'] = e
        result['data'] = None
    finally:
        return result
    
def get_host(IP_addr):
    result = {}
    try: 
        p = subprocess.Popen("host "+IP_addr, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = p.communicate()
        retcode = p.returncode
        if retcode != 0:
            raise Exception("could not get host. "+err)
        else:
            host = out.split()[-1][:-1]
            result['status'] = 'success'
            result['message'] = None
            result['data'] = host
    except Exception, e:
        logger.error(e)
        result['status'] = 'error'
        result['message'] = e
        result['data'] = None
    finally:
        return result

        
def __update_dns(operation, type, zone, domain, IP_addr, dns_server):
    try:
        config = {}
        loader.load_config_file('%s/config/config.json' % os.path.dirname(os.path.abspath(__file__)), config)
        
        assert('dns' in config)
        assert('keys' in config['dns'])
        assert('ttl' in config['dns'])
        
        keyfile = config['dns']['keys']
        TTL = config['dns']['ttl']
        server = ""
        if config['dns']['server']:
            server = config['dns']['server']
        if dns_server:
            server = dns_server
        server = get_address(server)
        if server["status"] == "success":
            dns_server = server["data"]
        else:
            raise  Exception("could not get dns server ip address")
        
        if type == "A":
            tmp1 = domain + "." + zone
            tmp2 = IP_addr
            tmp3 = zone
        else:
            tmp1 = IP_addr.split(".")[3] + "." + IP_addr.split(".")[2] + "." +  IP_addr.split(".")[1] + "." + IP_addr.split(".")[0] + ".in-addr.arpa"
            tmp2 = domain + "." + zone
            tmp3 = dns_server.split(".")[1] + "." + dns_server.split(".")[0] + ".in-addr.arpa"
            
        entry  = "server %s\n" % dns_server
        entry += "zone %s\n" % tmp3
        entry += "prereq %s %s IN %s\n" % ("nxrrset" if operation == "add" else "yxrrset", tmp1, type)
        entry += "update %s %s %s IN %s %s\n" % (operation, tmp1, TTL, type, tmp2)
        entry += "send\nquit"
        if keyfile:
            entry = "nsupdate -k {0} << EOF\n{1}\nEOF\n".format(keyfile, entry)
        else:
            entry = "nsupdate << EOF\n{0}\nEOF\n".format(entry)
        return entry
    except Exception, e:
        raise