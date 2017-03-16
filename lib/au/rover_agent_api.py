#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import socket
from struct import Struct, pack, unpack
from collections import namedtuple

from .protocol import *

DEFAULT_AGENT_HOST = '127.0.0.1'
DEFAULT_AGENT_PORT = '8888'
DEFAULT_AGENT_ADDR = DEFAULT_AGENT_HOST + ':' + DEFAULT_AGENT_PORT

CmdPkt = namedtuple('CmdPkt',('subsys','cmd','arg1','arg2','arg3','arg4'))
RespPkt = namedtuple('RespPkt', ('subsys', 'status', 'val1', 'val2', 'val3', 'val4',
    'data_bytes', 'data'))

_pkt_struct = Struct('I H H iiii i I')

_agent_status = [
    "okay",
    "general error",
    "rover function not implemented",
    "unknown rover subsystem",
    "unknown subsystem function",
    "bad subsystem function parameter"
    ]

def float_as_int(fval):
    return unpack('i', pack('f', fval))[0]

def int_as_float(ival):
    return unpack('f', pack('i', ival))[0]


class AgentException(Exception):
    def __init__(self, arg):
        if isinstance(arg, int) and arg >= 0 and arg < len(_agent_status):
            arg = _agent_status[arg]
        super(AgentException, self).__init__(arg)


class AgentConnection(object):

    def set_agent_addr(self, addr):
        if addr is None or not addr:
            if 'AGENT_ADDR' in os.environ:
                addr = os.environ['AGENT_ADDR']
            else:
                addr = DEFAULT_AGENT_ADDR
        addr_parts = addr.split(':')
        host = addr_parts[0]
        if not host:
            host = DEFAULT_AGENT_HOST
        port = ''
        if len(addr_parts) > 1:
            port = addr_parts[1]
        if not port:
            port = DEFAULT_AGENT_PORT
        self.addr = addr
        self.host = host
        self.port = int(port)

    def __init__(self, agent_addr=None):
        self.set_agent_addr(agent_addr)
        self.socket = None
        self.connected = False
        try:
            self.recv_flags = socket.MSG_WAITALL
        except AttributeError:
            self.recv_flags = 0

    def connect(self, agent_addr=None):
        if self.connected:
            if not agent_addr:
                return 0
            else:
                raise AgentException("Cannot change agent address while connected")
        if agent_addr:
            self.set_agent_addr(agent_addr)
        self.socket = socket.create_connection((self.host, self.port))
        self.connected = True
        return 0

    def close(self):
        if not self.connected:
            return 0
        self.socket.close()
        self.connected = False
        return 0

    def send_cmd(self, subsys, cmd, arg1=0, arg2=0, arg3=0, arg4=0):
        pkt_bytes = _pkt_struct.pack(IDENT, subsys, cmd, arg1, arg2, arg3, arg4, 0, 0)
        self.socket.sendall(pkt_bytes)
        return 0

    def get_resp(self):
        pkt_bytes = self.socket.recv(PKT_LEN, self.recv_flags)
        while len(pkt_bytes) < PKT_LEN:
            fragment = self.socket.recv(PKT_LEN - len(pkt_bytes), self.recv_flags)
            if fragment == b'':
                raise RuntimeError("socket connection broken")
            pkt_bytes += fragment
        (ident, subsys, status, val1, val2, val3, val4,
            reserved, data_bytes) = _pkt_struct.unpack(pkt_bytes)
        if data_bytes > 0:
            data = self.socket.recv(data_bytes, self.recv_flags)
            while len(data) < data_bytes:
                fragment = self.socket.recv(data_bytes - len(data), self.recv_flags)
                if fragment == b'':
                    raise RuntimeError("socket connection broken")
                data += fragment
        else:
            data = b''
        resp = RespPkt(subsys, status, val1, val2, val3, val4, data_bytes, data)
        return resp

    def cmd_resp(self, subsys, cmd, arg1=0, arg2=0, arg3=0, arg4=0):
        self.send_cmd(subsys, cmd, arg1, arg2, arg3, arg4)
        return self.get_resp()



class SubSystem(object):

    def __init__(self, subsys_ID, connection=None):
        self.ID = subsys_ID
        self.ac = connection

