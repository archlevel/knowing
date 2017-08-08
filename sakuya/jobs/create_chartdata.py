# -*- coding: utf-8 -*-

import argparse
import datetime
import MySQLdb

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--host', default='192.168.1.103')
    parser.add_argument('-P', '--port', type=int, default=3306)
    parser.add_argument('-u', '--username', default='caixh')
    parser.add_argument('-p', '--password', default='caixh123')
    parser.add_argument('-d', '--database', default='OPS_Monitor')
    parser.add_argument('-s', '--start', required=True)
    parser.add_argument('-e', '--end', required=True)
    args = parser.parse_args()

    try:
        start = datetime.datetime.strptime(args.start, '%Y-%m-%d')
        end = datetime.datetime.strptime(args.end, '%Y-%m-%d')
        if start > end:
            raise ValueError
    except Exception, e:
        print 'Invalid start/end value.'
        return

    conn = MySQLdb.connect(host=args.host,
                           port=args.port,
                           user=args.username,
                           passwd=args.password,
                           db=args.database)
    c = conn.cursor()

    while start <= end:
        tbl_name = 't_chartdata_%s' % start.strftime('%Y%m%d')
        print 'Create', tbl_name
        c.execute('''
CREATE TABLE IF NOT EXISTS `%s` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `f_ds_id` int(11) NOT NULL,
  `f_time` datetime NOT NULL,
  `f_data` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx1` (`f_ds_id`,`f_time`)
)''' % tbl_name)
        start += datetime.timedelta(1)

    conn.commit()

if __name__ == '__main__':
    main()
