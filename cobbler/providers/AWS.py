#!/usr/bin/python
import boto
import boto.ec2


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
    def __init__(self):
        inst = ConnectEC2()
        self.conn = inst.conn

    def _return_instance_objs(self, reservation_obj):
        return reservation_obj.instances

    def _return_instance_ids(self, instance_objs):
        return [inst_obj.id for inst_obj in instance_objs]

    def _run_sys(self, sys_nm, ami_nm, key_nm, inst_type, sec_grps):
        udat = "#!/bin/sh\n"
        udat += "#echo 'kernel.hostname = %s' >> /etc/sysctl.conf\n" % (sys_nm)
        udat += "sysctl -w kernel.hostname=%s\n" % (sys_nm)
        udat += "sysctl -p\n"
        udat += "echo 'it ran' > /root/yo.txt"
        reservation = self.conn.run_instances(ami_nm, key_name=key_nm,
                instance_type=inst_type, security_groups=sec_grps,
                user_data=udat)
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

    def return_sys_instance_obj(self, system_name, state=None):
        inst_objs = self.get_instance_objs(state=None)
        for inst_obj in inst_objs:
            tags = inst_obj.tags
            if 'Name' in tags and tags['Name'] == system_name:
                return inst_obj
        return False
