#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
from PIL import Image, PngImagePlugin
from . import rover_agent_api as api

class PanCamException(api.AgentException):
    pass

class CamIntFeature(object):
    def __init__(self, fcode):
        self._fcode = fcode
    def __get__(self, obj, cls=None):
        ret, val = obj.pc.get_feature(obj.cam_id, self._fcode)
        if ret:
            raise PanCamException("GET error %d for fcode %d" % (ret, self._fcode))
        return val
    def __set__(self, obj, val):
        ret = obj.pc.set_feature(obj.cam_id, self._fcode, val)
        if ret:
            raise PanCamException("SET error %d for fcode %d value %d" % (ret, self._fcode, val))

class CamIntFeature2(object):
    def __init__(self, fcode):
        self._fcode = fcode
    def __get__(self, obj, cls=None):
        ret, val1, val2 = obj.pc.get_feature2(obj.cam_id, self._fcode)
        if ret:
            raise PanCamException("GET error %d for fcode %d" % (ret, self._fcode))
        return val1, val2
    def __set__(self, obj, val):
        # NB: val is a 2-tuple!
        ret = obj.pc.set_feature(obj.cam_id, self._fcode, *val)
        if ret:
            raise PanCamException("SET error %d for fcode %d value %d" % (ret, self._fcode, val))

class CamFloatFeature(object):
    def __init__(self, fcode):
        self._fcode = fcode
    def __get__(self, obj, cls=None):
        ret, val = obj.pc.get_abs_feature(obj.cam_id, self._fcode)
        if ret:
            raise PanCamException("GET error %d for fcode %d" % (ret, self._fcode))
        return val
    def __set__(self, obj, val):
        ret = obj.pc.set_abs_feature(obj.cam_id, self._fcode, val)
        if ret:
            raise PanCamException("SET error %d for fcode %d value %f" % (ret, self._fcode, val))

class CamFeatureMode(object):
    def __init__(self, fcode):
        self._fcode = fcode
    def __get__(self, obj, cls=None):
        ret, val = obj.pc.get_feature_mode(obj.cam_id, self._fcode)
        if ret:
            raise PanCamException("GET MODE error %d for fcode %d" % (ret, self._fcode))
        return val
    def __set__(self, obj, val):
        ret = obj.pc.set_feature_mode(obj.cam_id, self._fcode, val)
        if ret:
            raise PanCamException("SET MODE error %d for fcode %d value %d" %(ret, self._fcode, val))

class FilterSelector(object):
    def __get__(self, obj, cls=None):
        ret, val = obj.pc.get_filter(obj.cam_id)
        if ret:
            raise PanCamException("GET FILTER error %d for camera id %d" % (ret, obj.cam_id))
        return val
    def __set__(self, obj, val):
        ret = obj.pc.set_filter(obj.cam_id, val)
        if ret:
            raise PanCamException("SET FILTER error %d for camera id %d filter %d" % (ret, obj.cam_id, val))

class ImageMetadata(object):

    def __init__(self, values=None, flags=0):
        self.flags = flags
        if values:
            self.cam_id     = values[api.METADATA_CAMERA_ID]
            self.timestamp  = float(values[api.METADATA_TIMESTAMP_SEC]) + float(values[api.METADATA_TIMESTAMP_NANO])/1e9
            self.shutter    = float(values[api.METADATA_SHUTTER]) / api.SHUTTER_SCALE
            self.gain       = values[api.METADATA_GAIN]
            self.filter     = values[api.METADATA_FILTER]
            self.whitebal_r = values[api.METADATA_WHITEBAL_R]
            self.whitebal_b = values[api.METADATA_WHITEBAL_B]
            self.focus      = values[api.METADATA_FOCUS]
            self.zoom       = values[api.METADATA_ZOOM]
            self.iris       = values[api.METADATA_IRIS]
            self.roll       = float(values[api.METADATA_ROLL]) / api.ANG_SCALE_FINE
            self.pitch      = float(values[api.METADATA_PITCH]) / api.ANG_SCALE_FINE
            self.yaw        = float(values[api.METADATA_YAW]) / api.ANG_SCALE_FINE
            self.latitude   = float(values[api.METADATA_LATITUDE]) / api.ANG_SCALE_FINE
            self.longitude  = float(values[api.METADATA_LONGITUDE]) / api.ANG_SCALE_FINE
            self.altitude   = float(values[api.METADATA_ALTITUDE]) / api.DIST_SCALE
        else:
            self.cam_id     = 0
            self.shutter    = 0.0
            self.gain       = 0
            self.filter     = 0
            self.whitebal_r = 0
            self.whitebal_b = 0
            self.focus      = 0
            self.zoom       = 0
            self.iris       = 0
            self.roll       = 0.0
            self.pitch      = 0.0
            self.yaw        = 0.0
            self.latitude   = 0.0
            self.longitude  = 0.0
            self.altitude   = 0.0
            

