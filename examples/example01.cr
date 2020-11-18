#orchestra
    sr = 44100
    nchnls = 2
    0dbfs = 1

    instrument Bass vol freq: pan  reson table // freq is a Pitch parameter, it's automatically converted by cpspch
        env=linseg(0, .02, 1, p3 - 0.04, 1, .02, 0)  //notation is in functional form
        slavecps=line(freq*reson,p3,freq)
	a:nosync=init(0.0)

	master,sync=syncphasor(freq,nosync)
	slave,sync2=syncphasor(slavecps,sync)
	osc=tablei(slave,table,1)
	out  = osc * (1-master)
	sig=out*ampdbfs(vol)

        sigl,sigr=pan2(ampdbfs(vol)*sig,pan)
        outs(env*sigl,env*sigr)
    endinstrument

    instrument pad vol+ freq: pan+ // the parameters vol and pan are glissable
        vibf=rand(2)
        sig=wgbow(ampdbfs(vol),freq,3,0.2,vibf,0.1)
        ffreq=linseg(freq*2,0.8,freq*4,p3-0.2,freq*2)
        sig1=butterlp(sig,ffreq)
        sigl,sigr=pan2(sig1,pan)
        outs(sigl,sigr)
    endinstrument


//    opcode STKRhodey,a,ii.  //opcodes not declared in crhydm.py can be declared

    

     basehz = 261.625565
     spec_len=init(2^18)
     padsynth_1=ftgenonce(0, 0, spec_len, "padsynth", basehz, 10, 2, 1, 1,  1,0.7600046992, 0.6199994683, 0.9399998784, 0.4400023818, 0.0600003302, 0.8499968648, 0.0899999291, 0.8199964762, 0.3199984133, 0.9400014281, 0.3000001907, 0.120003365, 0.1799997687, 0.5200006366, 0.9300042987 )

    instrument piano vol freq: pan
        sig=pluck(ampdbfs(vol), freq, freq, 0, 1)
        outs(sig*pan,sig*(1-pan))
    endinstrument

  instrument synth vol freq:
     sig=poscil(ampdbfs(vol), freq*(sr/spec_len/basehz), padsynth_1, -1)
     sig=sig * linseg(0,0.02,1,p3-0.02,0)
     left, right=pan2(sig, 0.5)
     outs( left, right)
  endinstrument

#score
    tempo(100)
    ftgen(1, 0, 16385, 10,  1)

    Bass:
        //vol varies along the pattern from -5 to -2. pan from 0.2 0.9 and 0.9 0
        pattern=|4,16,'*_** _*_* *_*_ ** _*'| * /vol  -5 -2/ * /pan 0.2 0.9 0.9 0/ + /table 1/
      
        notes=array(10) //creates an array/list of length 10
	notes[0]=/freq c6 e g a g e a d b g c7 d a6 g f f+/  // freq is a Pitch parameter
	notes[1]=/freq g6 a b d g- e- f d  b- g- d' e g; a b b+/  // '=octave up, ;=octave down
	notes[2]=/freq d6 e g a- g e- a d  a f c7 e a6 g- f f+/
	notes[3]=/freq g6 a- b- d f- d- g d  b- g- e7 a g6 b a b+/
	notes[4]=/freq c6+ e- f b- g+ f a d  c g+ c7 e a6 f g f+/
	notes[5]=/freq f6 a+ b d g- e- f d  b- g- d7 e- g6 a- b- b+/
	notes[6]=/freq c6 d f g g+ f a d  b f c7 a a6 g g f+/
	notes[7]=/freq g6 a b- d f e f d  b g- d7 f e  g6 g b b+/
	notes[8]=/freq d6 e- g+ a- g e b d+  a f c7 d- a6 g+ f f+/
	notes[9]=/freq g6+ a+ b d- g- e- f d  b- g- d7 e+ g6 a b b+/

        patt=array(10)
        i=0
        while i<10   
            patt[i]=(pattern*2)+ (notes[i] - 12) // transpose down one octave
            i+=1
        endwhile
 
	pat=patt[0]
        i=1
        while i<10 
	    pat+=patt[i]
            i+=1
        endwhile

	<<pat*5 - /freq g6 f e d c/ // the last 5 notes
	t=getTime()
        var(0,t,'reson',5, 12)
    pad:
        l=100
        //vol = -6. Pan changes in the same note (glissable parameter)
        << |l,1,'*'|^7 + /vol -6/ + /freq c4 c5 g b c6 d c7/ + /pan 1 > 0/ //7 notes chord
        |< |l,4,'*__*'|  + /vol -1/ + /freq c3 c3+/  // bass movement toward the next chord
        << |l,1,'*'|^7 + /vol -6/ + /freq d4 d5  a  c6 d f d7/ + /pan 0 > 1/   // 'vol':[-19] == 'vol':'-19'
        |< |l,4,'*__*'|  + /vol -1/ + /freq d3 d3-/  // bass movement toward the next chord
        << |l,1,'*'|^7 + /vol -6/ + /freq c4 c5 g b c6 d c7/+/pan 1 > 0/
        |< |l,4,'*__*'|  + /vol -1/ + /freq c3 c3+/  // bass movement toward the next chord
        << |l,1,'*'|^7 + /vol -6/ + /freq d4 d5 a c6 d f d7/+/pan 0 > 1/
        |< |l,4,'*__*'|  + /vol -1/ + /freq d3 d3-/  // bass movement toward the next chord
        << |10,1,'*'|^7 + /vol -6 > -60/ + /freq c4 c5 g b c6 d c7/ +/pan 0.2 > 1/
        |< (|10,8,'********'|  + /freq c5.9 c5.8 c5.7 c5.6 c.5 c.3 c.1 c/) * /vol -1 > -10/ //microtonality 

    piano:

        define any randomNote():
            import random
          
            octave=str(random.randint(5,9))
            note=['a','b','c','d','e','f','g'][random.randint(0,6)] + octave
            pos=random.randint(0,50)
            pattern='________________'
            p=list(pattern)
            if pos<16:
                p[pos]='*'
            pattern=''.join(p)
            pan=str(random.random())
            vol= '-' +str(random.randint(15,20))
            return '|1,16,"{}"| + /vol {}, freq {}, pan {}/'.format(pattern,vol,note,pan)
        enddefine

        for i=0 to 399
            << randomNote()
        endfor
        
    synth:

         notes=[8.00, 8.02, 7.04, 8.05, 8.07, 8.09, 8.11, 9.00, 9.02 ]
	 <<silence(2)
	 for i=0 to 99
           n1=notes[random.randint(0,8)]
           n2=notes[random.randint(0,8)]
           n3=notes[random.randint(0,8)]
           n4=notes[random.randint(0,8)]
           p1=['*_*_*_*_','**_*__*_','*_**_*__','*_*_**__','*_*_*__*','*_*___**','xxxx*_xx','x*___xxx','xxx*_xxx','xxxxxxxx','xxxxxxxx','xxxxxxxx'][random.randint(0,11)]
           p2=['*_*_*_*_','**_*__*_','*_**_*__','*_*_**__','*_*_*__*','*_*___**','xxxx*_xx','x*___xxx','xxx*_xxx','xxxxxxxx','xxxxxxxx','xxxxxxxx'][random.randint(0,11)]
           <<|1,16,p1+p2| + 'freq':[n1, n2, n3, n4] + 'freq':[n1, n2, n3, n4] + /vol -12/
           <<|1,16,p2+p1| + 'freq':[n4, n3, n2, n1] + 'freq':[n4, n3, n2, n1]
           <<silence(2)
         endfor



#end
options = '-odac'
