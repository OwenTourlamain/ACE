#!/usr/bin/python
# -* encoding: utf-8 *-

# FAUPE (Faux-AUPE :-) -- Fake AUPE server

import sys
import socket
import signal
import time

from struct import Struct, pack, unpack
from collections import namedtuple

from PIL import Image

# Make life easy....

#LGT_PYTHON_DIR = "/home/lgt/bin/python"
#sys.path.append(LGT_PYTHON_DIR)

from au.protocol import *

DEFAULT_AGENT_HOST = '127.0.0.1'
DEFAULT_AGENT_PORT = '8888'
DEFAULT_AGENT_ADDR = DEFAULT_AGENT_HOST + ':' + DEFAULT_AGENT_PORT

CmdPkt = namedtuple('CmdPkt',('subsys','cmd','arg1','arg2','arg3','arg4',
    'data_bytes', 'data'))
RespPkt = namedtuple('RespPkt', ('subsys', 'status', 'val1', 'val2', 'val3', 'val4',
    'data_bytes', 'data'))

_pkt_struct = Struct('I H H iiii i I')
_meta_struct = Struct('<' + ('i' * METADATA_NUM_VALUES))

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

# Subsystem command handler return codes
(   RESP_DONE,      # Command fully handled
    RESP_OK,        # Need STATUS_OK return to client
    RESP_NOTIMP,    # Need STATUS_NOTIMP return to client
    RESP_CMDERR,    # Client command error - status returned
    RESP_CLICLOSE,  # Client disconnect request - return STATUS_OK & close client
    RESP_CLIQUIT,   # Client connection error - close client
    RESP_SRVCLOSE,  # Close down server (no error)
    RESP_SRVQUIT    # Bad error - close down server
    ) = range(8)

OKAY_NO_DATA = (RESP_DONE, STATUS_OK, 0, 0, 0, 0, None)
BAD_PARAM = (RESP_CMDERR, STATUS_BADPARAM, 0, 0, 0, 0, None)

#####################################

class SubSystem(object):
    """A generic subsystem"""
    def __init__(self, ssid=SUBSYS_NONE, name="NULL", desc="Null subsystem"):
        self.ssid = ssid
        self.name = name
        self.desc = desc
        self.initialised = False

    def init(self):
        """Start up the subsystem"""
        self.initialised = True

    def announce(self):
        print "=== Subsystem %s ID %d (%s)" % (self.name, self.ssid, self.desc)

    def close(self):
        """Shut down the subsystem"""
        self.initialised = False

    def handle(self, cmd_pkt):
        """Handle a command packet"""
        return OKAY_NO_DATA

#####################################

class System(SubSystem):
    """Fake System subsystem"""
    def __init__(self, ssid):
        super(System, self).__init__(ssid=ssid, name="SYSTEM", desc="FAKE System")

    def init(self):
        self.announce()
        self.initialised = True

    def close(self):
        print "--- Subsystem %s ID %d closing down" % (self.name, self.ssid)
        self.initialised = False

    def handle(self, cmd_pkt):
        cmd = cmd_pkt.cmd
        if cmd == SYSTEM_CONNECT or cmd == SYSTEM_GET_VERSION:
            return (RESP_DONE, STATUS_OK, PROTOCOL_VERSION, PROTOCOL_MINOR, 0, 0, None)
        if cmd == SYSTEM_DISCONNECT:
            return (RESP_CLICLOSE, STATUS_OK, 0, 0, 0, 0, None)
        if cmd == SYSTEM_SHUTDOWN:
            return (RESP_SRVCLOSE, STATUS_OK, 0, 0, 0, 0, None)
        return (RESP_NOTIMP, STATUS_OK, 0, 0, 0, 0, None)


#####################################

class Filter(object):
    def __init__(self, name="", desc="", centre=0, width=0):
        self.name = name
        self.desc = desc
        self.centre = centre
        self.width = width