fsnum_to_fsid = [ "NONE", "AFW01", "AFW02", "AFW03", "AFW04", "AFW05" ]

class CameraInfo(object):
    
    def __init__(self, v, fs_num=0):
        self.cam_id = int(v[0])
        self.name = v[1]
        self.cam_class = v[2]
        self.unique_name = v[3]
        self.driver = v[4]
        self.model = v[5]
        self.guid = v[6]
        self.desc = v[7]
        if self.desc.startswith('"'):
            self.desc = self.desc[1:-1]
        self.filter_set_num = fs_num
        if len(v) > 8:
            self.filter_set_id = v[8]
        else:
            self.filter_set_id = fsnum_to_fsid[fs_num]

class PanCamImage(api.ImageFrame):
    
    def __init__(self, camera=None, info=None, **kwargs):
        super(PanCamImage, self).__init__(**kwargs)
        self.camera = camera
        self.info = info
        
    @property
    def size(self):
        return (self.width, self.height)

    def as_pil_image(self):
        if not self.image:
            raise PanCamException("No image data to convert to PIL format")
        if self.format == api.IMAGE_FORMAT_MONO8:
            return Image.frombuffer('L', (self.width, self.height),
                                    self.image, 'raw', 'L', 0, 1)
        elif self.format == api.IMAGE_FORMAT_MONO16:
            return Image.frombuffer('I;16', (self.width, self.height),
                                    self.image, 'raw', 'I;16', 0, 1)
        elif self.format == api.IMAGE_FORMAT_RGB8:
            return Image.frombuffer('RGB', (self.width, self.height),
                                    self.image, 'raw', 'RGB', 0, 1)
        elif self.format == api.IMAGE_FORMAT_BAYER:
            return Image.frombuffer('L', (self.width, self.height),
                                    self.image, 'raw', 'L', 0, 1)
        else:
            raise PanCamException("Cannot convert image format %d to PIL format" % self.format)
    
    def gen_metadata_tags(self):
        md = {}
        inf = self.info
        caminf = self.camera.info
        if inf is not None:
            flags = inf.flags
            if flags & api.META_SAVE_CAM:
                md['timestampUTC'] = datetime.datetime.utcfromtimestamp(inf.timestamp).isoformat()
                md['camNum']    = "%d" % inf.cam_id
                md['exposureTime'] = "%.6f" % inf.shutter
                md['gain']      = "%d" % inf.gain
                if caminf.cam_class == "HRC":
                    md['HRCImage'] = "true"
                    md['focus'] = "%d" % inf.focus
                    md['zoom']  = "%d" % inf.zoom
                    md['iris']  = "%d" % inf.iris
                    md['whiteBalanceRed'] = "%d" % inf.whitebal_r
                    md['whiteBalanceBlue'] = "%d" % inf.whitebal_b
                    md['filterNum'] = '0'
                    md['filterSetID'] = caminf.filter_set_id
                else:
                    md['HRCImage']  = "false"
                    md['filterNum'] = "%d" % inf.filter
                    md['filterSetID'] = caminf.filter_set_id
            if flags & api.META_SAVE_GPS:
                md['GPSLat']    = "%.6f" % inf.latitude
                md['GPSLong']   = "%.6f" % inf.longitude
                md['GPSAlt']    = "%.3f" % inf.altitude
            if flags & api.META_SAVE_IMU:
                md['IMURoll']   = "%.3f" % inf.roll
                md['IMUPitch']  = "%.3f" % inf.pitch
                md['IMUYaw']    = "%.3f" % inf.yaw
            md['pan']           = "%.4f" % inf.pan
            md['tilt']          = "%.4f" % inf.tilt
            md['dataProductID'] = inf.dataproduct_id
            md['sessionID']     = inf.session_id

        md['camName']       = caminf.name
        md['camClass']      = caminf.cam_class
        md['camID']         = caminf.unique_name
        md['camArch']       = caminf.driver
        md['camModel']      = caminf.model
        md['camGUID']       = caminf.guid
        md['camDesc']       = caminf.desc
        md['metaDataVer']   = "1.0"
        return md
        
