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
    ffreq=linseg(cpspch(freq)*2,0.8,cpspch(freq)*4,p3-0.2,cpspch(freq)*2)
    sig1=butterlp(sig,ffreq)
    sl,sr=pan2(sig1,pan)
    outs(sl,sr)
  endinstrument

#score
    tempo(100)
    

    Bass:
        pattern=|4,16,'****************'| * 'vol':[ -12, '>', -10] * 'pan':[0, '>',1, 1,'>', 0]

	notes1='freq':{ c6, e, g, a, g, e, a, d,   b, g, c7, d, a6, g, f, f+}
	notes2='freq':{ g6, a, b, d, g-, e-, f, d, b-, g-, d7, e, g6, a, b, b+}
	notes3='freq':{ d6, e, g, a-, g, e-, a, d, a, f, c7, e, a6, g-, f, f+}
	notes4='freq':{ g6, a-, b-, d, f-, d-, g, d, b-, g-, e7, a, g6, b, a, b+}
	notes5='freq':{ c6+, e-, f, b-, g+, f, a, d, c, g+, c7, e, a6, f, g, f+}
	notes6='freq':{ f6, a+, b, d, g-, e-, f, d, b-, g-, d7, e-, g6, a-, b-, b+}
	notes7='freq':{ c6, d, f, g, g+, f, a, d, b, f, c7, a, a6, g, g, f+}
	notes8='freq':{ g6, a, b-, d, f, e, f, d, b, g-, d7,f, e, g6, g, b, b+}
	notes9='freq':{ d6, e-, g+, a-, g, e, b, d+, a, f, c7, d-, a6, g+, f, f+}
	notes10='freq':{ g6+, a+, b, d-, g-, e-, f, d, b-, g-, d7, e+, g6, a, b, b+}
    
        pattern1=pattern+notes1
        pattern2=pattern+notes2
        pattern3=pattern+notes3
        pattern4=pattern+notes4
        pattern5=pattern+notes5
        pattern6=pattern+notes6
        pattern7=pattern+notes7
        pattern8=pattern+notes8
        pattern9=pattern+notes9
        pattern10=pattern+notes10

	pat=pattern1
	pat+=pattern2
	pat+=pattern3
	pat+=pattern4
	pat+=pattern5
	pat+=pattern6
	pat+=pattern7
	pat+=pattern8
	pat+=pattern9
	pat+=pattern10

	<<pat*10

    pad:
        l=100
        << (|l,1,'*'|^7 + 'vol':[-19] + 'freq':{ c4, c5,  g, b, c6, d, c7}) + 'pan':[1,'>',0]
        << (|l,1,'*'|^7 + 'vol':[-19] + 'freq':{ d4, d5,  a, c6, d, f, d7}) + 'pan':[0,'>',1]
        << (|l,1,'*'|^7 + 'vol':[-19] + 'freq':{ c4, c5,  g, b, c6, d, c7}) + 'pan':[1,'>',0]
        << (|l,1,'*'|^7 + 'vol':[ -19] + 'freq':{ d4, d5,  a, c6, d, f, d7}) + 'pan':[0,'>',1]
#end