class SystemSubsys(SubSystem):

    def __init__(self, connection=None):
        super(SystemSubsys, self).__init__(SUBSYS_SYSTEM, connection)

    def connect(self, agent_addr=None):
        self.ac.connect(agent_addr)
        resp = self.ac.cmd_resp(SUBSYS_SYSTEM, SYSTEM_CONNECT)
        status = resp.status
        if status:
            raise AgentException(status)
        pver = resp.val1
        pvmin = resp.val2
        if pver != PROTOCOL_VERSION or pvmin != PROTOCOL_MINOR:
            print("** WARNING: PROTOCOL VERSION MISMATCH!")
            print("   CLIENT = %d.%d but SERVER = %d.%d" % (PROTOCOL_VERSION,
                PROTOCOL_MINOR, pver, pvmin))
        return pver, pvmin

    def disconnect(self):
        resp = self.ac.cmd_resp(self.ID, SYSTEM_DISCONNECT)
        status = resp.status
        if status:
            raise AgentException(status)
        self.ac.close()

    def command(self, cmd):
        cmd = cmd.lower()
        if cmd == 'quit' or cmd == 'shutdown':
            resp = self.ac.cmd_resp(self.ID, SYSTEM_SHUTDOWN)
            status = resp.status
            if status:
                raise AgentException(status)
            return
        else:
            raise AgentException('unrecognised agent command: %s' % cmd)

    def get_version(self):
        resp = self.ac.cmd_resp(self.ID, SYSTEM_GET_VERSION)
        status = resp.status
        if status:
            raise AgentException(status)
        return resp.val1


class ImageFrame(object):

    def __init__(self, width=0, height=0, depth=0, format=0, image_bytes=0, image=b''):
        self.width = width
        self.height = height
        self.depth = depth
        self.format = format
        self.image_bytes = image_bytes
        self.image = image

    def tostring(self):
        return self.image

    def tobytes(self):
        return self.image

    def save_ppm(self, filename):
        if self.depth == 1 and (self.format == IMAGE_FORMAT_MONO8
                or self.format == IMAGE_FORMAT_BAYER):
            # 8-bit grey
            with open(filename, 'wb') as f:
                f.write(("P5\n%d %d\n255\n" % (self.width, self.height)).encode('ascii'))
                f.write(self.image)
        elif self.depth == 3 and self.format == IMAGE_FORMAT_RGB8:
            # 8-bit RGB
            with open(filename, 'wb') as f:
                f.write(("P6\n%d %d\n255\n" % (self.width, self.height)).encode('ascii'))
                f.write(self.image)
        elif self.depth == 2 and self.format == IMAGE_FORMAT_MONO16:
            # 16-bit grey (?? ENDIANNESS ??)
            with open(filename, 'wb') as f:
                f.write(("P5\n%d %d\n65535\n" % (self.width, self.height)).encode('ascii'))
                f.write(self.image)
        else:
            raise AgentException("Cannot save image as PPM (format %d, depth %d)" %
                (self.format, self.depth))