# (inherited from ImageFrame)
#    def save_ppm(self, filename):
#        self.save_ppm(filename)

    def save_png_with_metadata(self, filename):
        META_TAG_PREFIX = "AU_"
        if self.depth == 1 and (self.format == api.IMAGE_FORMAT_MONO8
            or self.format == api.IMAGE_FORMAT_BAYER):
            # 8-bit grey
            pi = Image.frombuffer('L', (self.width, self.height), self.image, 'raw', 'L', 0, 1)
        elif self.depth == 3 and self.format == api.IMAGE_FORMAT_RGB8:
            # 8-bit RGB
            pi = Image.frombuffer('RGB', (self.width, self.height), self.image, 'raw', 'RGB', 0, 1)
        elif self.depth == 2 and self.format == api.IMAGE_FORMAT_MONO16:
            # 16-bit grey (?? ENDIANNESS ??)
            pi = Image.frombuffer('I', (self.width, self.height), self.image, 'raw', 'I;16', 0, 1)
        else:
            raise PanCamException("Cannot save image as PNG (format %d, depth %d)" %
                (self.format, self.depth))
        md = self.gen_metadata_tags()
        pinf = PngImagePlugin.PngInfo()
        for key, val in md.items():
            pinf.add_text(META_TAG_PREFIX+key, val)
        pi.save(filename, pnginfo=pinf)

class Camera(object):
    
    def __init__(self, cam_id, pancam_ss, info=None):
        self.cam_id = cam_id
        self.pc = pancam_ss
        self.info = info
    
    def setup_info(self):
        if self.info is None:
            v = self.pc.get_config(self.cam_id)
            if v is not None:
                ret, f, c, w, filter_set_num = self.pc.get_filter_info(self.cam_id)
                if ret:
                    raise PanCamException("GET FILTER INFO error for cam_id %d" % self.cam_id)
                self.info = CameraInfo(v, fs_num=filter_set_num)
    
    def get_image_metadata(self):
        ret, flags, m = self.pc.get_image_metadata(self.cam_id)
        if ret:
            raise PanCamException("GET METADATA error for cam_id %d" % self.cam_id)
        meta = ImageMetadata(m,flags)
        # Add in pan & tilt (bit of a fudge...)
        meta.pan = self.pc.ptu.pan
        meta.tilt = self.pc.ptu.tilt
        meta.dataproduct_id = ""
        meta.session_id = ""
        return meta

    shutter         = CamFloatFeature(api.CAM_FEATURE_SHUTTER)
    shutter_mode    = CamFeatureMode(api.CAM_FEATURE_SHUTTER)
    shutter_target  = CamFloatFeature(api.CAM_FEATURE_EXPOSURE)
    shutter_alg     = CamIntFeature(api.CAM_FEATURE_AE_ALG)
    shutter_tol     = CamFloatFeature(api.CAM_FEATURE_AE_TOL)
    shutter_max     = CamFloatFeature(api.CAM_FEATURE_AE_MAX)
    shutter_min     = CamFloatFeature(api.CAM_FEATURE_AE_MIN)
    shutter_outliers = CamFloatFeature(api.CAM_FEATURE_AE_OUTLIERS)
    shutter_rate    = CamFloatFeature(api.CAM_FEATURE_AE_RATE)
    @property
    def shutter_reg(self):
        ret, l = self.pc.get_feature(self.cam_id, api.CAM_FEATURE_REG_LEFT)
        if ret: raise PanCamException("GET DSP REGION LEFT error for cam_id %d" % self.cam_id)
        ret, t = self.pc.get_feature(self.cam_id, api.CAM_FEATURE_REG_TOP)
        if ret: raise PanCamException("GET DSP REGION TOP error for cam_id %d" % self.cam_id)
        ret, r = self.pc.get_feature(self.cam_id, api.CAM_FEATURE_REG_RIGHT)
        if ret: raise PanCamException("GET DSP REGION RIGHT error for cam_id %d" % self.cam_id)
        ret, b = self.pc.get_feature(self.cam_id, api.CAM_FEATURE_REG_BOTTOM)
        if ret: raise PanCamException("GET DSP REGION BOTTOM error for cam_id %d" % self.cam_id)
        self._dsp_reg = (l, t, r, b)
        return self._dsp_reg
    @shutter_reg.setter
    def shutter_reg(self, reg):
        l, t, r, b = reg
        self._dsp_reg = reg
        self.pc.set_feature(self.cam_id, api.CAM_FEATURE_REG_LEFT, l)
        self.pc.set_feature(self.cam_id, api.CAM_FEATURE_REG_TOP, t)
        self.pc.set_feature(self.cam_id, api.CAM_FEATURE_REG_RIGHT, r)
        self.pc.set_feature(self.cam_id, api.CAM_FEATURE_REG_BOTTOM, b)
    gain            = CamIntFeature(api.CAM_FEATURE_GAIN)
    gain_mode       = CamFeatureMode(api.CAM_FEATURE_GAIN)
    ae_algorithm    = CamIntFeature(api.CAM_XF_AE_ALG)
    ae_target       = CamFloatFeature(api.CAM_XF_AE_TARGET)
    ae_tolerance    = CamFloatFeature(api.CAM_XF_AE_TOL)
    ae_max_shutter  = CamFloatFeature(api.CAM_XF_AE_MAX)
    ae_min_shutter  = CamFloatFeature(api.CAM_XF_AE_MIN)
    ae_outliers     = CamFloatFeature(api.CAM_XF_AE_OUTLIERS)
    ae_adjust_rate  = CamFloatFeature(api.CAM_XF_AE_RATE)
    ae_max_frames   = CamIntFeature(api.CAM_XF_AE_MAXFRAMES)
    ae_meter_region = CamIntFeature(api.CAM_XF_AE_REGION)
    exp_delay       = CamFloatFeature(api.CAM_XF_EXP_DELAY)
    @property
    def roi(self):
        ret, x = self.pc.get_feature(self.cam_id, api.CAM_XF_ROI_X)
        if ret: raise PanCamException("GET ROI error for cam_id %d" % self.cam_id)
        ret, y = self.pc.get_feature(self.cam_id, api.CAM_XF_ROI_Y)
        if ret: raise PanCamException("GET ROI error for cam_id %d" % self.cam_id)
        ret, w = self.pc.get_feature(self.cam_id, api.CAM_XF_ROI_WIDTH)
        if ret: raise PanCamException("GET ROI error for cam_id %d" % self.cam_id)
        ret, h = self.pc.get_feature(self.cam_id, api.CAM_XF_ROI_HEIGHT)
        if ret: raise PanCamException("GET ROI error for cam_id %d" % self.cam_id)
        self._roi = (x, y, w, h)
        return self._roi
    @roi.setter
    def roi(self, roi):
        x, y, w, h = roi
        self._roi = roi
        self.pc.set_feature(self.cam_id, api.CAM_XF_ROI_X, x)
        self.pc.set_feature(self.cam_id, api.CAM_XF_ROI_Y, y)
        self.pc.set_feature(self.cam_id, api.CAM_XF_ROI_WIDTH, w)
        self.pc.set_feature(self.cam_id, api.CAM_XF_ROI_HEIGHT, h)
    

