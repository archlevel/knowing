# -*- coding: utf-8 -*-

import urllib2
import logging
from sakuya.config import get_config

def get_belongto(ip):

    belongto = None
    try:
        #f = urllib2.urlopen(get_config('webapp')['zeus_api_url'] + '/item/get_belongto_by_ip?ip=' + ip, None, 3)
        f = urllib2.urlopen(get_config('webapp')['zeus_api_url'] + '/item/get_label_by_ip?ip=' + ip, None, 3)
        belongto = f.read()
    except Exception, e:
        logging.exception('Fail to get belongto for ip %s' % ip)
    finally:
        try:
            f.close()
        except Exception, e:
            pass

    return belongto
