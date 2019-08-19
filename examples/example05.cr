#options
  -odac
#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

instrument Drum vol freq pan
    env=adsr(0.01,0.2,0,0)
    a:sig=oscil(ampdbfs(vol),freq)
    outs(env*sig*pan,env*sig*(1-pan))
endinstrument

instrument Bass vol freq pan
tb=ftgen(0,0,16384, 10, 1)
    env=adsr(0.01,0.1,0.8,0.01)
    a:sig=buzz(ampdbfs(vol),cpspch(freq),8,tb)
    outs(env*sig*pan,env*sig*(1-pan))
endinstrument

#score
    Drum:
        'a'>'vol -5 freq 75'
	'b'>'vol -6 freq 65'
        'l'>'pan 0'
	'r'>'pan 1'

        pattern=|4,16,'xxxxxxaaxxxbbxaa'| + 'xxxxxxllxxxrrxll'

        << pattern * 8

    Bass: 
        pattern=|2,8,'__x**__*'| + 'vol':[ -10] 

	<< (((pattern + 'freq':{e5, e, a}) +  (pattern + 'freq':{g5, g, d}))  *2) + 'pan':[0]
	<< (((pattern + 'freq':{c5, d, f}) +  (pattern + 'freq':{d5, c, a4})) *2) + 'pan':[0.3]
	<< (((pattern + 'freq':{e5, e, a}) +  (pattern + 'freq':{g5, g, d}))  *2) + 'pan':[0.6]
	<< (((pattern + 'freq':{c5, d, f}) +  (pattern + 'freq':{d5, c, a4})) *2) + 'pan':[1]
#end