class FilterWheel(object):
    def __init__(self, name="", desc="", fwid="", fwid_num=0, no_filter_ix=0, filters=None):
        self.name = name
        self.desc = desc
        self.fwid = fwid
        self.fwid_num = fwid_num
        self.no_filter_ix = no_filter_ix
        if filters:
            self.filters = filters
            self.num_filters = len(filters)
        else:
            self.filters = []
            self.num_filters = 0

#####################################

LWAC_filters = [
    Filter("NULL",  "No filter",    0,      0),
    Filter("BLUE",  "Blue colour",  448,    124),
    Filter("GREEN", "Green colour", 536,    81),
    Filter("RED",   "Red colour",   637,    103),
    Filter("GEOL1", "Geology 1",    438,    24 ),
    Filter("GEOL2", "Geology 2",    500,    24),
    Filter("GEOL3", "Geology 3",    532,    10),
    Filter("GEOL4", "Geology 4",    568,    10 ),
    Filter("GEOL5", "Geology 5",    610,    10 ),
    Filter("GEOL6", "Geology 6",    671,    10),
    Filter("VIS",   "Visible",      545,    295),
    Filter("EMPTY", "Empty",        700,    600) ]

RWAC_filters = [
    Filter("NULL",  "No filter",    0,  0),
    Filter("BLUE",  "Blue colour",  448,    124),
    Filter("GREEN", "Green colour", 536,    81),
    Filter("RED",   "Red colour",   637,    103),
    Filter("GEOL7", "Geology 7",    740,    13),
    Filter("GEOL8", "Geology 8",    780,    10 ),
    Filter("GEOL9", "Geology 9",    832,    37 ),
    Filter("GEOL10",    "Geology 10",   900,    50),
    Filter("GEOL11",    "Geology 11",   950,    50),
    Filter("GEOL12",    "Geology 12",   1000,   50 ),
    Filter("VIS",   "Visible",  545,    295),
    Filter("EMPTY", "Empty",    700,    600) ]

LWAC_filter_wheel = FilterWheel(name="FERRIC-L",
                                desc="FERRIC left filter wheel",
                                fwid="AFW03",
                                fwid_num=3,
                                no_filter_ix=10,
                                filters=LWAC_filters)

RWAC_filter_wheel = FilterWheel(name="FERRIC-R",
                                desc="FERRIC right filter wheel",
                                fwid="AFW04",
                                fwid_num=4,
                                no_filter_ix=10,
                                filters=RWAC_filters)

#####################################

camera_features_list = [
    CAM_FEATURE_BRIGHTNESS,
    CAM_FEATURE_EXPOSURE,
    CAM_FEATURE_HUE,
    CAM_FEATURE_SATURATION,
    CAM_FEATURE_GAMMA,
    CAM_FEATURE_SHUTTER,
    CAM_FEATURE_GAIN,
    CAM_FEATURE_IRIS,
    CAM_FEATURE_FOCUS,
    CAM_FEATURE_FRAMERATE,
    CAM_FEATURE_ZOOM,
    CAM_FEATURE_WHITEBALANCE,
    CAM_FEATURE_AE_ALG,
    CAM_FEATURE_AE_TOL,
    CAM_FEATURE_AE_MAX,
    CAM_FEATURE_AE_MIN,
    CAM_FEATURE_AE_OUTLIERS,
    CAM_FEATURE_AE_RATE ]

camera_xfeatures_list = [
    CAM_XF_AE_ALG,
    CAM_XF_AE_TARGET,
    CAM_XF_AE_TOL,
    CAM_XF_AE_MAX,
    CAM_XF_AE_MIN,
    CAM_XF_AE_OUTLIERS,
    CAM_XF_AE_RATE,
    CAM_XF_AE_MAXFRAMES,
    CAM_XF_AE_REGION,
    CAM_XF_ROI_X,
    CAM_XF_ROI_Y,
    CAM_XF_ROI_WIDTH,
    CAM_XF_ROI_HEIGHT,
    CAM_XF_EXP_DELAY ]

