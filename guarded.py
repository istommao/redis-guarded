"""redis guarded"""
import re
import subprocess


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


def main():
    """main."""
    info = get_redis_output()
    return format_output(info)


if __name__ == '__main__':
    dataset = main()
    print(dataset)
