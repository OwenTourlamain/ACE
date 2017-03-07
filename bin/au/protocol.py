#!/usr/bin/python3
# -*- coding: utf-8 -*-

PROTOCOL_VERSION    = 3
PROTOCOL_MINOR      = 2
IDENT               = 0xB0AD1CEA
PKT_LEN             = 32

# Angle multiplier for arm & PTU: degrees to integer units
ANG_SCALE           = 1000000
# Angle multiplier for IMU & GPS: degrees to integer units
ANG_SCALE_FINE      = 10000000
# Time multiplier for shutter: seconds to integer units (usec)
SHUTTER_SCALE       = 1000000
# Distance multiplier for altitude: metres to integer units (mm)
DIST_SCALE          = 1000

# 32 bytes in package:
# uint32_t  ident;
#   uint16_t    subsys;
#   uint16_t    cmd;
#   int32_t     arg1, arg2, arg3, arg4;
#   int32_t     unused;
#   uint32_t    num_data_bytes;

#====== Enumerated types for function parameters =====

# PanCam camera IDs

(   CAMERA_ID0,
    CAMERA_ID1,
    CAMERA_ID2,
    PANCAM_NUM_CAMS ) = range(4)

CAMERA_WACL = CAMERA_ID0
CAMERA_WACR = CAMERA_ID1
CAMERA_HRC = CAMERA_ID2

CAMERA_ID0_NAME     = "CAM0"
CAMERA_ID1_NAME     = "CAM1"
CAMERA_ID2_NAME     = "CAM2"

CAMERA_WACL_NAME    = "LWAC"
CAMERA_WACR_NAME    = "RWAC"
CAMERA_HRC_NAME     = "HRC"

CAMERA_ID0_DESC     = "Channel 0 master camera"
CAMERA_ID1_DESC     = "Channel 1 camera"
CAMERA_ID2_DESC     = "Channel 2 camera"

CAMERA_WACL_DESC    = "Wide-angle camera (left)"
CAMERA_WACR_DESC    = "Wide-angle camera (right)"
CAMERA_HRC_DESC     = "High resolution camera"

# Aerobot camera IDs

(   CAMERA_AEROCAM,
    AEROBOT_NUM_CAMS ) = range(2)

CAMERA_ACAM_NAME    = "ACAM"
CAMERA_ACAM_DESC    = "Aerobot multispectral camera"

# Mast PTU joints

(   PTU_PAN,
    PTU_TILT,
    PTU_NUM_JOINTS ) = range(3)

# Arm joints

(   ARM_BASE,
    ARM_SHOULDER,
    ARM_ELBOW,
    ARM_NUM_JOINTS ) = range(4)

# Image formats

(   IMAGE_FORMAT_RGB8,
    IMAGE_FORMAT_YUV422,
    IMAGE_FORMAT_MONO8,
    IMAGE_FORMAT_BAYER,
    IMAGE_FORMAT_MONO16,
    IMAGE_FORMAT_MONO12P,
    IMAGE_NUM_FORMATS ) = range(7)

# Camera features

(   CAM_FEATURE_BRIGHTNESS,
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
    CAM_FEATURE_AE_RATE,
    CAM_FEATURE_REG_LEFT,
    CAM_FEATURE_REG_TOP,
    CAM_FEATURE_REG_RIGHT,
    CAM_FEATURE_REG_BOTTOM,
    CAM_NUM_FEATURES ) = range(23)

# Extended (server-side) camera features

CAM_XF_BASE = 200

(   CAM_XF_AE_ALG,
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
    CAM_XF_EXP_DELAY,
    CAM_XF_MAX_FEATURE ) = range(CAM_XF_BASE, CAM_XF_BASE+15)

CAM_NUM_XFEATURES = CAM_XF_MAX_FEATURE - CAM_XF_BASE

# Camera feature modes

(   FEATURE_MODE_MANUAL,
    FEATURE_MODE_AUTO,
    FEATURE_MODE_ONCE,
    FEATURE_MODE_EXTERN,
    FEATURE_NUM_MODES ) = range(5)

# Auto Exposure algorithm selection

(   AE_ALG_MEAN,
    AE_ALG_RANGE,
    AE_NUM_ALGS ) = range(3)

# Auto Exposure region selection

(   AE_REGION_FULL,
    AE_REGION_ROI,
    AE_NUM_REGIONS ) = range(3)

# Frame discard mode selection

(   FRAME_DISCARD_FIXED,
    FRAME_DISCARD_SHUTTER,
    FRAME_DISCARD_GAIN,
    FRAME_DISCARD_NUM_MODES ) = range(4)

# Joint angle selection

(   AS_COMMANDED,
    AS_ROUNDED,
    AS_MEASURED ) = range(3)

# Metadata array indices

