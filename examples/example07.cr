#options
  -odac
  //-odac  -Ma

#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

  instrument Bass vol freq pan
    env=madsr(0.01,0.8,0.1,0.1)
    fre=cpspch(freq)
    sig1=vco2(0.1,fre,8)
    sig=reson(sig1*0.0005,fre*1.1,fre/3)
    sl,sr=pan2(ampdbfs(vol)*sig,pan)
    outs(env*sl,env*sr)
  endinstrument

  instrument pad vol freq pan+
    vibf=rand(2)
    sig=wgbow(ampdbfs(vol),cpspch(freq),3,0.2,vibf,0.1)
    ffreq=linseg(cpspch(freq)*3,0.8,cpspch(freq)*4,p3-0.2,cpspch(freq)*2)
    sig=butterlp(sig,ffreq)
    sl,sr=pan2(sig,pan)
    outs(sl,sr)
  endinstrument

  instrument synth freq Amp1 Type1 PW1 Oct1 Tune1 Amp2 Type2 PW2 Oct2 Tune2 CF FA FD FS FR Res AA AD AS AR

    CPS=cpspch(freq) ;convert from note number to cps
    Oct1=octave(Oct1) ;convert from octave displacement to multiplier
    Tune1=cent(Tune1)   ;convert from cents displacement to multiplier
    Oct2=octave(Oct2)
    Tune2=cent(Tune2)

;oscillator 1
;if type is sawtooth or square...
    if Type1==1||Type1==2 then
 ;...derive vco2 'mode' from waveform type
        Mode1=(Type1==1?0:2)
        Sig1=vco2(ampdbfs(Amp1),CPS*Oct1*Tune1,Mode1,PW1);VCO audio oscillator
    else                                   ;otherwise...
         Sig1=noise(ampdbfs(Amp1), 0.5)              ;...generate white noise
    endif

;oscillator 2 (identical in design to oscillator 1)
    if Type2==1||Type2==2 then
        Mode2=(Type2==1?0:2)
        Sig2=vco2(ampdbfs(Amp2),CPS*Oct2*Tune2,Mode2,PW2)
    else
      Sig2=noise(ampdbfs(Amp2),0.5)
    endif

;mix oscillators
    Mix=sum(Sig1,Sig2)
;lowpass filter
    FiltEnv=expsegr(0.0001,FA,CPS*CF,FD,CPS*CF*FS,FR,0.0001)
    Out=moogladder(Mix, FiltEnv, Res)

;amplitude envelope
    AmpEnv=expsegr(0.0001,AA,1,AD,AS,AR,0.0001)
    Out=(Out*AmpEnv)
    outs(Out,Out)

  endinstrument

