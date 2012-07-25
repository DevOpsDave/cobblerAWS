#!/usr/bin/python
import boto
import boto.ec2
from string import Template


class ConnectEC2(object):

    def __init__(self, region='us-east-1', aws_access_key_id=None,
            aws_secret_access_key=None):
        self.region = region
        self.creds = {'key_id': aws_access_key_id,
                'key_secret': aws_secret_access_key}
        self.conn = self._connect_()

    def _connect_(self):
        if (self.creds['key_id'] or self.creds['key_secret']) is None:
            conn = boto.ec2.connect_to_region(self.region)
            return conn
        else:
            conn = boto.ec2.connect_to_region(self.region,
                    aws_access_key_id=self.creds['key_id'],
                    aws_secret_access_key=self.creds['key_secret'])
            return conn


class SystemAWS(object):

    """
    Private
    """
    def __init__(self, user_data='/root/work/cobblerAWS/cloud-config.txt'):
        inst = ConnectEC2()
        self.conn = inst.conn
        self.user_data = open(user_data).read()

    def _return_instance_objs(self, reservation_obj):
        return reservation_obj.instances

    def _return_instance_ids(self, instance_objs):
        return [inst_obj.id for inst_obj in instance_objs]

    def _run_sys(self, sys_nm, ami_nm, key_nm, inst_type, sec_grps):
        user_data = Template(self.user_data).safe_substitute(sys_nm=sys_nm)
        reservation = self.conn.run_instances(ami_nm, key_name=key_nm,
                instance_type=inst_type, security_groups=sec_grps,
                user_data=user_data)
        reservation.instances[0].add_tag('Name', sys_nm)
        return reservation

    def _terminate_instances(self, instance_id_list):
        self.conn.terminate_instances(instance_ids=instance_id_list)

    def _stop_instances(self, instance_id_list):
        self.conn.stop_instances(instance_ids=instance_id_list)

    """
    Public
    """
    def get_instance_objs(self, state=None):
        instances = []
        reservations = self.conn.get_all_instances()
        for res in reservations:
            instobj_list = self._return_instance_objs(res)
            instances += instobj_list
        return instances

    def get_sys_by_name(self, system_name, state=None):
        inst_objs = self.get_instance_objs(state=None)
        for inst_obj in inst_objs:
            tags = inst_obj.tags
            if 'Name' in tags and tags['Name'] == system_name:
                return inst_obj
        return False

    def provision_host(self, sys_nm, ami_nm, inst_type='t1.micro',
            key_name='dbarcelo-omnia',
            sec_grps=['quick-start-1']):

        inst = self.get_sys_by_name(sys_nm, state='Running')
        if inst is False or inst.state != 'running':
            new_host = self._run_sys(sys_nm, ami_nm, key_name, inst_type, sec_grps)
            return new_host
        else:
            return False

    def decomision_host(self, sys_nm):
        inst = self.get_sys_by_name(sys_nm)
        if inst is not None and str(inst.state) != 'running':
            self._terminate_instances([inst.id])
        else:
            return False

