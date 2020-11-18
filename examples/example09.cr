#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

  instrument Drum vol freq pan
    env=adsr(0.005,0.1,0,0)
    a:sig=oscil(vol,freq)
    outs(env*sig*pan,env*sig*(1-pan))
  endinstrument


//instr usage: Must be followed by rename
instr 1   ; Table Based Rezzy Synth

idur   = p3
iamp   = p4
ifqc   = cpspch(p5)
irez   = p7
itabl1 = p8
ipan   = p9

; Amplitude envelope
kaenv  linseg 0, .01, 1, p3-.02, 1, .01, 0

; Frequency Sweep
kfco linseg .1*p6, .5*p3, p6, .5*p3, .1*p6

; This relationship attempts to separate Freq from Res.
ka1 = 100/irez/sqrt(kfco)-1
ka2 = 1000/kfco

; Initialize Yn-1 & Yn-2 to zero
aynm1 init 0
aynm2 init 0

; Oscillator
  axn oscil iamp, ifqc, itabl1

; Replace the differential eq. with a difference eq.
  ayn = ((ka1+2*ka2)*aynm1-ka2*aynm2+axn)/(1+ka1+ka2)
  aynm2 = aynm1
  aynm1 = ayn

; Amp envelope and output
  aout = ayn * kaenv
  outs ipan*aout,(1-ipan)*aout
endin

rename 1 Synth amp note: fqc rez tabl1 pan

 tabx=ftgen(0,0,4096,10,  1,0.6,0.3,0.2,0.1)
 taby=ftgen(0,0,4096,10,  1,0.3,0.2,0.1)

  instrument pad vol+ freq: init

    if init==0 igoto end

    k:cx=lfo(0.25,freq/9000)+lfo(0.2,freq/10000)+oscil(0.001,0.1)
    k:cy=lfo(0.2,freq/6000)+lfo(0.15,freq/7000)+lfo(0.001,0.2)
    rx=lfo(0.5,freq/5000)+lfo(0.02,0.05)
    ry=lfo(0.2,freq/7500)+lfo(0.05,0.01)
      sig1=wterrain(ampdbfs(vol),freq,cy,cx,rx,ry,tabx,taby)
      sig2=wterrain(ampdbfs(vol),freq,cx,cy,ry,rx,tabx,taby)
      sig1=0.2*dcblock(sig1)
      sig2=0.2*dcblock(sig2)
      outs(sig1,sig2)
    end:
  endinstrument


#score
ftgen(1, 0, 1024, 10, 1)
ftgen(2, 0,   256,   7,  -1, 128, -1,   0,  1, 128,  1)
ftgen(3, 0,  256,   7,   1, 256, -1)
ftgen(4, 0,   256,   7,  -1, 128,  1, 128, -1)
ftgen(5, 0,   256,   7,   1,  64,  1,   0, -1,  192, -1)
ftgen(6, 0,  8192,   7,   0, 2048,  0,   0, -1, 2048, -1, 0, 1, 2048, 1, 0, 0, 2048, 0)

; Distortion Table
ftgen(7, 0, 1024,   8, -.8, 42, -.78,  400, -.7, 140, .7,  400, .78, 42, .8)


    Drum:
        'a'>'vol 0.4 freq 80'
        'b'>'vol 0.5 freq 65'
        'l'>'pan 0.2'
        'r'>'pan 0.8'

        pattern=|4,16,'xxxxxxaaxxxbbxaa'| + 'xxxxxxllxxxrrxll'
        <<silence(30) 
        <<(pattern + silence(26)) * 10



    pad:
      pattern=|30,2,'**'|^4
      notes=/freq g6 c7 e a      a6 d7 f b a/
      vol=/vol -25 /
      pattern +=notes + vol
      <<pattern + /init 1 1 1 1 0/ 
      <<pattern * 10
      <<(pattern + notes) + /vol -25 > -30 . . . -30 > -60/

    Synth:
      
      <<silence(30)
      <<|30,16,/note g6_________ a b____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note d_________ b a____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note g_________ a d____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note a_________ g a____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note g_________ g a____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note g_________ b a____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note d_________ a b____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note g_________ d a____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note a7_________ a g____/| +  'tabl1':[random.randint(1,6)]
      <<|30,16,/note g_________ a g____/| +  'tabl1':[random.randint(1,6)]

        t=getTime()

        var(0,t,'rez',10, 100)
        var(t/2,t,'amp',0.07,0.01)
        var(0,t,'fqc',10,100)

        put(0,'pan',[0.4])
        put(0,'amp',[0.07])
        put(t/2,'pan',[0,1,0,1,0.6])

#end
options='-odac'

