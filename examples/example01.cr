#orchestra
    sr = 44100
    nchnls = 2
    0dbfs = 1

    instrument Bass vol freq: pan  // freq is a Pitch parameter, it's automatically converted by cpspch
        env=madsr(0.01,0.6,0.1,0.1)  //notation is in functional form
        sig1=vco2(0.1,freq,8)
        sig=reson(sig1*0.0009,freq*2.2,freq/3)
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

    
    instrument piano vol freq: pan
        sig=pluck(ampdbfs(vol), freq, freq, 0, 1)
        outs(sig*pan,sig*(1-pan))
    endinstrument

#score
    tempo(100)
    
    Bass:
        //vol varies along the pattern from 1 to 10. pan from 0.2 0.9 and 0.9 0
        pattern=|4,16,'****************'| * /vol  1 10/ * /pan 0.2 0.9 0.9 0/
      
        notes=array(10) //creates an array/list of length 10
	notes[0]=/freq c6 e g a g e a d b g c7 d a6 g f f+/  // freq is a Pitch parameter
	notes[1]=/freq g6 a b d g- e- f d  b- g- d7 e g6 a b b+/
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
            patt[i]=pattern+notes[i]
            i+=1
        endwhile
 
	pat=patt[0]
        i=1
        while i<10 
	    pat+=patt[i]
            i+=1
        endwhile

	<<pat*10 - /freq g6 f e d c/ // the last 5 notes

    pad:
        l=100
        // vol = -5. Pan changes in the same note (glissable parameter)
        << |l,1,'*'|^7 + /vol -5/ + /freq c4 c5 g b c6 d c7/ + /pan 1 > 0/ //7 notes chord
        |< |l,4,'*__*'|  + /vol -1/ + /freq c3 c3+/  // bass movement toward the next chord
        << |l,1,'*'|^7 + /vol -5/ + /freq d4 d5  a  c6 d f d7/ + /pan 0 > 1/   // 'vol':[-19] == 'vol':'-19'
        |< |l,4,'*__*'|  + /vol -1/ + /freq d3 d3-/  // bass movement toward the next chord
        << |l,1,'*'|^7 + /vol -5/ + /freq c4 c5 g b c6 d c7/+/pan 1 > 0/
        |< |l,4,'*__*'|  + /vol -1/ + /freq c3 c3+/  // bass movement toward the next chord
        << |l,1,'*'|^7 + /vol -5/ + /freq d4 d5 a c6 d f d7/+/pan 0 > 1/
        |< |l,4,'*__*'|  + /vol -1/ + /freq d3 d3-/  // bass movement toward the next chord
        << |10,1,'*'|^7 + /vol -5 > -60/ + /freq c4 c5 g b c6 d c7/ +/pan 0.2 > 1/
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
            vol= '-' +str(random.randint(12,20))
            return '|1,16,"{}"| + /vol {}, freq {}, pan {}/'.format(pattern,vol,note,pan)
        enddefine

        for i=0 to 399
            << randomNote()
        endfor
        
#end
options = '-odac'
