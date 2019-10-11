/*
  zak system
*/
#orchestra
sr = 44100
nchnls = 2
0dbfs = 1
reserveZak(10,10)

instrument Fm CarFreq
  FeedbackAmountEnv=linseg(0, 2, 0.2, 0.1, 0.3, 0.8, 0.2, 1.5, 0)
  AmpEnv=madsr(0.6,0.1,0.9,0.01)
  Phase1=phasor(cpspch(CarFreq))
  Phase2=phasor(cpspch(CarFreq)*2)
  Carrier1=0 ; init for feedback
  Carrier2=0 ; init for feedback
  a:Carrier1=tablei(Phase1+(Carrier1*FeedbackAmountEnv), 1, 1, 0, 1)
  a:Carrier2=tablei(Phase2+(Carrier2*FeedbackAmountEnv), 1, 1, 0, 1)
  Carrier=(Carrier1+Carrier2)/2
  <<Carrier*AmpEnv, Carrier*AmpEnv
endinstrument

instrument wave
    sigl,sigr=diskin2('loop1.wav')
    <<sigl,sigr
endinstrument

instrument mixer waveZakl waveZakr
//the volumes and pans are defined by a linseg of duration p3
  vFm=linseg(1,p3-5,1,5,0)
  pFm=linseg(0,p3,1)
  vWave=linseg(0.1,p3-5,0.1,5,0)
  pWave=linseg(1,p3,0)
  vEcho=linseg(0.5,p3-5,0.5,5,0)
  pEcho=linseg(0,p3,1)
  genVol=linseg(1,p3-5,1,5,0)


  >>fml,fmr
  waveZakl>>wl
  waveZakr>>wr
  echo[0]>>sl,sr

    mr=vFm*fmr*pFm+vWave*wr*pWave+vEcho*pEcho*sl
    ml=vFm*fml*(1-pFm)+wl*vWave*(1-pWave)+vEcho*(1-pEcho)*sr
    outs(mr,ml)

    <<mr,ml
endinstrument

instrument echo rvt lpt
  mixer[0]>>ls,rs
  els=comb(ls,rvt,lpt)
  ers=comb(rs,rvt,lpt)
  <<els,ers
endinstrument

#patchboard
   mixer[0]<<Fm  //it's Fm[0] by default

#score
  f1=ftgen(0,1024,10,1)
  tempo(120)

  Fm:
    pattern1=|4,16,'****************'|
    notes1='CarFreq':{c7, d, a, e, b, f, b-, e,   d-, c, a6, e, d, e, g, b}
    notes2='CarFreq':{c5, e, d, e, f, g, b, f,    f, c+, d6, g, a, e, f, b}
    notes3='CarFreq':{c6, d, g, a, b, g, a, f,   d, e, b6, d, e, f, g, a}
    notes4='CarFreq':{d6, d, f, a, a-, g, g, f,   e, d, e, b6, d,  f, e, g }
    t1=getTime()
    <<((pattern1 + notes1) + (pattern1 + notes2) + (pattern1 + notes3) + (pattern1 + notes4))* 8
    t2=getTime()

  wave:
    <<|(Fm.t2-Fm.t1)/12,1,'*'| * 12
  mixer:
    <<|Fm.t2-Fm.t1+10,1,'*'|  + 'waveZakl':[getZakOut('wave',0)[0]] + 'waveZakr':[getZakOut('wave',0)[1]]
  echo:
    <<|Fm.t2-Fm.t1+10,1,'*'| + 'rvt':[2] + 'lpt':[0.3]  
#end

options='-odac'
//-odac -Ma --midi-key-cps=4 --midi-velocity-amp=5
;aconnect -li para localizar el port de Rosegarden