#score
    tempo(100)
    

    Bass:
        pattern=|4,16,'****************'| * 'vol':[-12, '>' ,-10] * 'pan':[0, '>', 1, 1,'>', 0]

	notes1='freq':{ c6, e, g, a, g,  f, e, a, d, b, g, c7, d,  d-, a6, g, f, d+}
	notes2='freq':{ g6, a, b, d, g-, e-, f, d, b-, g-, d7, e,  f, g6, a, g, b+}
	notes3='freq':{ d6, e, g, a-, g, e-, a, d, a, f, c7, e, a6, g-, f, f+}
	notes4='freq':{ g6, a-, b-,  b, d, f-, d-, g, d, b-, g-, e7, a, g6, b, g, b+}
	notes5='freq':{ c6+, e-, f, b-, g+, f, a, d, c, g+, c7, e, a6, f, g, a+}
	notes6='freq':{ f6, a+, b, d, g-, e-, f, d, b-, g-, d7, e-, g6, a-, e-, b+}
	notes7='freq':{ c6, d, f, g, g+, f, a, d, b, f, c7, a, a6, g, b, f+}
	notes8='freq':{ g6, a, b-, d, f, e, f, d, b, g-, d7, f, e, g6, g, f, b+}
	notes9='freq':{ d6, e-, g+, a-, g, e, b, d+, a, f, c7, d-, a6, g+, g, f+}
	notes10='freq':{ g6+, a+, b, d-, g-, e-, f, d, b-, g-, d7, e+, g6, a, g, b+}
    
        pat=pattern+notes1
        pat+=pattern+notes2
        pat+=pattern+notes3
        pat+=pattern+notes4
        pat+=pattern+notes5
        pat+=pattern+notes6
        pat+=pattern+notes7
        pat+=pattern+notes8
        pat+=pattern+notes9
        pat+=(pattern+notes10)  

	<<pat*10
	<<(pattern+notes10)  * 'vol':[-10, '>', -60]

    pad:
        l=100
        << |l,1,'*'|^7 + 'vol':[-19] + 'freq':{ c4, c5,  e, g, c6, g, c7} +'pan':[1, '>', 0]
        << (|l,1,'*'|^7 + 'vol':[-19] + 'freq':{ d4, d5,  f, a, d6, a, d7}) + 'pan':[0,'>',1]
        << (|l,1,'*'|^7 + 'vol':[-19] + 'freq':{ c4, c5,  e, g, c6, g, c7}) + 'pan':[ 1,'>',0]
        << (|l,1,'*'|^7 + 'vol':[-19] + 'freq':{ d4, d5,  f, a, d6, a, d7}) + 'pan':[0,'>',1]

    synth:
     preset ='Amp1':[-15] + 'Type1':[1] + 'PW1':[0.5] + 'Tune1':[1]+'Oct1':[1] + 'FA':[0.1]+ 'FD':[0.1]+'FS':[0.5]+'FR':[0.1]+'AA':[0.01]+'AD':[0.2]+ 'AS':[0.5]+ 'AR':[0.01]+ 'Res':[0.5]+ 'CF':[5]
     preset+='Amp2':[-15] +  'Type2':[2]+ 'PW2':[0.3]+'Tune2':[1]+ 'Oct2':[2]
     pattern1=|4,8,'*_*___*_'| + 'freq':{ c7, e, g }
     pattern2=|4,8,'***_*_*_'| + 'freq':{ d7, f, e, c, g }
     pattern3=|4,8,'*__*__*_'| + 'freq':{ c7, e, g }
     pattern4=|4,8,'**_**_*_'| + 'freq':{ d7, f, e, c, g }
     pattern5=|4,8,'_*_**_*_'| + 'freq':{ c7, e, a, g }
     pattern6=|4,8,'**_**_*_'| + 'freq':{ d7, f, e, c, g }
     pattern7=|4,8,'**_**_*_'| + 'freq':{ c7, g, e, a, g }
     pattern8=|4,8,'**_****_'| + 'freq':{ d7, f, g, e, c, g }
     silence=|4,1,'x'|
     pattern10=pattern1+pattern2 + preset
     pattern11=pattern3+pattern4 + preset +  'AA':[0.01]
     pattern12=pattern5+pattern6 + preset +  'AA':[0.01]+ 'Res':[0.6]
     pattern13=pattern1+pattern7 + preset +  'AA':[0.01]+ 'Res':[0.6]
     pattern14=pattern2+pattern8 + preset +  'AA':[0.01]+ 'Res':[0.6]
     pattern15=pattern4+pattern3 + preset +  'AA':[0.01]+ 'Res':[0.6]
     pattern16=pattern3+pattern7 + pattern6 + preset + 'AA':[0.01]+'FA':[0.01]+'Res':[0.6]
     pattern17=pattern6+pattern2 + pattern5 + preset +  'AA':[0.01]+ 'Res':[0.6]
     << (pattern10 + silence) *  4 * 'CF':[ 2, '>', 6, 6,'>',2] 
     << (pattern11 + silence) *  4 * 'CF':[ 2,'>', 6, 6,'>',2]
     << (pattern12 + silence) *  4 * 'CF':[ 2,'>', 6, 6,'>',2]
     << silence * 4
     << (pattern13 + silence) *  4 * 'CF':[ 2,'>', 6, 6,'>',2] * 'Res':[0.6,'>',0.9]
     << (pattern14 + silence) *  4 * 'CF':[ 2,'>', 6, 6,'>',2] * 'Res':[0.6,'>',0.9]
     << (pattern15 + silence) *  4 * 'CF':[ 2,'>', 6, 6,'>',2] * 'Res':[0.6,'>',0.9]
     << silence * 4
     << pattern16  *  4 * 'CF':[ 2,'>', 6, 6,'>',2] * 'Res':[0.6,'>',0.9] * 'FS':[ 0.3, '>', 0.9]
     << pattern17  *  3 * 'CF':[ 2,'>', 6, 6,'>',2] * 'Res':[0.6,'>',0.9] * 'FS':[0.3, '>', 0.9] * 'Amp1':[ -19, '>', -90]
#end

