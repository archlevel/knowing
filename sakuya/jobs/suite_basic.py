# -*- coding: utf-8 -*-

import argparse
import json
import urllib2
import time
import datetime
import yaml
import errno
import signal
import logging
from contextlib import closing
from pysnmp.entity.rfc3413.oneliner import cmdgen
from sakuya.config import get_config
from sakuya.lib import util

STATS_INTERVAL = 60 # 60"

SUITE_DATA_API = get_config('webapp')['base_url'] + '/api/suite-data'

class Job(object):

    interrupted = False

    def __init__(self, args):
        self.args = args

        util.setup_logging('suite_basic', True)

        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

        with open(get_config('webapp')['suite_hosts']) as f:
            self.groups = yaml.load(f.read())

        self.cmdgen = cmdgen.CommandGenerator()

    def signal_handler(self, signum, frame):
        if signum == signal.SIGTERM or signum == signal.SIGINT:
            self.interrupted = True

    def get(self, host, oids):

        errorIndication, errorStatus, errorIndex, varBinds = self.cmdgen.getCmd(
            cmdgen.CommunityData('public'),
            cmdgen.UdpTransportTarget((host, 161)),
            *(cmdgen.MibVariable(*oid) for oid in oids),
            lookupNames=True, lookupValues=True
        )

        result = {}
        for name, val in varBinds:
            mib, sym, indices = name.getMibSymbol()
            try:
                val = int(val)
            except Exception, e:
                val = 0
            result[(mib, sym, int(str(indices[0])))] = val

        return result

    def run(self):

        now = datetime.datetime.now()
        self.next_time = now.replace(second=0, microsecond=0) + datetime.timedelta(seconds=STATS_INTERVAL)

        while not self.interrupted:
            now = datetime.datetime.now()
            if now >= self.next_time:
                stats_time = now.replace(second=0, microsecond=0)
                self.next_time = stats_time + datetime.timedelta(seconds=STATS_INTERVAL)

                try:
                    self.process(stats_time)
                except Exception, e:
                    logging.exception('Fail to process.')

            time.sleep(1)

    def process(self, stats_time):

        for groupname, hosts in self.groups.iteritems():

            host_result = {}
            for hostname, hostinfo in hosts.iteritems():
                try:
                    host_result[hostname] = self.process_host(hostinfo['ip'], hostinfo['num_cores'])
                except Exception, e:
                    logging.exception('Fail to process host.')

            if not host_result:
                continue

            try:
                host_result['汇总'] = self.process_group(host_result)
            except Exception, e:
                logging.exception('Fail to process group.')
            else:
                self.post_result(stats_time, groupname.encode('utf-8'), host_result)

    def process_host(self, ip, num_cores):

        snmp_res = self.get(ip, [('UCD-SNMP-MIB', 'laLoadInt', 1),
                                 ('UCD-SNMP-MIB', 'memTotalReal', 0),
                                 ('UCD-SNMP-MIB', 'memAvailReal', 0),
                                 ('UCD-SNMP-MIB', 'memBuffer', 0),
                                 ('UCD-SNMP-MIB', 'memCached', 0),
                                 ('UCD-SNMP-MIB', 'dskTotal', 1),
                                 ('UCD-SNMP-MIB', 'dskUsed', 1)])

        result = {}

        load = snmp_res[('UCD-SNMP-MIB', 'laLoadInt', 1)]
        result['Load'] = float(load) / 100 / num_cores

        mem_total = snmp_res[('UCD-SNMP-MIB', 'memTotalReal', 0)]
        mem_avail = snmp_res[('UCD-SNMP-MIB', 'memAvailReal', 0)]
        mem_buffer = snmp_res[('UCD-SNMP-MIB', 'memBuffer', 0)]
        mem_cached = snmp_res[('UCD-SNMP-MIB', 'memCached', 0)]
        result['Memory'] = 1 - float(mem_avail + mem_buffer + mem_cached) / mem_total

        dsk_total = snmp_res[('UCD-SNMP-MIB', 'dskTotal', 1)]
        dsk_used = snmp_res[('UCD-SNMP-MIB', 'dskUsed', 1)]
        result['Disk'] = float(dsk_used) / dsk_total

        return dict((k, int(round(v * 10000))) for (k, v) in result.iteritems())

    def process_group(self, host_result):

        result = dict((k, []) for k in host_result[host_result.keys()[0]].keys())

        for hostname, data in host_result.iteritems():
            for datasource ,value in data.iteritems():
                result[datasource].append((hostname, value))

        for datasource, value_list in result.iteritems():
            if not value_list:
                continue
            avg = int(round(float(sum(v[1] for v in value_list)) / len(value_list)))
            value_list.sort(key=lambda x: x[1], reverse=True)
            result[datasource] = (avg, json.dumps(value_list[:10]))

        return result

    def post_result(self, stats_time, groupname, host_result):

        for hostname, data in host_result.iteritems():

            body = {
                'category': ['基础监控', groupname, hostname],
                'data': data,
                'datetime': stats_time.strftime('%Y-%m-%d %H:%M')
            }

            if self.args.test:
                print 'category:', ' - '.join(body['category'])
                print 'data:', body['data']
                continue

            req = urllib2.Request(url=SUITE_DATA_API, data=json.dumps(body))
            try:
                with closing(urllib2.urlopen(req)) as f:
                    ret = json.loads(f.read())
                    logging.info('::'.join(body['category']) + ', ' + ret['status'].encode('utf-8'))
            except Exception, e:
                logging.exception('Fail to post host.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()

    job = Job(args)
    if args.test:
        job.process(datetime.datetime.now())
    else:
        job.run()