class PanCamSubsys(SubSystem):

    def __init__(self, connection=None):
        super(PanCamSubsys, self).__init__(SUBSYS_PANCAM, connection)
        self.config = None
        self.cameras = []

    #=========== Camera control ==========

    def get_image(self, camera_id, image_format, image_frame, flags=0):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_IMAGE, camera_id, image_format, flags)
        status = resp.status
        if status:
            return status
        image_frame.width = resp.val1
        image_frame.height = resp.val2
        image_frame.depth = resp.val3
        image_frame.image_bytes = resp.val4
        image_frame.image = resp.data
        image_frame.format = image_format
        return 0

    def get_image_rgb(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_RGB8, image_frame, flags=flags)

    def get_image_yuv(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_YUV422, image_frame, flags=flags)

    def get_image_mono(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO8, image_frame, flags=flags)

    def get_image_raw(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_BAYER, image_frame, flags=flags)

    def get_image_mono8(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO8, image_frame, flags=flags)

    def get_image_mono16(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO16, image_frame, flags=flags)

    def get_image_mono12p(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO12P, image_frame, flags=flags)

    def set_feature(self, camera_id, feature, feature_val, feature_val2=0):
        resp = self.ac.cmd_resp(self.ID, CAM_SET_FEATURE_VALUE,
            camera_id, feature, feature_val, feature_val2)
        status = resp.status
        return status

    def set_abs_feature(self, camera_id, feature, feature_aval):
        resp = self.ac.cmd_resp(self.ID, CAM_SET_FEATURE_ABS_VALUE,
            camera_id, feature, float_as_int(feature_aval))
        status = resp.status
        return status

    def get_feature(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_FEATURE_VALUE,
            camera_id, feature)
        return resp.status, resp.val1

    def get_feature2(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_FEATURE_VALUE,
            camera_id, feature)
        return resp.status, resp.val1, resp.val2

    def get_abs_feature(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_FEATURE_ABS_VALUE,
            camera_id, feature)
        return resp.status, int_as_float(resp.val1)

    def set_feature_mode(self, camera_id, feature, mode):
        resp = self.ac.cmd_resp(self.ID, CAM_SET_FEATURE_MODE,
            camera_id, feature, mode)
        return resp.status

    def get_feature_mode(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_FEATURE_MODE,
            camera_id, feature)
        return resp.status, resp.val1

    def get_image_metadata(self, camera_id, _pattern = '<' + ('i' * METADATA_NUM_VALUES)):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_IMAGE_METADATA, camera_id)
        if resp.status:
            return resp.status, 0, ()
        metadata = unpack(_pattern, resp.data)
        return resp.status, resp.val2, metadata

    def discard_frames(self, camera_id, nframes, discard_mode):
        resp = self.ac.cmd_resp(self.ID, CAM_DISCARD_FRAMES, camera_id, nframes,
            discard_mode)
        return resp.status, resp.val1, resp.val2

    #================= Filter wheel control ================

    def set_filter(self, camera_id, filter_no):
        resp = self.ac.cmd_resp(self.ID, CAM_SET_FILTER,
            camera_id, filter_no)
        return resp.status

    def get_filter(self, camera_id):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_FILTER, camera_id)
        return resp.status, resp.val1

    def get_filter_info(self, camera_id):
        resp = self.ac.cmd_resp(self.ID, CAM_GET_FILTER, camera_id)
        # return filter no, central wavelength, bandwidth in nm, filter set id num
        return resp.status, resp.val1, resp.val2, resp.val3, resp.val4

    #============ Misc.configuration info ===========

    def get_pancam_config(self):
        if self.config is None:
            resp = self.ac.cmd_resp(self.ID, CAM_GET_PANCAM_CONFIG)
            if resp.status:
                raise AgentException("Cannot get pancam configuration")
            self.config = {}
            lines = resp.data.decode('ascii', errors='replace')
            for line in lines.split('\n'):
                if line.strip():
                    v = line.split('\t')
                    self.config[int(v[0])] = v
        return self.config

    def setup_cameras(self, set_exposure=False):
        for cam in self.cameras:
            cam.setup_info()
            if set_exposure:
                cam.shutter_mode = FEATURE_MODE_MANUAL
                cam.shutter = 0.02  # 1/50 sec
                cam.gain_mode = FEATURE_MODE_MANUAL
                if cam.info.model.startswith("DMK") or cam.info.model.startswith("DFK"):
                    cam.gain = 400  # Imaging Source Firewire camera
                else:
                    cam.gain = 0    # AVT/Prosilica GigE Vision camera

    def get_config(self, camera_id):
        if self.config is None:
            self.get_pancam_config()
        if camera_id in self.config:
            return self.config[camera_id]
        else:
            return None


class MastSubsys(SubSystem):

    def __init__(self, connection=None):
        super(MastSubsys, self).__init__(SUBSYS_MAST, connection)

    #================= Pan/tilt control ================

    def set_pan_tilt(self, pan, tilt):
        ipan = int(pan * 1.0 * ANG_SCALE)
        itilt = int(tilt * 1.0 * ANG_SCALE)
        resp = self.ac.cmd_resp(self.ID, PTU_SET_ALL_JOINTS, ipan, itilt)
        return resp.status

    def set_pan(self, pan):
        ipan = int(pan * 1.0 * ANG_SCALE)
        resp = self.ac.cmd_resp(self.ID, PTU_SET_ONE_JOINT, PTU_PAN, ipan)
        return resp.status

    def set_tilt(self, tilt):
        itilt = int(tilt * 1.0 * ANG_SCALE)
        resp = self.ac.cmd_resp(self.ID, PTU_SET_ONE_JOINT, PTU_TILT, itilt)
        return resp.status

    def stow(self):
        resp = self.ac.cmd_resp(self.ID, PTU_STOW)
        return resp.status

    def get_pan_tilt(self, how):
        resp = self.ac.cmd_resp(self.ID, PTU_GET_JOINTS, how)
        pan = resp.val1 * 1.0 / ANG_SCALE
        tilt = resp.val2 * 1.0 / ANG_SCALE
        return resp.status, pan, tilt