camera_modes_list = [
    CAM_FEATURE_BRIGHTNESS,
    CAM_FEATURE_EXPOSURE,
    CAM_FEATURE_HUE,
    CAM_FEATURE_SATURATION,
    CAM_FEATURE_GAMMA,
    CAM_FEATURE_SHUTTER,
    CAM_FEATURE_GAIN,
    CAM_FEATURE_IRIS,
    CAM_FEATURE_FOCUS,
    CAM_FEATURE_FRAMERATE,
    CAM_FEATURE_ZOOM,
    CAM_FEATURE_WHITEBALANCE ]

camera_fmult = {
    CAM_FEATURE_BRIGHTNESS: 1.0,
    CAM_FEATURE_EXPOSURE:   100.0,
    CAM_FEATURE_HUE:        1.0,
    CAM_FEATURE_SATURATION: 1.0,
    CAM_FEATURE_GAMMA:      1.0,
    CAM_FEATURE_SHUTTER:    1000000.0,
    CAM_FEATURE_GAIN:       1.0,
    CAM_FEATURE_IRIS:       1.0,
    CAM_FEATURE_FOCUS:      1.0,
    CAM_FEATURE_FRAMERATE:  1.0,
    CAM_FEATURE_ZOOM:       1.0,
    CAM_FEATURE_WHITEBALANCE:   1.0,
    CAM_FEATURE_AE_ALG:     1.0,
    CAM_FEATURE_AE_TOL:     100.0,
    CAM_FEATURE_AE_MAX:     1000000.0,
    CAM_FEATURE_AE_MIN:     1000000.0,
    CAM_FEATURE_AE_OUTLIERS:    10000.0,
    CAM_FEATURE_AE_RATE:    100.0,
    CAM_XF_AE_ALG:          1.0,
    CAM_XF_AE_TARGET:       10000.0,
    CAM_XF_AE_TOL:          10000.0,
    CAM_XF_AE_MAX:          1000000.0,
    CAM_XF_AE_MIN:          1000000.0,
    CAM_XF_AE_OUTLIERS:     10000.0,
    CAM_XF_AE_RATE:         10000.0,
    CAM_XF_AE_MAXFRAMES:    1.0,
    CAM_XF_AE_REGION:       1.0,
    CAM_XF_ROI_X:           1.0,
    CAM_XF_ROI_Y:           1.0,
    CAM_XF_ROI_WIDTH:       1.0,
    CAM_XF_ROI_HEIGHT:      1.0,
    CAM_XF_EXP_DELAY:       1000000.0 }

# In-camera features

camera_features_default = {
    CAM_FEATURE_BRIGHTNESS: 1,
    CAM_FEATURE_EXPOSURE:   40,
    CAM_FEATURE_HUE:        1,
    CAM_FEATURE_SATURATION: 1,
    CAM_FEATURE_GAMMA:      1,
    CAM_FEATURE_SHUTTER:    10000,  # 1/100 s
    CAM_FEATURE_GAIN:       0,
    CAM_FEATURE_IRIS:       0,
    CAM_FEATURE_FOCUS:      0,
    CAM_FEATURE_FRAMERATE:  2.0,
    CAM_FEATURE_ZOOM:       1,
    CAM_FEATURE_WHITEBALANCE:   1,
    CAM_FEATURE_AE_ALG:     0,      # MEAN
    CAM_FEATURE_AE_TOL:     3,      # 3%
    CAM_FEATURE_AE_MAX:     30000000,   # 30s
    CAM_FEATURE_AE_MIN:     40,     # 40us
    CAM_FEATURE_AE_OUTLIERS:    500,    # 5%
    CAM_FEATURE_AE_RATE:    100 }   # 100%

# Server-supplied extra features

