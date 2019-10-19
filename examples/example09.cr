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

rename 1 Synth amp note fqc rez tabl1 pan

#score
ftgen(1, 0, 1024, 10, 1)
ftgen(2, 0,   256,   7,  -1, 128, -1,   0,  1, 128,  1)
ftgen(3, 0,  256,   7,   1, 256, -1)
ftgen(4, 0,   256,   7,  -1, 128,  1, 128, -1)
ftgen(5, 0,   256,   7,   1,  64,  1,   0, -1,  192, -1)
ftgen(6, 0,  8192,   7,   0, 2048,  0,   0, -1, 2048, -1, 0, 1, 2048, 1, 0, 0, 2048, 0)

; Distortion Table
ftgen(7, 0, 1024,   8, -.8, 42, -.78,  400, -.7, 140, .7,  400, .78, 42, .8)

    tempo(120)
    Drum:
        'a'>'vol 0.4 freq 80'
	'b'>'vol 0.5 freq 65'
        'l'>'pan 0.2'
	'r'>'pan 0.8'

        pattern=|4,16,'xxxxxxaaxxxbbxaa'| + 'xxxxxxllxxxrrxll'

        <<pattern * 16

    Synth:
        pattern=|4,16,'*_____xx*____xxx'| + 'amp':[0.1] + 'rez':[30] + 'tabl1':[3] + 'fqc':[90]
	pattern1 = pattern + 'note':{c7, d}  + /tabl1 1/
	pattern2 = pattern + 'note':{e, d}   + /tabl1 2/
	pattern3 = pattern + 'note':{d, c} + /tabl1 3/
	pattern4 = pattern + 'note':{d, e} + /tabl1 4/
	pattern5 = pattern + 'note':{e, f} + /tabl1 5/
	pattern6 = pattern + 'note':{f, e} + /tabl1 6/
	pattern7 = pattern + 'note':{e, d} + /tabl1 7/
	pattern8 = pattern + 'note':{d, f} + /tabl1 4/
	pattern9 = pattern + 'note':{e, c} + /tabl1 3/
	pattern10 = pattern + 'note':{f, c} + /tabl1 1/

    
	<<pattern1+pattern2+pattern3+pattern4+pattern5+pattern6+pattern7+pattern8+pattern9+pattern10
	<<pattern1+pattern3+pattern10+pattern1+pattern2+pattern3+pattern7+pattern5+pattern3+pattern2
	<<pattern1+pattern6+pattern3+pattern9+pattern5+pattern6+pattern3+pattern5+pattern2+pattern1
        t=getTime()

        var(0,t,'rez',10,90) 
        var(0,60,'amp',0.1,0.005)
        var(60,t,'amp',0.1,0.01)
        put(0,'pan',[0.5])
        put(t/2,'pan',[0,1,0,1,0.5])
#end 
options='  -odac'
