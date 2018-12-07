/*
  zak system with patchboard
*/
#options
-odac
//-odac -Ma --midi-key-cps=4 --midi-velocity-amp=5
;aconnect -li para localizar el port de Rosegarden
#orchestra
sr = 44100
nchnls = 2
0dbfs = 1

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

instrument mixer vFm+ pFm+ vWave+ pWave+ vEcho+ pEcho+
  >>fml,fmr
  >>wl,wr
  >>sl,sr

    mr=vFm*fmr*pFm+vWave*wr*pWave+vEcho*pEcho*sl
    ml=vFm*fml*(1-pFm)+wl*vWave*(1-pWave)+vEcho*(1-pEcho)*sr
    outs(mr,ml)

    <<mr,ml
endinstrument

instrument echo rvt lpt
  >>ls,rs
  els=comb(ls,rvt,lpt)
  ers=comb(rs,rvt,lpt)
  <<els,ers
endinstrument

#patchboard
   mixer[0]>>echo[0] //output of mixer connected to input of echo

   mixer[0]<<Fm  //it's Fm[0] by default
   mixer[1]<<wave
   mixer[2]<<echo

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
    <<|Fm.t2-Fm.t1,1,'*'| + 'pFm':[0,'>',1] + 'vFm':[1] + 'pWave':[1,'>',0] + 'vWave':[0.1] + 'vEcho':[0.5] + 'pEcho':[0,'>',1]
    <<|1,1,'*'| + 'vFm':[1,'>',0 ]+ 'vWave':[0.1,'>',0] + 'vEcho':[0.5,'>',0]
  echo:
    <<|Fm.t2-Fm.t1,1,'*'| + 'rvt':[2] + 'lpt':[0.3]  
    <<|1,1,'*'|
#end