class ArmSubsys(SubSystem):

    def __init__(self, connection=None):
        super(ArmSubsys, self).__init__(SUBSYS_ARM, connection)

    #================ Arm control ===============

    def set_joints(self, base, shoulder, elbow):
        ibase = int(base * 1.0 * ANG_SCALE)
        ishoulder = int(shoulder * 1.0 * ANG_SCALE)
        ielbow = int(elbow * 1.0 * ANG_SCALE)
        resp = self.ac.cmd_resp(self.ID, ARM_SET_ALL_JOINTS,
            ibase, ishoulder, ielbow)
        return resp.status

    def set_joint(self, joint, angle):
        iang = int(angle * 1.0 * ANG_SCALE)
        resp = self.ac.cmd_resp(self.ID, ARM_SET_ONE_JOINT, joint, iang)
        return resp.status

    def set_base(self, angle):
        return self.set_joint(ARM_BASE, angle)

    def set_shoulder(self, angle):
        return self.set_joint(ARM_SHOULDER, angle)

    def set_elbow(self, angle):
        return self.set_joint(ARM_ELBOW, angle)

    def stow(self):
        resp = self.ac.cmd_resp(self.ID, ARM_STOW)
        return resp.status

    def get_joints(self, how):
        resp = self.ac.cmd_resp(self.ID, ARM_GET_JOINTS, how)
        base = resp.val1 * 1.0 / ANG_SCALE
        shoulder = resp.val2 * 1.0 / ANG_SCALE
        elbow = resp.val3 * 1.0 / ANG_SCALE
        return resp.status, base, shoulder, elbow

