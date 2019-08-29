/*
example 2
swing demo using the parameters 4 and 5 when creating a pattern
*/
#options
  -odac
  //-odac  -Ma
  //-Q hw:1
  //-+rtmidi=alsaseq -Q20 -odac

#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

instrument Bass vol freq pan
    tb=ftgen(0, 0, 16384, 10, 1)  // sine wave
    env=linseg(0, .02, 1, p3 - 0.04, 1, .02, 0)
    sig=buzz(ampdbfs(vol),cpspch(freq),8,tb)
    outs(env*sig*pan,env*sig*(1-pan))
endinstrument

#score
   //tempo(120)
   Bass:
        s='*_*'
        vol=-10 

        notes=[0]*4
        notes[0]={e5, e, a, g,   e,d,g,f}
        notes[1]={d5, e, d, g,   a,c,b,g}
        notes[2]={e5, e, f, a,   g,e,a,d}
        notes[3]={c5, d, a, e,   f,g,f,g}

        n=0
        while n<=10
            pattern1=|4,16,'freq':(notes[n%4]*2)|          + 'vol':[vol] + 'pan':[0]
            pattern2=|4,16,'freq':(notes[n%4]*2),s*8,n/10| + 'vol':[vol] + 'pan':[1] //with swing
            <<pattern1+pattern2
            n+=1
        endwhile
#end

