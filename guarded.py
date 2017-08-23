#-*- coding:utf-8 -*-
"""redis guarded"""
from __future__ import print_function

import json

import re
import socket
import subprocess
import time
import urllib2

__author__ = 'silence'


def getoutput(cmd):
    """getoutput."""
    try:
        _, info = subprocess.getstatusoutput(cmd)
    except AttributeError:
        # py2
        import commands
        info = commands.getoutput(cmd)
    return info


def get_redis_output(host='127.0.0.1', port='6379'):
    """Get redis output info."""
    redis_cli = '/usr/local/bin/redis-cli'
    cmd = '{} -h {} -p {} info'.format(redis_cli, host, port)
    return getoutput(cmd)


def format_output(info):
    """Format output."""
    regex = r'(\w+):([\w\-\=\/\,\.]*)[\r\n]{0,1}'
    return dict(re.findall(regex, info))


def format_value(key, dataset):
    if key == 'keyspace_hit_ratio':
        try:
            value = float(
                dataset['keyspace_hits']) / (int(dataset['keyspace_hits']) +
                                             int(dataset['keyspace_misses']))
        except ZeroDivisionError:
            value = 0
    elif key == 'mem_fragmentation_ratio':
        value = float(dataset[key])
    else:
        value = int(dataset[key])

    return value


def main():
    """main."""
    info = get_redis_output()
    dataset = format_output(info)

    timestamp = int(time.time())
    step = 60

    hostname = socket.gethostname()

    metric = "redis"
    endpoint = hostname
    tags = 'port=%s' % '6379'

    monit_keys = [
        ('connected_clients', 'GAUGE'),
        ('blocked_clients', 'GAUGE'),
        ('used_memory', 'GAUGE'),
        ('used_memory_rss', 'GAUGE'),
        ('mem_fragmentation_ratio', 'GAUGE'),
        ('total_commands_processed', 'COUNTER'),
        ('rejected_connections', 'COUNTER'),
        ('expired_keys', 'COUNTER'),
        ('evicted_keys', 'COUNTER'),
        ('keyspace_hits', 'COUNTER'),
        ('keyspace_misses', 'COUNTER'),
        ('keyspace_hit_ratio', 'GAUGE'),
    ]

    datalst = []

    for key, vtype in monit_keys:
        if key not in dataset:
            continue

        value = format_value(key, dataset)

        item = {
            'Metric': '%s.%s' % (metric, key),
            'Endpoint': endpoint,
            'Timestamp': timestamp,
            'Step': step,
            'Value': value,
            'CounterType': vtype,
            'TAGS': tags
        }
        datalst.append(item)

    post_data(datalst)


def post_data(datalst):
    """Post Data."""
    opener = urllib2.build_opener(urllib2.HTTPHandler())

    url = 'http://127.0.0.1:1988/v1/push'

    request = urllib2.Request(url, data=json.dumps(datalst))
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'POST'

    try:
        conn = opener.open(request)
    except urllib2.HTTPError as error:
        print(error)

    if conn.code == 200:
        print(conn.read())


if __name__ == '__main__':
    main()