class MonoCamera(Camera):
    
    def __init__(self, cam_id, pancam_ss):
        super(MonoCamera, self).__init__(cam_id, pancam_ss)
        
    def get_image(self, ae=False, meta=api.META_SAVE_CAM, sync=False, last=False):
        im = PanCamImage(camera=self)
        flags = meta
        if ae:
            flags |= api.IMAGE_AUTOEXPOSE
        if sync:
            flags |= api.IMAGE_SYNC
        if last:
            flags |= api.IMAGE_PREVIOUS
        ret = self.pc.get_image_mono(self.cam_id, im, flags)
        if ret:
            raise PanCamException("GET IMAGE error for cam_id %d" % self.cam_id)
        if meta:
            md = self.get_image_metadata()
            im.info = md
        return im

    def get_image_16(self, ae=False, meta=api.META_SAVE_CAM, sync=False, last=False):
        im = PanCamImage(camera=self)
        flags = meta
        if ae:
            flags |= api.IMAGE_AUTOEXPOSE
        if sync:
            flags |= api.IMAGE_SYNC
        if last:
            flags |= api.IMAGE_PREVIOUS
        ret = self.pc.get_image_mono16(self.cam_id, im, flags)
        if ret:
            raise PanCamException("GET IMAGE error for cam_id %d" % self.cam_id)
        if meta:
            md = self.get_image_metadata()
            im.info = md
        return im

    def get_image_12p(self, ae=False, meta=api.META_SAVE_CAM, sync=False, last=False):
        im = PanCamImage(camera=self)
        flags = meta
        if ae:
            flags |= api.IMAGE_AUTOEXPOSE
        if sync:
            flags |= api.IMAGE_SYNC
        if last:
            flags |= api.IMAGE_PREVIOUS
        ret = self.pc.get_image_mono12p(self.cam_id, im, flags)
        if ret:
            raise PanCamException("GET IMAGE error for cam_id %d" % self.cam_id)
        if meta:
            md = self.get_image_metadata()
            im.info = md
        return im