class AeroCamSubsys(SubSystem):

    def __init__(self, connection=None):
        super(AeroCamSubsys, self).__init__(SUBSYS_AEROCAM, connection)
        self.config = None
        self.cameras = []

    #=========== Camera control ==========

    def get_image(self, camera_id, image_format, image_frame, flags=0):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_IMAGE, camera_id, image_format, flags)
        status = resp.status
        if status:
            return status
        image_frame.width = resp.val1
        image_frame.height = resp.val2
        image_frame.depth = resp.val3
        image_frame.image_bytes = resp.val4
        image_frame.image = resp.data
        image_frame.format = image_format
        return 0

    def get_image_mono(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO8, image_frame, flags=flags)

    def get_image_mono8(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO8, image_frame, flags=flags)

    def get_image_mono16(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO16, image_frame, flags=flags)

    def get_image_mono12p(self, camera_id, image_frame, flags=0):
        return self.get_image(camera_id, IMAGE_FORMAT_MONO12P, image_frame, flags=flags)

    def set_feature(self, camera_id, feature, feature_val, feature_val2=0):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_SET_FEATURE_VALUE,
            camera_id, feature, feature_val, feature_val2)
        status = resp.status
        return status

    def set_abs_feature(self, camera_id, feature, feature_aval):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_SET_FEATURE_ABS_VALUE,
            camera_id, feature, float_as_int(feature_aval))
        status = resp.status
        return status

    def get_feature(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_FEATURE_VALUE,
            camera_id, feature)
        return resp.status, resp.val1

    def get_feature2(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_FEATURE_VALUE,
            camera_id, feature)
        return resp.status, resp.val1, resp.val2

    def get_abs_feature(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_FEATURE_ABS_VALUE,
            camera_id, feature)
        return resp.status, int_as_float(resp.val1)

    def set_feature_mode(self, camera_id, feature, mode):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_SET_FEATURE_MODE,
            camera_id, feature, mode)
        return resp.status

    def get_feature_mode(self, camera_id, feature):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_FEATURE_MODE,
            camera_id, feature)
        return resp.status, resp.val1

    def set_image_format(self, camera_id, image_format):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_SET_IMAGE_FORMAT,
            camera_id, image_format)
        return resp.status

    def get_image_format(self, camera_id):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_IMAGE_FORMAT,
            camera_id)
        return resp.status, resp.val1

    def get_image_metadata(self, camera_id, _pattern = '<' + ('i' * METADATA_NUM_VALUES)):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_IMAGE_METADATA, camera_id)
        if resp.status:
            return resp.status, 0, ()
        metadata = unpack(_pattern, resp.data)
        return resp.status, resp.val2, metadata

    def discard_frames(self, camera_id, nframes, discard_mode):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_DISCARD_FRAMES, camera_id, nframes,
            discard_mode)
        return resp.status, resp.val1, resp.val2

    #================= Filter wheel control ================

    def set_filter(self, camera_id, filter_no):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_SET_FILTER,
            camera_id, filter_no)
        return resp.status

    def get_filter(self, camera_id):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_FILTER, camera_id)
        return resp.status, resp.val1

    def get_filter_info(self, camera_id):
        resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_FILTER, camera_id)
        # return filter no, central wavelength, bandwidth in nm, filter set id num
        return resp.status, resp.val1, resp.val2, resp.val3, resp.val4

    #============ Misc.configuration info ===========

    def get_aerocam_config(self):
        if self.config is None:
            resp = self.ac.cmd_resp(self.ID, AEROCAM_GET_CONFIG)
            if resp.status:
                raise AgentException("Cannot get AeroCam configuration")
            self.config = {}
            lines = resp.data.decode('ascii', errors='replace')
            for line in lines.split('\n'):
                if line.strip():
                    v = line.split('\t')
                    self.config[int(v[0])] = v
        return self.config

    def setup_cameras(self, set_exposure=False):
        for cam in self.cameras:
            cam.setup_info()
            if set_exposure:
                if cam.info.name == "LWAC" or cam.info.name == "RWAC":
                    cam.shutter_mode = FEATURE_MODE_MANUAL
                    cam.shutter = 0.1
                    cam.gain_mode = FEATURE_MODE_MANUAL
                    cam.gain = 400

    def get_config(self, camera_id):
        if self.config is None:
            self.get_aerocam_config()
        if camera_id in self.config:
            return self.config[camera_id]
        else:
            return None

class AerobotSubsys(SubSystem):

    def __init__(self, connection=None):
        super(AerobotSubsys, self).__init__(SUBSYS_AEROBOT, connection)

    #=========== IMU control ============

    def get_orientation(self):
        resp = self.ac.cmd_resp(self.ID, AEROBOT_GET_ORIENTATION)
        roll = resp.val1 * 1.0 / ANG_SCALE_FINE
        pitch = resp.val2 * 1.0 / ANG_SCALE_FINE
        yaw = resp.val3 * 1.0 / ANG_SCALE_FINE
        return resp.status, roll, pitch, yaw


    def reset_imu(self):
        resp = self.ac.cmd_resp(self.ID, AEROBOT_RESET_IMU)
        return resp.status

    #========== GPS control ==============

    def get_position(self):
        resp = self.ac.cmd_resp(self.ID, AEROBOT_GET_POSITION)
        lat = resp.val1 * 1.0 / ANG_SCALE_FINE
        lon = resp.val2 * 1.0 / ANG_SCALE_FINE
        alt = resp.val3 * 1.0 / DIST_SCALE
        fmode = resp.val4
        return resp.status, lat, lon, alt, fmode


# Test code

if __name__ == '__main__':
    print("create agent connection...")
    ac = AgentConnection()
    print("create system subsystem...")
    ss = SystemSubsys(ac)
#    print "create pancam subsystem..."
#    pc = PanCamSubsys(ac)
#    print "create mast subsystem..."
#    mast = MastSubsys(ac)
#    print "create arm subsystem..."
#    arm = ArmSubsys(ac)
#    print "create aerocam subsystem..."
#    aerocam = AeroCamSubsys(ac)
#    print "create aerobot subsystem..."
#    aerobot = AerobotSubsys(ac)
    print("system connect")
    version = ss.connect()  # NB: version is a tuple!
    print("protocol version = %d.%d" % version)
    ss.disconnect()
    print("disconnected")
