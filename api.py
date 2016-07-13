import os
import subprocess


naming_fixes = {'keystone-all':'keystone'}


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def cprint(msg, color):
    print color + msg + bcolors.ENDC


def execute(cmd):
    pp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    outp, err = pp.communicate()
    if pp.returncode != 0:
        raise RuntimeError('Process returned non-zero code %i' % pp.returncode)
    return outp.strip()


def get_services_list(node):
    services = execute("ssh %s 'ps -aux' | grep 'python.*config-file' | awk '{print $12}' |  sort -u" % node)
    services = [os.path.basename(path) for path in services.split('\n')]
    cprint('[ Founded OpenStack Services on % s ]' % node, bcolors.OKBLUE)
    for i, s in enumerate(services):
	if s in naming_fixes:
	   services[i] = naming_fixes[s]
        print ' --- %s' % s
    return services


def get_resources_list(node):
    cprint('[Resources list on %s]' % node, bcolors.OKGREEN)
    resources = execute("ssh %s 'crm_resource --list-raw'" % node).split('\n')
    print resources
    return resources


def split_services_by_crm(node):
    services = get_services_list(node)
    resources = get_resources_list(node)

    controlled_by_init = []
    controlled_by_pm = []

    for s in services:
        matched = False
        for r in resources:
            if s in r:
                if ':' in r:
                    r = r.split(':')[0]
                controlled_by_pm.append(r)
                matched = True
                break
        if not matched:
            controlled_by_init.append(s)
    return controlled_by_init, controlled_by_pm


def restart_services(node, services):
    # controlled by initd and pacemaker
    cprint('[ Restarting services %s ... ]' % node, bcolors.WARNING)
    for service in services:
        print 'restarting: %s'%service
	print execute("ssh %s 'service %s restart'" % (node, service))


def restart_resources(node, resources):
    cprint('[ Restarting resources %s ... ]' % node, bcolors.WARNING)
    for resource in resources:
        print execute("ssh %s 'crm resource restart %s'" % (node, resource))


def fuel_controllers():
    return execute("fuel nodes 2>&1 | grep controller | awk '{ print $9 }'").split('\n')


def fuel_computes():
    return execute("fuel nodes 2>&1 | grep compute | awk '{ print $9 }'").split('\n')





def copy_patch(nodes):
    filename = 'monitor.patch'
    for node in nodes:
        location = '/usr/lib/python2.7/dist-packages/'
        print '[ copying files to %s ]' % node
        print execute('scp %s %s:%s' % (filename, node, location))
        print '[ apply patch to oslo.messaging %s ]' % node
        print execute("ssh %s 'cd %s && patch -p0 < ./%s'" % (node, location, filename))
        print '[ remove patch file %s ]' % node
        print execute("ssh %s 'rm %s/%s'" % (node, location, filename))
