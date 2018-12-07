/*
   example03
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
  a=init(10)
 
  instrument Synth amp note cutoff res a d s r pan
    env=adsr(a,d,s,r)   
    vco=vco2 (ampdbfs(amp), cpspch(note))
    sig=moogladder (vco, cutoff, res)
    outs(env*sig*pan , env*sig*(1-pan))
  endinstrument

  instrument Drum amp freq
    t1=ftgen(0,0,0,1,"drum.wav",0,0,0)

    sig=loscil(ampdbfs(amp),freq,t1,1,1)
    outs(sig,sig)
  endinstrument

#score
   tempo(120)
   t=getTime()
   n=10
  
  Synth:
    adsr=' a 0.001 d 0.09 s 0.6 r 0.01 '

    'a'> adsr
 
//pattern: duration=4, parts=16, pattern='aaaaaaaaaaaaaaaa'

  p1=|4,16,'a'*16| + 'note':{c6, d, f, e,   f+, d, a, g,   g-, a, b, a,  g, f,e, d} + 'amp':[-10]

  << p1*n * 'cutoff':[80,300] * 'res':[0.8,0.99] * 'pan':[0,1]

  Drum:
  'a' > 'freq 1'
  'b' > 'freq 1.3'
  <<|4,16,'axbaxabxaxxaxxbb'|*n + 'vol':[-13] 
#end