camera_xfeatures_default = {
    CAM_XF_AE_ALG:          0,      # AE_ALG_MEAN
    CAM_XF_AE_TARGET:       4000,   # 40%
    CAM_XF_AE_TOL:          250,    # 2.5%
    CAM_XF_AE_MAX:          30000000,   # 30s
    CAM_XF_AE_MIN:          40,     # 40us
    CAM_XF_AE_OUTLIERS:     500,    # 5%
    CAM_XF_AE_RATE:         10000,  # 100%
    CAM_XF_AE_MAXFRAMES:    16,
    CAM_XF_AE_REGION:       0,      # AE_REGION_FULL
    CAM_XF_ROI_X:           0,
    CAM_XF_ROI_Y:           0,
    CAM_XF_ROI_WIDTH:       0,      # Full width
    CAM_XF_ROI_HEIGHT:      0,      # Full height
    CAM_XF_EXP_DELAY:       120000 } # 0.12 s delay (in stream mode)

#####################################
#####################################
#####################################

class Camera(object):
    """A fake camera"""
    def __init__(self,
                 cam_id=0, name="NONAME", desc="No description", cam_class="NOCLASS",
                 uname="NOUNAME", driver="ND", model="NOMODEL", addr="NOADDR", guid="NOGUID",
                 sensmode="NOSMODE", fw=None):
        self.cam_id = cam_id
        self.name = name
        self.desc = desc
        self.cam_class = cam_class
        self.uname = uname
        self.driver = driver
        self.model = model
        self.addr = addr
        self.guid = guid
        self.sensmode = sensmode
        self.fw = fw
        self.reset()

    def reset(self):
        self.ifeat = camera_features_default.copy()
        self.feat = { f: v/camera_fmult[f] for f,v in self.ifeat.iteritems() }
        self.ixfeat = camera_xfeatures_default.copy()
        self.xfeat = { f: v/camera_fmult[f] for f,v in self.ixfeat.iteritems() }
        self.fmode = { f: FEATURE_MODE_MANUAL for f in camera_modes_list }    # All set to manual
        if self.fw:
            self.filter = self.fw.no_filter_ix
        else:
            self.filter = 0
        self.im_width = 1024
        self.im_height = 1024
        self.im_data = ''
        self.im_format = IMAGE_FORMAT_MONO8
        self.meta = [ 0 ] * METADATA_NUM_VALUES
        self.meta_flags = 0

    def load_image(self, imfile=None):
        dfn = "FAKE_%s_%s.png" % (self.name, self.sensmode)
        ifn = imfile or dfn
        im = Image.open(ifn).convert('L')
        self.im_data = im.tostring()
        self.im_bytes = len(self.im_data)
        self.im_width, self.im_height = im.size

    def get_image(image_flags=0, image_format=IMAGE_FORMAT_MONO8):
        pass

    def save_metadata(self, flags=META_SAVE_ALL, timestamp=None):
        if not timestamp:
            timestamp = time.time()
        self.meta[METADATA_TIMESTAMP_SEC] = int(timestamp)
        self.meta[METADATA_TIMESTAMP_NANO] = int((timestamp - int(timestamp)) * 1000000000)
        self.meta[METADATA_CAMERA_ID] = self.cam_id
        self.meta[METADATA_SHUTTER] = self.ifeat[CAM_FEATURE_SHUTTER]
        self.meta[METADATA_GAIN] = self.ifeat[CAM_FEATURE_GAIN]
        self.meta[METADATA_FILTER] = self.filter
        self.meta_flags = flags


#####################################


