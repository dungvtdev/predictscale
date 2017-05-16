from fabric.contrib.project import rsync_project
from fabric.api import run
from fabric.contrib.files import exists
from fabric import operations

import os
import subprocess

remote_horizon_dir = '~/DeployedProjects/'
ip = '192.168.1.226'
user = 'dung'
pwd = '123'

base_path = os.path.dirname(os.path.abspath(__file__))


def deploy():
    dashboard_dir = os.path.join(remote_horizon_dir,
                                 'client')
    dashboard_local_name = 'client'
    dashboard_local = os.path.join(base_path, dashboard_local_name)

    is_dir_exists = exists(dashboard_dir, use_sudo=False)
    if not is_dir_exists:
        run('mkdir -p %s' % dashboard_dir)
    rsync_project(local_dir=dashboard_local,
                  remote_dir=dashboard_dir, exclude='.git')

    # enabled_file_name = '_50_predictionscale.py'
    # dashboard_enabled_remote = os.path.join(remote_horizon_dir,
    #                                         'openstack_dashboard/enabled/%s' %
    #                                         enabled_file_name)
    # enabled_file_path = os.path.join(base_path, enabled_file_name)

    # operations.put(local_path=enabled_file_path,
    #                remote_path=dashboard_enabled_remote)


def test_name():
    run('uname -s')


def sync():
    file = os.path.abspath(__file__)

    command = 'deploy'

    r = subprocess.call(['fab',
                         '-f%s' % file,
                         '-u%s' % user,
                         '-p%s' % pwd,
                         '-H%s' % ip,
                         command])


if __name__ == '__main__':
    sync()
