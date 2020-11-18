#orchestra
  //sr = 44100
  //nchnls = 2
  //0dbfs = 1
  ksmps=32

instrument MidiOut status chan data1 data2
        midiout(status,chan,data1,data2)
endinstrument

instrument Midi chan note% vel  //% -> midi note
        noteondur(chan,note,vel,p3)
endinstrument

instrument Midi1=Midi(chan=1)
instrument Midi2=Midi(chan=2)
instrument Midi10=Midi(chan=10)

#score
    tempo(120)
    
    MidiOut:
    <<'0  1 192 1  40 0' 
    <<'0  1 192 2  94 0'
    <<'0  1 192 10 10  0'
    
    Midi1:
    <<silence(0.1)
    pattern1=|20,16,'*_** _*_* *_*_ ** _*'| + /vel 120/
    pattern2=|20,16,'*_** _*_* *_*_ ** _*'| 

    pattern1 +=/note c7 d e f   e^ f c d av g/  - 12
    pattern2 +=/note b6 d^ e g   e^ f c d av f/  - 12
    pattern=pattern1+ pattern2

    <<pattern * 2 

    pattern1 +=/note d7 c e fi d   e^ c f d gv a/  - 12
    pattern2 +=/note e7 d e g   f^ e d c fv a/  - 12
    pattern=pattern1+ pattern2

    <<pattern * 2 

    pattern1 +=/note f7 e d c   f e^ c d av g/  - 12
    pattern2 +=/note d7 e g a   e^ f c d av f/  - 12
    pattern=pattern1+ pattern2

    <<pattern * 2 

    pattern1 +=/note c7 d e f   e^ f c d av g/  - 12
    pattern2 +=/note b6 d^ e g   e^ f c d av f/  - 12
    pattern=pattern1+ pattern2

    <<pattern * 2 


    Midi2:
    <<silence(0.1)
       pattern1=|20,2,'**'|^4
       pattern2=|20,2,'**'|^4
       notes1=/note  c5 c^ g e^     dvv d^ a f^/
       notes2=/note  e5 d^ g e^     dvv d^ a f^/
       vol=/vel 127 /
       pattern1 +=notes1 + vol
       pattern2 +=notes2
       <<(pattern1 + pattern2)  * 8  


    
    Midi10:
    <<silence(0.1)
        'a'>'note 50'
        'b'>'note 48'
        pattern=|4,16,'bxaa'*4|  + 'vel':[110]
	<<silence(100)
        <<pattern*25
	<<silence(100)
        <<pattern*4


#end  

options='-+rtmidi=alsaseq -Q128 -odac'
  //-odac
  //-odac  -Ma
  //-Q hw:1