class PanCam(SubSystem):
    """Fake PanCam subsystem providing fixed images"""
    def __init__(self, ssid):
        super(PanCam, self).__init__(ssid=ssid, name="PANCAM", desc="FAKE PanCam")

    def init(self):
        self.announce()
        self.cam_func = {
            CAM_GET_IMAGE:          self.cam_get_image,
            CAM_SET_FEATURE_VALUE:  self.cam_set_feature_value,
            CAM_GET_FEATURE_VALUE:  self.cam_set_feature_value,
            CAM_SET_FEATURE_MODE:   self.cam_set_feature_mode,
            CAM_GET_FEATURE_MODE:   self.cam_get_feature_mode,
            CAM_SET_IMAGE_FORMAT:   self.cam_set_image_format,
            CAM_GET_IMAGE_FORMAT:   self.cam_get_image_format,
            CAM_SET_FILTER:         self.cam_set_filter,
            CAM_GET_FILTER:         self.cam_get_filter,
            CAM_STOW_FILTERS:       self.cam_stow_filters,
            CAM_SET_FEATURE_ABS_VALUE:  self.cam_set_feature_abs_value,
            CAM_GET_FEATURE_ABS_VALUE:  self.cam_get_feature_abs_value,
            CAM_GET_PANCAM_CONFIG:  self.cam_get_pancam_config,
            CAM_GET_IMAGE_METADATA: self.cam_get_image_metadata,
            CAM_DISCARD_FRAMES:     self.cam_discard_frames,
            CAM_GET_LAST_IMAGE:     self.cam_get_last_image }
        self.cameras = []
        self.cam_by_id = [ None ] * PANCAM_NUM_CAMS
        self.cam_by_name = {}
        slaves = [ [] ] * PANCAM_NUM_CAMS
        with open('pancam_hw.dat', 'r') as f:
            for l in f:
                (cam_id, master_id, name, cam_class, uname, driver, model,
                    addr, guid, sensmode, framerate, desc) = l.rstrip().split('\t')
                if desc.startswith('"'):
                    desc = desc[1:-1]
                cam_id = int(cam_id)
                master_id = int(master_id)
                if master_id >= 0:
                    slaves[master_id].append(cam_id)
                if cam_id == CAMERA_WACL and name == "LWAC":
                    fw = LWAC_filter_wheel
                elif cam_id == CAMERA_WACR and name == "RWAC":
                    fw = RWAC_filter_wheel
                else:
                    fw = None
                cam = Camera(cam_id=cam_id, name=name, desc=desc, cam_class=cam_class, uname=uname,
                             driver=driver, model=model, addr=addr, guid=guid, sensmode=sensmode, fw=fw)
                self.cameras.append(cam)
                self.cam_by_id[cam_id] = cam
                self.cam_by_name[name] = cam
        for cam in self.cameras:
            cam.slaves = tuple(self.cam_by_id[cid] for cid in slaves[cam.cam_id])
        for cam in self.cameras:
            print ">> Initialising %s (%s)" % (cam.name, cam.desc)
            cam.load_image()
        self.initialised = True

    def close(self):
        print "--- Subsystem %s ID %d closing down" % (self.name, self.ssid)
        self.initialised = False

    def cam_get_image(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg3 & IMAGE_PREVIOUS:
            return (RESP_DONE, STATUS_OK, cam.im_width, cam.im_height, 1, cam.im_bytes, cam.im_data)
        if arg2 != IMAGE_FORMAT_MONO8:
            return BAD_PARAM
        ts = time.time()
        cam.get_image()
        if arg3 & IMAGE_SYNC:
            for slave in cam.slaves:    # Possibly empty...
                slave.get_image()
        if arg3 & META_SAVE_CAM:
            cam.save_metadata(flags=META_SAVE_CAM, timestamp=ts)
            if arg3 & IMAGE_SYNC:
                for slave in cam.slaves:    # Possibly empty...
                    slave.save_metadata(flags=META_SAVE_CAM, timestamp=ts)
        return (RESP_DONE, STATUS_OK, cam.im_width, cam.im_height, 1, cam.im_bytes, cam.im_data)

    def cam_set_feature_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 in cam.ixfeat:
            return self.cam_set_ext_feature_value(cmd, arg1, arg2, arg3, arg4, data)
        if arg2 not in cam.ifeat:
            return BAD_PARAM
        cam.ifeat[arg2] = int(arg3)
        cam.feat[arg2] = float(arg3) / camera_fmult[arg2]
        return OKAY_NO_DATA

    def cam_get_feature_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 in cam.ixfeat:
            return self.cam_get_ext_feature_value(cmd, arg1, arg2, arg3, arg4, data)
        if arg2 not in cam.ifeat:
            return BAD_PARAM
        return (RESP_DONE, STATUS_OK, cam.ifeat[arg2])

    def cam_set_ext_feature_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 not in cam.ixfeat:
            return BAD_PARAM
        cam.ixfeat[arg2] = int(arg3)
        cam.xfeat[arg2] = float(arg3) / camera_fmult[arg2]
        return OKAY_NO_DATA

    def cam_get_ext_feature_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 not in cam.ixfeat:
            return BAD_PARAM
        return (RESP_DONE, STATUS_OK, cam.ixfeat[arg2])

    def cam_set_feature_mode(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 not in cam.fmode:
            return BAD_PARAM
        cam.fmode[arg2] = int(arg3)
        return OKAY_NO_DATA

    def cam_get_feature_mode(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 not in cam.fmode:
            return BAD_PARAM
        return (RESP_DONE, STATUS_OK, cam.fmode[arg2])

    def cam_set_image_format(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 != IMAGE_FORMAT_MONO8:
            return BAD_PARAM
        cam.im_format = arg2

    def cam_get_image_format(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        return (RESP_DONE, STATUS_OK, cam.im_format)

    def cam_set_filter(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if cam.fw:
            if arg2:
                cam.filter = arg2
            else:
                cam.filter = cam.fw.no_filter_ix
        return OKAY_NO_DATA

    def cam_get_filter(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if cam.fw:
            f = cam.fw.filters[cam.filter]
            return (RESP_DONE, STATUS_OK, cam.filter, f.centre, f.width, cam.fw.fwid_num)
        else:
            return (RESP_DONE, STATUS_OK, cam.filter)

    def cam_stow_filters(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if cam.fw:
            cam.filter = cam.fw.no_filter_ix
        return OKAY_NO_DATA

    def cam_set_feature_abs_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 in cam.xfeat:
            return self.cam_set_ext_feature_abs_value(cmd, arg1, arg2, arg3, arg4, data)
        if arg2 not in cam.feat:
            return BAD_PARAM
        v = int_as_float(arg3)
        cam.feat[arg2] = v
        cam.ifeat[arg2] = int(v * camera_fmult[arg2] + 0.5)
        return OKAY_NO_DATA

    def cam_get_feature_abs_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 in cam.xfeat:
            return self.cam_get_ext_feature_abs_value(cmd, arg1, arg2, arg3, arg4, data)
        if arg2 not in cam.feat:
            return BAD_PARAM
        return (RESP_DONE, STATUS_OK, float_as_int(cam.feat[arg2]))

    def cam_set_ext_feature_abs_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 not in cam.xfeat:
            return BAD_PARAM
        v = int_as_float(arg3)
        cam.xfeat[arg2] = v
        cam.ixfeat[arg2] = int(v * camera_fmult[arg2] + 0.5)
        return OKAY_NO_DATA

    def cam_get_ext_feature_abs_value(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        if arg2 not in cam.xfeat:
            return BAD_PARAM
        return (RESP_DONE, STATUS_OK, float_as_int(cam.xfeat[arg2]))

    def cam_get_pancam_config(self, cmd, arg1, arg2, arg3, arg4, data):
        config = ""
        for cam in self.cameras:
            if cam.fw:
                fw_id = cam.fw.fwid
            else:
                fw_id = "NONE"
            l = "%d\t%s\t%s\t%s\t%s\t%s\t%s\t\"%s\"\t%s\n" % (cam.cam_id,
                    cam.name, cam.cam_class, cam.uname, cam.driver,
                    cam.model, cam.guid, cam.desc, fw_id)
            config += l
        return (RESP_DONE, STATUS_OK, len(self.cameras), 0, 0, 0, config)

    def cam_get_image_metadata(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        metadata = _meta_struct.pack(*cam.meta)
        return (RESP_DONE, STATUS_OK, METADATA_NUM_VALUES, cam.meta_flags, 0, 0, metadata)

    def cam_discard_frames(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        return (RESP_DONE, STATUS_OK, arg2, arg3)

    def cam_get_last_image(self, cmd, arg1, arg2, arg3, arg4, data):
        cam = self.cam_by_id[arg1]
        return (RESP_DONE, STATUS_OK, cam.im_width, cam.im_height, 8, cam.im_bytes, cam.im_data)

    def handle(self, cmd_pkt):
        cmd = cmd_pkt.cmd
        func = self.cam_func[cmd]
        resp = func(cmd, cmd_pkt.arg1, cmd_pkt.arg2, cmd_pkt.arg3, cmd_pkt.arg4, cmd_pkt.data)
        if resp:
            return resp
        else:
            return OKAY_NO_DATA

#####################################

class Mast(SubSystem):
    """Fake PTU control"""
    def __init__(self, ssid):
        super(Mast, self).__init__(ssid=ssid, name="MAST", desc="FAKE Mast")

    def init(self):
        self.announce()
        self.pan = 0.0
        self.tilt = 0.0
        self.initialised = True

    def close(self):
        print "--- Subsystem %s ID %d closing down" % (self.name, self.ssid)
        self.initialised = False

    def handle(self, cmd_pkt):
        cmd = cmd_pkt.cmd
        arg1 = cmd_pkt.arg1
        arg2 = cmd_pkt.arg2
        if cmd == PTU_SET_ALL_JOINTS:
            self.pan = float(arg1)/ANG_SCALE
            self.tilt = float(arg2)/ANG_SCALE
            return OKAY_NO_DATA
        elif cmd == PTU_SET_ONE_JOINT:
            if arg1 < 0 or arg1 >= PTU_NUM_JOINTS:
                return BAD_PARAM
            if arg1 == PTU_PAN:
                self.pan = float(arg2)/ANG_SCALE
                return OKAY_NO_DATA
            elif arg1 == PTU_TILT:
                self.tilt = float(arg2)/ANG_SCALE
                return OKAY_NO_DATA
        elif cmd == PTU_STOW:
            self.pan = 0.0
            self.tilt = 0.0
            return OKAY_NO_DATA
        elif cmd == PTU_GET_JOINTS:
            return (RESP_DONE, STATUS_OK, int(self.pan * ANG_SCALE), int(self.tilt * ANG_SCALE))
        return OKAY_NO_DATA

#####################################

ss_lookup = {}
ss_numcmds = {}
running = False
interrupted = False
oldsig = None

def signal_handler(signum, frame):
    global running, interrupted
    interrupted = True
    running = False
    signal.signal(signal.SIGINT, oldsig)

class Server(object):
    """Fake AUPE main server"""
    def __init__(self, addr=('127.0.0.1', 8888)):
        try:
            self.recv_flags = socket.MSG_WAITALL
        except AttributeError:
            self.recv_flags = 0
        self.ms = None
        self.ms_addr = addr
        self.cs = None
        self.cs_addr = ('', 0)

    def get_cmd(self, socket):
        pkt_bytes = socket.recv(PKT_LEN, self.recv_flags)
        while len(pkt_bytes) < PKT_LEN:
            fragment = socket.recv(PKT_LEN - len(pkt_bytes), self.recv_flags)
            if fragment == '':
                raise RuntimeError("socket connection broken")
            pkt_bytes += fragment
        (ident, subsys, cmd, arg1, arg2, arg3, arg4,
            reserved, data_bytes) = _pkt_struct.unpack(pkt_bytes)
        if data_bytes > 0:
            data = socket.recv(data_bytes, self.recv_flags)
            while len(data) < data_bytes:
                fragment = self.socket.recv(data_bytes - len(data), self.recv_flags)
                if fragment == '':
                    raise RuntimeError("socket connection broken")
                data += fragment
        else:
            data = ''
        cmd_pkt = CmdPkt(subsys, cmd, arg1, arg2, arg3, arg4, data_bytes, data)
        return cmd_pkt

    def send_resp(self, socket, subsys, status, val1=0, val2=0, val3=0, val4=0, data=None):
        data_bytes = len(data) if data else 0
        pkt_bytes = _pkt_struct.pack(IDENT, subsys, status, val1, val2, val3, val4, 0, data_bytes)
        socket.sendall(pkt_bytes)
        if data:
            socket.sendall(data)

    def run(self):
        global running, interrupted, oldsig
        self.ms = socket.socket()
        self.ms.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ms.bind(self.ms_addr)
        self.ms.listen(1)
        running = True
        print "Listening on %s:%d" % self.ms_addr
        oldsig = signal.signal(signal.SIGINT, signal_handler)
        while (running):
            try:
                self.cs, self.cs_addr = self.ms.accept()
            except socket.error as err:
                if err.args[0] == 4:
                    break
                raise
                break
            print "+++ Accepted connection from %s:%d" % self.cs_addr
            client_connected = True
            while running and client_connected:
                cmd_pkt = self.get_cmd(self.cs)
                ss_id = cmd_pkt.subsys
                try:
                    ss = ss_lookup[ss_id]
                except KeyError:
                    ss = None
                if not ss:
                    self.send_resp(self.cs, ss_id, STATUS_BADSUBSYS)
                    continue
                cmd = cmd_pkt.cmd
                if cmd >= ss_numcmds[ss_id]:
                    self.send_resp(self.cs, ss_id, STATUS_BADFUNC)
                    continue
                if cmd == COMMAND_NONE:
                    self.send_resp(self.cs, ss_id, STATUS_OK)
                    continue
                acresp = ss.handle(cmd_pkt)
                action, resp = acresp[0], acresp[1:]
                if action == RESP_DONE or action == RESP_OK or action == RESP_NOTIMP or action == RESP_CMDERR:
                    self.send_resp(self.cs, ss_id, *resp)
                elif action == RESP_CLICLOSE:
                    self.send_resp(self.cs, ss_id, STATUS_OK, 0, 0, 0, 0, None)
                    client_connected = False
                    break
                elif action == RESP_CLIQUIT:
                    client_connected = False
                    break
                elif action == RESP_SRVCLOSE:
                    self.send_resp(self.cs, ss_id, STATUS_OK, 0, 0, 0, 0, None)
                    time.sleep(0.5)
                    client_connected = False
                    running = False
                    break
                elif action == RESP_SRVQUIT:
                    print "** internal error - server closing down!"
                    client_connected = False
                    running = False
                    break
            self.cs.shutdown(socket.SHUT_RDWR)
            self.cs.close()
            print "--- closed connection from %s:%d" % self.cs_addr
        print "... server shutting down"
        self.ms.shutdown(socket.SHUT_RDWR)
        self.ms.close()

def main():
    """Fake AUPE server"""

    print "============================"
    print "===== FAKE AUPE SERVER ====="
    print "============================"
    print

    # Set up subsystems

    system_ss = System(SUBSYS_SYSTEM)
    ss_lookup[SUBSYS_SYSTEM] = system_ss
    ss_numcmds[SUBSYS_SYSTEM] = SYSTEM__MAX__CMD
    system_ss.init()

    pancam_ss = PanCam(SUBSYS_PANCAM)
    ss_lookup[SUBSYS_PANCAM] = pancam_ss
    ss_numcmds[SUBSYS_PANCAM] = PANCAM__MAX__CMD
    pancam_ss.init()

    mast_ss = Mast(SUBSYS_MAST)
    ss_lookup[SUBSYS_MAST] = mast_ss
    ss_numcmds[SUBSYS_MAST] = MAST__MAX__CMD
    mast_ss.init()

    print

    server = Server()
    server.run()

    print

    mast_ss.close()
    pancam_ss.close()
    system_ss.close()


#####################################

if __name__ == "__main__":
    main()