(   METADATA_CAMERA_ID,
    METADATA_TIMESTAMP_SEC,
    METADATA_TIMESTAMP_NANO,
    METADATA_SHUTTER,
    METADATA_GAIN,
    METADATA_FILTER,
    METADATA_ROLL,
    METADATA_PITCH,
    METADATA_YAW,
    METADATA_LATITUDE,
    METADATA_LONGITUDE,
    METADATA_ALTITUDE,
    METADATA_WHITEBAL_R,
    METADATA_WHITEBAL_B,
    METADATA_FOCUS,
    METADATA_ZOOM,
    METADATA_IRIS,
    METADATA_NUM_VALUES ) = range(18)

# Image & metadata request flag bits

META_SAVE_CAM = 0x0001
META_SAVE_IMU = 0x0002
META_SAVE_GPS = 0x0004
META_SAVE_ALL = 0x0007

IMAGE_AUTOEXPOSE = 0x0100
IMAGE_PREVIOUS = 0x0200
IMAGE_SYNC = 0x0400

#============== Protocol status values ============

(   STATUS_OK,
    STATUS_ERROR,
    STATUS_NOTIMP,
    STATUS_BADSUBSYS,
    STATUS_BADFUNC,
    STATUS_BADPARAM,
    STATUS__MAX__VALUE ) = range(7)

#================ Subsystems supported ============

(   SUBSYS_NONE,
    SUBSYS_SYSTEM,
    SUBSYS_PANCAM,
    SUBSYS_MAST,
    SUBSYS_ARM,
    SUBSYS_CHASSIS,
    SUBSYS_VICON,
    SUBSYS_AEROCAM,
    SUBSYS_AEROBOT,
    SUBSYS__MAX__VALUE ) = range(10)

#=============== Protocol commands ==============

# System-level commands

(   COMMAND_NONE,   # (special value of zero)
    SYSTEM_CONNECT,
    SYSTEM_DISCONNECT,
    SYSTEM_SHUTDOWN,
    SYSTEM_GET_VERSION,
    SYSTEM__MAX__CMD ) = range(6)

# PanCam (camera) commands

(   DUMMY_ZERO,
    CAM_GET_IMAGE,
    CAM_SET_FEATURE_VALUE,
    CAM_GET_FEATURE_VALUE,
    CAM_SET_FEATURE_MODE,
    CAM_GET_FEATURE_MODE,
    CAM_SET_IMAGE_FORMAT,
    CAM_GET_IMAGE_FORMAT,
    CAM_SET_FILTER,
    CAM_GET_FILTER,
    CAM_STOW_FILTERS,
    CAM_SET_FEATURE_ABS_VALUE,
    CAM_GET_FEATURE_ABS_VALUE,
    CAM_GET_PANCAM_CONFIG,
    CAM_GET_IMAGE_METADATA,
    CAM_DISCARD_FRAMES,
    CAM_GET_LAST_IMAGE,
    PANCAM__MAX__CMD ) = range(18)

# Mast PTU commands

(   DUMMY_ZERO,
    PTU_SET_ALL_JOINTS,
    PTU_SET_ONE_JOINT,
    PTU_STOW,
    PTU_GET_JOINTS,
    MAST__MAX__CMD ) = range(6)

# Rover arm commands

(   DUMMY_ZERO,
    ARM_SET_ALL_JOINTS,
    ARM_SET_ONE_JOINT,
    ARM_STOW,
    ARM_GET_JOINTS,
    ARM__MAX__CMD ) = range(6)

# Rover chassis commands

CHASSIS__MAX__CMD = 1

# Vicon interface commands

(   DUMMY_ZERO,
    VICON_GET_PAN_TILT,
    VICON__MAX__CMD ) = range(3)

# Aerocam interface commands

(   DUMMY_ZERO,
    AEROCAM_GET_IMAGE,
    AEROCAM_SET_FEATURE_VALUE,
    AEROCAM_GET_FEATURE_VALUE,
    AEROCAM_SET_FEATURE_MODE,
    AEROCAM_GET_FEATURE_MODE,
    AEROCAM_SET_IMAGE_FORMAT,
    AEROCAM_GET_IMAGE_FORMAT,
    AEROCAM_SET_FILTER,
    AEROCAM_GET_FILTER,
    AEROCAM_STOW_FILTERS,
    AEROCAM_SET_FEATURE_ABS_VALUE,
    AEROCAM_GET_FEATURE_ABS_VALUE,
    AEROCAM_GET_CONFIG,
    AEROCAM_GET_IMAGE_METADATA,
    AEROCAM_DISCARD_FRAMES,
    AEROCAM__MAX__CMD ) = range(17)

# Aerobot platform commands

(   DUMMY_ZERO,
    AEROBOT_GET_ORIENTATION,
    AEROBOT_GET_POSITION,
    AEROBOT_GET_HEIGHT,
    AEROBOT_GET_TETHER_ANGLES,
    AEROBOT_RESET_IMU,
    AEROBOT__MAX__CMD ) = range(7)

