/*
   example03
*/
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

  t1=ftgen(0,0,0,1,"drum.wav",0,0,0)
  instrument Drum amp freq
    sig=loscil(ampdbfs(amp),freq,t1,1,1)
    env=linseg(0, .02, 1, .02, 0)
    outs(sig*env,sig*env)
  endinstrument

#score
   tempo(120)
   t=getTime()
   n=10
  
  Synth:
    adsr1=' a 0.01 d 0.09 s 0.6 r 0.01 '
    adsr2=' a 0.06 d 0.04 s 0.4 r 0.02 '

    'a' > adsr1  
    'b' > adsr2
 
     //pattern: duration=4, parts=16, pattern='abaabaaaaabaaaaa'

    p1=|4,16,'abaabaaaaabaaaaa'| + 'note':{c6, d, f, e,   f+, d, a, g,   g-, a, b, a,  g, f,e, d} + 'amp':[-10]

    << p1*n * 'cutoff':[80,300] * 'res':[0.8,0.99] * 'pan':[0,1]

  Drum:
    'a' > 'freq 1 amp -13'
    'b' > 'freq 1.3 amp -13'
    'c' > 'amp +=2'
    <<(|4,16,'axba xabx axxa xxbb'| + 'xxcx xxcx xxxx xxcx') * n
#end
//#end Synth
//#end(0,4)Drum
options='  -odac'
  //-odac  -Ma
  //-Q hw:1
  //-+rtmidi=alsaseq -Q20 -odac

