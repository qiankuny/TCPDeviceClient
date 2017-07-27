# _*_ coding: UTF-8 _*_
'''
Created on 2015/12/28

@author: oscal
'''
import ctypes as ct

class LittleEndianStructBase(ct.LittleEndianStructure):
    def __init__(self):
        self._data = None
        
    def pack(self):
        return ct.string_at(ct.pointer(self), ct.sizeof(self))
    
    @classmethod
    def unpack(cls,data):
        if None != data:
            s = ct.cast(data, ct.POINTER(cls)).contents
            s._data = data
            return s

class BigEndianStructBase(ct.BigEndianStructure):
    def __init__(self):
        self._data = None
        
    def pack(self):
        return ct.string_at(ct.pointer(self), ct.sizeof(self))
    
    @classmethod
    def unpack(cls,data):
        if None != data:
            s = ct.cast(data, ct.POINTER(cls)).contents
            s._data = data
            return s
        