class ColourCamera(Camera):
    
    def __init__(self, cam_id, pancam_ss):
        super(ColourCamera, self).__init__(cam_id, pancam_ss)
        
    def get_image(self, ae=False, meta=api.META_SAVE_CAM, sync=False, last=False):
        im = PanCamImage(camera=self)
        flags = meta
        if ae:
            flags |= api.IMAGE_AUTOEXPOSE
        if sync:
            flags |= api.IMAGE_SYNC
        if last:
            flags |= api.IMAGE_PREVIOUS
        ret = self.pc.get_image_rgb(self.cam_id, im, flags)
        if ret:
            raise PanCamException("GET IMAGE error for cam_id %d" % self.cam_id)
        if meta:
            md = self.get_image_metadata()
            im.info = md
        return im
        
    whitebalance        = CamIntFeature2(api.CAM_FEATURE_WHITEBALANCE)
    whitebalance_mode   = CamFeatureMode(api.CAM_FEATURE_WHITEBALANCE)

class WAC(MonoCamera):
    
    def __init__(self, cam_id, pancam_ss):
        super(WAC, self).__init__(cam_id, pancam_ss)
        
    filter = FilterSelector()

class HRC(ColourCamera):
    
    def __init__(self, cam_id, pancam_ss):
        super(HRC, self).__init__(cam_id, pancam_ss)
        
    zoom        = CamIntFeature(api.CAM_FEATURE_ZOOM)
    focus       = CamIntFeature(api.CAM_FEATURE_FOCUS)
    focus_mode  = CamFeatureMode(api.CAM_FEATURE_FOCUS)
    iris        = CamIntFeature(api.CAM_FEATURE_IRIS)
    iris_mode   = CamFeatureMode(api.CAM_FEATURE_IRIS)

class MonoHRC(MonoCamera):
    
    def __init__(self, cam_id, pancam_ss):
        super(MonoHRC, self).__init__(cam_id, pancam_ss)

class PTU(object):
    
    def __init__(self, mast_ss):
        self.ms = mast_ss
        
    @property
    def pan(self):
        ret, p, t = self.ms.get_pan_tilt(api.AS_ROUNDED)
        if ret:
            raise PanCamException("GET PAN error for cam_id %d" % self.cam_id)
        return p
    @pan.setter
    def pan(self, value):
        ret = self.ms.set_pan(value)
        if ret:
            raise PanCamException("SET PAN error for cam_id %d" % self.cam_id)
        
    @property
    def tilt(self):
        ret, p, t = self.ms.get_pan_tilt(api.AS_ROUNDED)
        if ret:
            raise PanCamException("GET TILT error for cam_id %d" % self.cam_id)
        return t
    @tilt.setter
    def tilt(self, value):
        ret = self.ms.set_tilt(value)
        if ret:
            raise PanCamException("SET TILT error for cam_id %d" % self.cam_id)
        
    @property
    def pan_tilt(self):
        ret, p, t = self.ms.get_pan_tilt(api.AS_ROUNDED)
        if ret:
            raise PanCamException("GET PAN_TILT error for cam_id %d" % self.cam_id)
        return p, t
    @pan_tilt.setter
    def pan_tilt(self, value):
        ret = self.ms.set_pan_tilt(*value)
        if ret:
            raise PanCamException("SET PAN_TILT error for cam_id %d" % self.cam_id)
        
    def stow(self):
        self.ms.stow()


# Set up the "standard" PanCam

agent = api.AgentConnection()
system = api.SystemSubsys(agent)
pancam = api.PanCamSubsys(agent)
mast = api.MastSubsys(agent)   # Include mast (PTU) here for convenience

lwac = WAC(api.CAMERA_WACL, pancam)
rwac = WAC(api.CAMERA_WACR, pancam)
hrc = MonoHRC(api.CAMERA_HRC, pancam)
pancam.cameras = [ lwac, rwac, hrc ]

ptu = PTU(mast)

pancam.ptu = ptu

if __name__ == "__main__":

    system.connect()
    pancam.setup_cameras()
    print("LWAC shutter: %.4f, gain: %d" % (lwac.shutter, lwac.gain))
    print("RWAC shutter: %.4f, gain: %d" % (rwac.shutter, rwac.gain))
    if hrc:
        print("HRC  shutter: %.4f, gain: %d" % (hrc.shutter, hrc.gain))
        print("HRC  zoom: %d, focus: %d, iris: %d" % (hrc.zoom, hrc.focus, hrc.iris))

#    im = hrc.get_image(flags=256)
#    save_image(im, 'zz')

    system.disconnect()

