#orchestra
  //sr = 44100
  //nchnls = 2
  //0dbfs = 1
  ksmps=32

instrument MidiOut status chan data1 data2
        midiout(status,chan,data1,data2)
endinstrument

instrument Midi chan note vel
        midion(chan,note,vel)
endinstrument

instrument Midi1=Midi
instrument Midi2=Midi
instrument Midi3=Midi
instrument Midi4=Midi
instrument Midi10=Midi

#score
    tempo(120)
    
    MidiOut:
    //<<'0 1 192 1 20 0'
    //<<'0 1 192 2 120 0'
    //<<'0 1 192 3 20 10'
    //<<'0 1 192 4 20 30'
    //<<'0 1 192 10 10 0'
    
    Midi1:
        pattern=|4,16,'****************'| + 'chan':[ 1] + 'vel':[100]
        notes='note':{{ c5, d, e, a,     f, g, b, d6,        c, a5, g, e,      a, g, d, c}}  

        <<(pattern+notes)*10

    Midi2:
        pattern=|4,4,'****'| + 'chan':[2] + 'vel':[100]
        notes='note':[40, 44, 46, 44 ]    
        <<(pattern+notes)*10
    Midi3:
        pattern=|4,8,'x*x*x*x*'| + 'chan':[3] + 'vel':[100]
        notes='note':[50, 54, 56, 54 ]    
        <<(pattern+notes)*10
    Midi4:
        pattern=|4,1,'*'|^4 + 'chan':[ 4] + 'vel':[ 100]
        notes='note':[ 60, 64, 66, 70 ]    
        <<(pattern+notes)*10
    Midi10:
        'a'>'note 50'
        'b'>'note 55'
        pattern=|4,16,'axxbaxabxxbaxxab'| + 'chan':[ 10] + 'vel':[100]
        <<pattern*10


#end

options='-+rtmidi=alsaseq -Q20 -odac'
  //-odac
  //-odac  -Ma
  //-Q hw:1

