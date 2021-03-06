#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classes
========
  
@Autores:
- Matheus Lazarin Alberto, mtslazarin@gmail.com
- João Vitor Gutkoski Paes, joao.paes@eac.ufsm.br

This submodule is mainly the means to an end. PyTTa is made intended to be
user friendly, the manipulation of the classes are documented here, but their
instantiation should be used through the <generate> submodule:
    
    >>> pytta.generate.sweep()
    >>> pytta.generate.noise()
    >>> pytta.generate.measurement('playrec')
    >>> pytta.generate.measurement('rec', domain = 'time', timeLen = 5)
    
This way, the default settings will be loaded into any object instantiated.

User intended classes:
    
    >>> pytta.SignalObj()
    >>> pytta.RecMeasure()
    >>> pytta.PlayRecMeasure()
    >>> pytta.FRFMeasure()
    
For further information see the specific class, or method, documentation
"""
#%% Importing modules
#import pytta as pa
import numpy as np
import matplotlib.pyplot as plot
import scipy.signal as signal
import sounddevice as sd
from pytta import default


class PyTTaObj(object):
    """
    PyTTa object class to define some properties and methods to be used 
    by any signal and processing classes. pyttaObj is a private class created
    just to shorten attributes declaration to each PyTTa class.
    
    Properties(self):    (default),     meaning
        - samplingRate:  (44100),       signal's sampling rate
        - freqLimits:    ([20,20000]),  frequency bandwidth limits
        - comment:       (' '),         some commentary about the signal or measurement object
        
    """

    def __init__(self,samplingRate=None,
                 fftDegree = None,
                 timeLength = None,
                 numSamples = None,
                 freqMin = None,
                 freqMax = None,
                 comment = "No comments."
                 ):
        self._samplingRate = samplingRate
        self._fftDegree = fftDegree
        self._timeLength = timeLength
        self._numSamples = numSamples
        self._freqMin, self._freqMax = freqMin, freqMax
        self._comment = comment

#%% PyTTaObj Properties
                
    @property
    def samplingRate(self):
        return self._samplingRate

    @property
    def fftDegree(self):
        return self._fftDegree

    @property
    def timeLength(self):
        return self._timeLength

    @property
    def numSamples(self):
        return self._numSamples

    @property
    def freqMin(self):
        return self._freqMin

    @property
    def freqMax(self):
        return self._freqMax

    @property
    def comment(self):
        return self._comment

#%% PyTTaObj Methods

    def __call__(self):
        for name, value in vars(self).items():
            if len(name)<=8:
                print(name[1:]+'\t\t =',value)
            else: 
                print(name[1:]+'\t =',value)
                
    

class SignalObj(PyTTaObj):

    """
    Signal object class.
    
    Properties(self): 	   	(default),   	meaning  
        - timeSignal:   	(ndarray),   	signal at time domain;
        - timeVector:   	(ndarray),   	time reference vector for timeSignal;
        - freqSignal:   	(ndarray),   	signal at frequency domain;
        - freqVector:   	(ndarray),   	frequency reference vector for freqSignal;
        - numSamples:	(samples),   	signal's number of samples;
        - timeLength:  	(seconds),   	signal's duration;
        
    Properties(inherited):  (default),          meaning
        - samplingRate:     (44100),            signal's sampling rate;
        - freqMin:	   (20),               minimum frequency bandwidth limit;
        - freqMax:	   (20000),            maximum frequency bandwidth limit;
        - comment: 	   ('No comments.')    some commentary about the signal;        
        
    Methods: 	 	 	meaning
        - play():  	 	reproduce the timeSignal with default output device;
        - plot_time():  	generates the signal's historic graphic;
        - plot_freq():  	generates the signal's spectre graphic;
    
    """
    
    def __init__(self,
                     signalArray=np.array([0]),
                     domain='time',
                     *args,
                     **kwargs):
        if self.size_check(signalArray)>2:
            message = "No 'pyttaObj' is able handle arrays with more \
                        than 2 dimensions, '[:,:]', YET!."
            raise AttributeError(message)
        else:
            pass
        super().__init__(*args,**kwargs)
        self._domain = domain or args[1]
        if self.domain == 'freq':
            self.freqSignal = signalArray # [-] signal in frequency domain
        elif self.domain == 'time':
            self.timeSignal = signalArray # [-] signal in time domain
        else:
            self.timeSignal = signalArray
            print('Taking the input as a time domain signal')
            self.domain = 'time'

#%% Signal Properties
           
    @property
    def domain(self):
        return self._domain
    
    @property 
    def timeVector(self):
        return self._timeVector
    
    @property 
    def freqVector(self):
        return self._freqVector
            
    @property # when timeSignal is called returns the ndarray
    def timeSignal(self):
        return self._timeSignal
    @timeSignal.setter
    def timeSignal(self,newSignal): # when timeSignal have new ndarray value,
                                    # calculate other properties
        self._timeSignal = np.array(newSignal)
        self._numSamples = len(self.timeSignal) # [-] number of samples
        self._fftDegree = np.log2(self.numSamples) # [-] size parameter
        
        # [s] signal time lenght
        self._timeLength = self.numSamples / self.samplingRate
        
        # [s] time vector (x axis)
        self._timeVector = np.linspace( 0, \
                                      self.timeLength \
                                          - (1/self.samplingRate), \
                                      self.numSamples ) 
        
        # [Hz] frequency vector (x axis)
        self._freqVector = np.linspace( 0, \
                                      (self.numSamples - 1) \
                                          * self.samplingRate \
                                          / self.numSamples, \
                                      self.numSamples )
        
        # [-] signal in frequency domain
        self._freqSignal = np.transpose( np.fft.fft( \
                                      self.timeSignal.transpose() ) )


    @property
    def freqSignal(self): 
        return self._freqSignal
    @freqSignal.setter
    def freqSignal(self,newSignal):
        self._freqSignal = np.array(newSignal)
        self._timeSignal = np.transpose( \
                                        np.real( \
                                        np.fft.ifft( \
                                        self.freqSignal.transpose()
                                        ) ) )
        self._numSamples = len(self.timeSignal) # [-] number of samples
        self._fftDegree = np.log2(self.numSamples) # [-] size parameter
        
        # [s] signal time lenght
        self._timeLength = self.numSamples/self.samplingRate 
        
        # [s] time vector
        self._timeVector = np.arange(0, self.timeLength, 1/self.samplingRate)
        
        # [Hz] frequency vector
        self._freqVector = np.linspace(0, (self.numSamples-1) \
                                       * self.samplingRate \
                                       / self.numSamples, \
                                       self.numSamples)

        
#%% Signal Methods
        
    def __truediv__(self, other):
        """
        Frequency domain division method
        """
        if type(other) != type(self):
            raise TypeError("A SignalObj can only operate with other alike")

        result = SignalObj(samplingRate=self.samplingRate)
        result._domain = 'freq'
        if self.size_check() > 1:
            if other.size_check() > 1:
                i = 0
                for channelA in range(self.num_channels()):
                    for channelB in range(other.num_channels()):
                        result.freqSignal[:,i + channelB] = \
                                self.freqSignal[:,channelA] \
                                /other.freqSignal[:,channelB]
                    i = channelB
            else:
                for channel in range(self.num_channels()):
                    result.freqSignal = self.freqSignal[:,channel] \
                                        /other.freqSignal
                                        
        elif other.size_check() > 1:
            for channel in range(self.num_channels()):
                result.freqSignal = self.freqSignal \
                                /other.freqSignal[:,channel]
                                
        else: result.freqSignal = self.freqSignal / other.freqSignal

        return result
    
    
    def __add__(self, other):
        """
        Time domain addition method
        """
        if type(other) != type(self):
            raise TypeError("A SignalObj can only operate with other alike")

        result = SignalObj(samplingRate=self.samplingRate)
        result.domain = 'time'
        if self.size_check() > 1:
            if other.size_check() > 1:
                i = 0
                for channelA in range(self.num_channels()):
                    for channelB in range(other.timeSignal.shape):
                        result.timeSignal[:,i + channelB] = \
                                self.timeSignal[:,channelA] \
                                +other.timeSignal[:,channelB]
                    i = channelB
            else:
                for channel in range(self.num_channels()):
                    result.freqSignal = self.timeSignal[:,channel] \
                                        +other.timeSignal
                                        
        elif other.size_check() > 1:
            for channel in range(self.num_channels()):
                result.timeSignal = self.timeSignal \
                                +other.timeSignal[:,channel]
                                
        else: result.timeSignal = self.timeSignal + other.timeSignal
        return result


    def __sub__(self, other):
        """
        Time domain subtraction method
        """
        if type(other) != type(self):
            raise TypeError("A SignalObj can only operate with other alike")

        result = SignalObj(samplingRate=self.samplingRate)
        result.domain = 'time'
        if self.size_check() > 1:
            if other.size_check() > 1:
                i = 0
                for channelA in range(self.num_channels()):
                    for channelB in range(other.num_channels):
                        result.timeSignal[:,i + channelB] \
                                =self.timeSignal[:,channelA] \
                                -other.timeSignal[:,channelB]
                    i = channelB
            else:
                for channel in range(self.num_channels()):
                    result.freqSignal = self.timeSignal[:,channel] \
                                        -other.timeSignal
                                        
        elif other.size_check() > 1:
            for channel in range(self.num_channels()):
                result.timeSignal = self.timeSignal \
                                -other.timeSignal[:,channel]
                                
        else: result.timeSignal = self.timeSignal - other.timeSignal
        return result
    

    def mean(self):
        return SignalObj(np.mean(self.timeSignal,1),'time',self.samplingRate)
    
    def num_channels(self):
        try:
            numChannels = np.shape(self.timeSignal)[1]
        except IndexError:
            numChannels = 1
        return numChannels
    
    def size_check(self, inputArray = []):
        if inputArray == []: inputArray = self.timeSignal[:]
        return np.size( inputArray.shape )


    def play(self,outChannel=None,latency='low',**kwargs):
        """
        Play method
        """
        if outChannel == None:
            if self.num_channels() <=1:
                outChannel = default.outChannel
            elif self.num_channels() > 1:
                outChannel = np.arange(1,self.num_channels()+1)
                
        sd.play(self.timeSignal,self.samplingRate,mapping=outChannel,**kwargs)
			   
#   def plot(self): # TODO
#        ...

    def plot_time(self):
        """
        Time domain plotting method
        """
        plot.figure( figsize=(10,5) )
        plot.plot( self.timeVector, self.timeSignal )
        plot.axis( [ self.timeVector[0] - 10/self.samplingRate, \
                    self.timeVector[-1] + 10/self.samplingRate, \
                    1.05*np.min( self.timeSignal ), \
                   1.05*np.max( self.timeSignal ) ] )
        plot.xlabel(r'$Time$ [s]')
        plot.ylabel(r'$Amplitude$ [-]')
        
    def plot_freq(self,smooth=True):
        """
        Frequency domain plotting method
        """
        plot.figure( figsize=(10,5) )
        if not smooth:
            dBSignal = 20 * np.log10( np.abs( \
                            (2 / self.numSamples ) * self.freqSignal ) )
            plot.semilogx( self.freqVector, dBSignal )
        else:
            signalSmooth = signal.savgol_filter( np.abs( \
                                    self.freqSignal.transpose() ), 31, 3 )
            dBSignal = 20 * np.log10( np.abs( signalSmooth ) )
            plot.semilogx( self.freqVector, dBSignal.transpose() )
        plot.axis( ( 15, 22050, 
                   np.min( dBSignal )/1.05, 1.05*np.max( dBSignal ) ) )
        plot.xlabel(r'$Frequency$ [Hz]')
        plot.ylabel(r'$Magnitude$ [dBFS]')



class Measurement(PyTTaObj):
    """
    Measurement object class created to define some properties and methods to
    be used by the playback, recording and processing classes. It is a private
    class
    
    Properties(self): 	 	(default), 	 	 	meaning
        - device: 	 	 	(system default),  	list of input and output devices;
        - inChannel:  	 	([1]), 	 	 	 	list of device's input channel used for recording;
        - outChannel: 	 	([1]), 	 	 	 	list of device's output channel used for playing/reproducing a signalObj

    Properties(inherited): 	(default), 	 	 	meaning
        - samplingRate: 	 	(44100), 	 	 	measurement's sampling rate;
        - freqMin: 	 	 	(20),               minimum frequency bandwidth limits;
        - freqMax: 	 	 	(20000),            maximum frequency bandwidth limits;
        - comment: 	 	 	('No comments')     some commentary about the measurement;        
        
    """
    def __init__(self,
                 device=None,
                 inChannel=None,
                 outChannel=None,
                 *args,
                 **kwargs
                 ):
        super().__init__(*args,**kwargs)
        self._device = device # device number. For device list use sounddevice.query_devices()
        self._inChannel = inChannel # input channels
        self._outChannel = outChannel # output channels
        
#%% Measurement Properties
        
    @property
    def device(self):
        return self._device
    
    @property
    def inChannel(self):
        return self._inChannel
    
    @property
    def outChannel(self):
        return self._outChannel
        
        
        
class RecMeasure(Measurement):
    """
    Signal Recording object
    
    Properties(self) 	 	 (default), 	 	meaning:
		- domain:  	 	 	 ('samples'), 	Information about the recording length. May be 'time' or 'samples';
		- fftDegree:	 	 	 (18),  	 	 	number of samples will be 2**fftDeg. Used if domain is set to 'samples';
		- timeLength: 	 	 (10), 	 	  	time length of the recording. Used if domain is set to 'time';

    Properties(inherited) 	(default), 	 	 	meaning:
        - device: 	 	 	(system default),  	list of input and output devices;
        - inChannel:	 	 	([1]), 	 	 	 	list of device's input channel used for recording;
        - outChannel: 	 	([1]), 	 	 	 	list of device's output channel used for playing/reproducing a signalObj
        - samplingRate: 	 	(44100), 	 	 	recording's sampling rate;
        - freqMin: 	 	 	(20),               minimum frequency bandwidth limits;
        - freqMax: 	 	 	(20000),            maximum frequency bandwidth limits;
        - comment: 	 	 	('No comments.')	 	some commentary about the measurement;        

	Methods  	 	meaning:
		- run(): 	starts recording using the inch and device information, during timeLen seconds;
		

    """
    def __init__(self,domain=None,
                 fftDegree=None,
                 timeLength=None,
                 *args,**kwargs):
        super().__init__(*args,**kwargs)
        self._domain = domain
        if self.domain == 'samples':
            self._fftDegree = fftDegree
        elif self.domain == 'time':
            self._timeLength = timeLength
        else:
            self._timeLength = None
            self._fftDegree = None

#%% Rec Properties
            
    @property
    def timeLength(self):
        return self._timeLength
    @timeLength.setter
    def timeLength(self,newLength):
        self._timeLength = np.round( newLength, 2 )
        self._numSamples = self.timeLength * self.samplingRate
        self._fftDegree = np.round( np.log2( self.numSamples ), 2 )
        
    @property
    def fftDegree(self):
        return self._fftDegree
    @fftDegree.setter
    def fftDegree(self,newDegree):
        self._fftDegree = np.round( newDegree, 2 )
        self._numSamples = 2**self.fftDegree
        self._timeLength = np.round( self.numSamples / self.samplingRate, 2 )

#%% Rec Methods
        
    def run(self):
        """
        Run method: starts recording during Tmax seconds
        Outputs a signalObj with the recording content
        """
        self.recording = sd.rec(self.numSamples,
                                self.samplingRate,
                                mapping = self.inChannel,
                                blocking=True,
                                latency='low',
                                dtype = 'float32'
                                )
        self.recording = np.squeeze(self.recording)
        self.recording = SignalObj(self.recording,'time',self.samplingRate)
        maxOut = np.max(np.abs(self.recording.timeSignal[:,:]))
        print('max input level (recording): ', 20*np.log10(maxOut), 'dBFs - ref.: 1 [-]')
        return self.recording
    
    
    
class PlayRecMeasure(Measurement):
    """
    Playback and Record object

    Properties(self) 	 	 (default),         meaning:
		- excitation:  	 	 (SignalObj), 	 	Signal information used to reproduce (playback);
		- samplingRate:      (44100), 	 	 	signal's sampling rate;
        - freqMin: 	 	 	 (20),              minimum frequency bandwidth limits;
        - freqMax: 	 	 	 (20000),           maximum frequency bandwidth limits;
        - numSamples:    	 (len(timeSignal)), number of samples will be 2**fftDeg. Used if domain is set to 'samples';
		- timeLen: 	 	 	 (numSamples/samplingRate),  time length of the recording. Used if domain is set to 'time';

    Properties(inherited): 	(default), 	 	 	meaning:
        - device: 	 	 	(system default),  	list of input and output devices;
        - inChannel:  	 	([1]), 	 	 	 	list of device's input channel used for recording;
        - outChannel: 	 	([1]), 	 	 	 	list of device's output channel used for playing/reproducing a signalObj
        - comment: 	 	 	('No comments.'), 	some commentary about the measurement;

	Methods 	  	 	meaning:
		- run(): 	 	starts playing the excitation signal and recording during the excitation timeLen duration;

    """
    def __init__(self,excitation=None,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if excitation is None:
            self._excitation = None
        else:
            self.excitation = excitation

#%% PlayRec Methods
            
    def run(self):
        """
        Starts reproducing the excitation signal and recording at the same time
        Outputs a signalObj with the recording content
        """
        recording = sd.playrec(self.excitation.timeSignal,
                             samplerate=self.samplingRate, 
                             input_mapping=self.inChannel,
                             output_mapping=self.outChannel,
                             device=self.device,
                             blocking=True,
                             latency='low',
                             dtype = 'float32'
                             ) # y_all(t) - out signal: x(t) conv h(t)
        recording = np.squeeze( recording ) # turn column array into line array
        self.recording = SignalObj(recording, 'time', self.samplingRate )
#        print('max output level (excitation): ', 20*np.log10(max(self.excitation.timeSignal)), 'dBFs - ref.: 1 [-]')
#        print('max input level (recording): ', 20*np.log10(max(self.recording.timeSignal)), 'dBFs - ref.: 1 [-]')
        return self.recording

#%% PlayRec Properties
            
    @property
    def excitation(self):
        return self._excitation        
    @excitation.setter
    def excitation(self,newSignalObj):
        self._excitation = newSignalObj
        
    @property
    def samplingRate(self):
        return self.excitation._samplingRate

    @property
    def fftDegree(self):
        return self.excitation._fftDegree

    @property
    def timeLength(self):
        return self.excitation._timeLength

    @property
    def numSamples(self):
        return self.excitation._numSamples

    @property
    def freqMin(self):
        return self.excitation._freqMin

    @property
    def freqMax(self):
        return self.excitation._freqMax


     
class FRFMeasure(PlayRecMeasure):
    """
    Transferfunction object

    Properties(self) 	 	 (default),         meaning:
		- excitation:  	 	 (SignalObj), 	 	Signal information used to reproduce (playback);
		- samplingRate:      (44100), 	 	 	signal's sampling rate;
        - freqMin: 	 	 	 (20),              minimum frequency bandwidth limits;
        - freqMax: 	 	 	 (20000),           maximum frequency bandwidth limits;
        - numSamples:    	 (len(timeSignal)), number of samples will be 2**fftDeg. Used if domain is set to 'samples';
		- timeLen: 	 	 	 (numSamples/samplingRate),  time length of the recording. Used if domain is set to 'time';

    Properties(inherited): 	(default), 	 	 	meaning:
        - device: 	 	 	(system default),  	list of input and output devices;
        - inChannel:  	 	([1]), 	 	 	 	list of device's input channel used for recording;
        - outChannel: 	 	([1]), 	 	 	 	list of device's output channel used for playing/reproducing a signalObj
        - comment: 	 	 	('No comments.'), 	some commentary about the measurement;		
		
	Methods 	  	 	meaning:
		- run(): 	 	starts playing the excitation signal and recording during the excitation timeLen duration. At the end of recording calculates the transferfunction between recorded and reproduced signals;

    """
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        
    def run(self):
        """
        Starts reproducing the excitation signal and recording at the same time
        Divides the recorded signalObj by the excitation signalObj to generate a transferfunction
        Outputs the transferfunction signalObj
        """
        self.recording = super().run()
        self.transferfunction = self.recording/self.excitation
        return self.transferfunction