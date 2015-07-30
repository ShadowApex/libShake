#!/usr/bin/python
from ctypes import *
from time import sleep

libShake = cdll.LoadLibrary('libshake.so')

Shake_EffectType = c_int
SHAKE_EFFECT_RUMBLE = Shake_EffectType(0)
SHAKE_EFFECT_PERIODIC = Shake_EffectType(1)
SHAKE_EFFECT_CONSTANT = Shake_EffectType(2)
SHAKE_EFFECT_SPRING = Shake_EffectType(3)
SHAKE_EFFECT_FRICTION = Shake_EffectType(4)
SHAKE_EFFECT_DAMPER = Shake_EffectType(5)
SHAKE_EFFECT_INERTIA = Shake_EffectType(6)
SHAKE_EFFECT_RAMP = Shake_EffectType(7)
SHAKE_EFFECT_COUNT = Shake_EffectType(8)

Shake_PeriodicWaveform = c_int
SHAKE_PERIODIC_SQUARE = Shake_PeriodicWaveform(0)
SHAKE_PERIODIC_TRIANGLE = Shake_PeriodicWaveform(1)
SHAKE_PERIODIC_SINE = Shake_PeriodicWaveform(2)
SHAKE_PERIODIC_SAW_UP = Shake_PeriodicWaveform(3)
SHAKE_PERIODIC_SAW_DOWN = Shake_PeriodicWaveform(4)
SHAKE_PERIODIC_CUSTOM = Shake_PeriodicWaveform(5)
SHAKE_PERIODIC_COUNT = Shake_PeriodicWaveform(6)

class Shake_EffectRumble(Structure):
    _fields_ = [
        ("strongMagnitude", c_int),
        ("weakMagnitude", c_int)]

class Shake_Envelope(Structure):
    _fields_ = [
        ("attackLength", c_int),
        ("attackLevel", c_int),
        ("fadeLength", c_int),
        ("fadeLevel", c_int)]

class Shake_EffectPeriodic(Structure):
    _fields_ = [
        ("waveform", Shake_PeriodicWaveform),
        ("period", c_int),
        ("magnitude", c_int),
        ("offset", c_int),
        ("phase", c_int),
        ("envelope", Shake_Envelope)]

class Shake_Union(Union):
    _fields_ = [
        ("rumble", Shake_EffectRumble),
        ("periodic", Shake_EffectPeriodic)]

class Shake_Effect(Structure):
    _anonymous_ = ('u')
    _fields_ = [
        ("type", Shake_EffectType),
        ("id", c_int),
        ("direction", c_int),
        ("length", c_int),
        ("delay", c_int),
        ("u", Shake_Union)]


def device_info(device):
    print "Device #%d" % libShake.Shake_DeviceId(device)
    print " Name:", c_char_p(libShake.Shake_DeviceName(device)).value
    print " Adjustable gain:", libShake.Shake_QueryGainSupport(device)
    print " Adjustable autocenter:", libShake.Shake_QueryAutocenterSupport(device)
    print " Effect capacity:", libShake.Shake_DeviceEffectCapacity(device)
    print " Supported effects:"
    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_RUMBLE):
        print "  SHAKE_EFFECT_RUMBLE"

    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_PERIODIC):
        print "  SHAKE_EFFECT_PERIODIC"
        if libShake.Shake_QueryWaveformSupport(device, SHAKE_PERIODIC_SQUARE):
            print "  * SHAKE_PERIODIC_SQUARE"
        if libShake.Shake_QueryWaveformSupport(device, SHAKE_PERIODIC_TRIANGLE):
            print "  * SHAKE_PERIODIC_TRIANGLE"
        if libShake.Shake_QueryWaveformSupport(device, SHAKE_PERIODIC_SINE):
            print "  * SHAKE_PERIODIC_SINE"
        if libShake.Shake_QueryWaveformSupport(device, SHAKE_PERIODIC_SAW_UP):
            print "  * SHAKE_PERIODIC_SAW_UP"
        if libShake.Shake_QueryWaveformSupport(device, SHAKE_PERIODIC_SAW_DOWN):
            print "  * SHAKE_PERIODIC_SAW_DOWN"
        if libShake.Shake_QueryWaveformSupport(device, SHAKE_PERIODIC_CUSTOM):
            print "  * SHAKE_PERIODIC_CUSTOM"

    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_CONSTANT):
        print "  SHAKE_EFFECT_CONSTANT"
    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_SPRING):
        print "  SHAKE_EFFECT_SPRING"
    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_FRICTION):
        print "  SHAKE_EFFECT_FRICTION"
    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_DAMPER):
        print "  SHAKE_EFFECT_DAMPER"
    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_INERTIA):
        print "  SHAKE_EFFECT_INERTIA"
    if libShake.Shake_QueryEffectSupport(device, SHAKE_EFFECT_RAMP):
        print "  SHAKE_EFFECT_RAMP"


if __name__ == "__main__":
    libShake.Shake_Init()
    print "Detected devices:", libShake.Shake_NumOfDevices()

    if libShake.Shake_NumOfDevices() > 0:
        device = libShake.Shake_Open(0)
        device_info(device)

        effect = Shake_Effect()
        libShake.Shake_InitEffect(pointer(effect), SHAKE_EFFECT_PERIODIC)
        effect.periodic.waveform               = SHAKE_PERIODIC_SINE
        effect.periodic.period                 = int(0.1 * int('0x100', 16))
        effect.periodic.magnitude              = int('0x6000', 16)
        effect.periodic.envelope.attackLengeth = int('0x100', 16)
        effect.periodic.envelope.attackLevel   = 0
        effect.periodic.envelope.fadeLength    = int('0x100', 16)
        effect.periodic.envelope.fadeLevel     = 0
        effect.direction                       = int('0x4000', 16)
        effect.length                          = 2000
        effect.delay                           = 0

        id = libShake.Shake_UploadEffect(device, pointer(effect))
        libShake.Shake_Play(device, id)

        sleep(2)
        libShake.Shake_EraseEffect(device, id)
        libShake.Shake_Close(device)

    libShake.Shake_Quit()
