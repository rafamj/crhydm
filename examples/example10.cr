#options
;  -odac
;this file can't be rendered in real time
-W

#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

#score
    tempo(120)
    times=8


#orchestra
  instrument Granular amp freq: grtab wintab dens gdur

      env=madsr(0.0001, 0.04 ,0.9,0.01) * amp
      outl=grain3(cpspch(freq), 0, 0.04, 0, gdur, dens, 2000, grtab,   wintab,  0, 0)
      outr=grain3(cpspch(freq), 0, 0.04, 0, gdur, dens, 2000, grtab,   wintab,  0, 0)

      <<env*outl, env*outr


  endinstrument

#score
      Granular:
          f1=ftgen( 0,16384,20,2,1)
          f2=ftgen( 0 1024 10 1 0 .5 0 .33 0 .25 0 .2 0 .167)

          notes=/freq c7 e6 b f    a g a f    e c7 d a6    g a d7 g/
          pattern=|1,16,'*'*16| * 4
          pattern += /amp 0.01/ + /grtab 2/ + /wintab 1/ + /gdur 0.9/ + /dens 2000/
          pattern += notes * 4

          <<pattern * times 


#orchestra

  instrument Fm amp freq: car mod index

      t=ftgen(0,0,2048, 10, 1)
         
      env=linseg(0, 0.02, 1,p3-0.02, 0)
      sig=foscili(amp, cpspch(freq), car, mod, index, t)

      <<env*sig,env*sig

  endinstrument

#score
        Fm:
          define void transpose(list,semitones,function): #not python functions must be passed as parameters
              for i in range(1,len(list)):
                  list[i]=function(list[i],semitones)
          enddefine

          define void reverse(list):
              p=list.pop(0)
              list.reverse()
              list.insert(0,p)
          enddefine

          notes=array(eval('2 * 2')) //testing the function eval

          notes[0]= /freq c5  b     a  a     e  d    /
          notes[1]= /freq d5  a     b  e     f  c    /
          notes[2]= /freq e5  g     a  g     f  e    /
          notes[3]= /freq f5  d     g  e     g  f    /
  
                     
          pattern=|2,8,'***_*_**'| + /amp 0.3/ + /index 3/
          for n=0 to times-1
              pattern += notes[n%4] 
              reverse(notes[n%4])
              transpose(notes[n%4],4,transposeNote) //transposeNote is a predefined function
              <<silence(2)
              <<pattern
          endfor
          t=getTime()
          var(0,t,'car',1,3)         
          var(0,t,'mod',1,2)

#orchestra
  
  instrument mixer
      >>gl,gr
      >>fml,fmr


    vFm=1
    pFm=0.5
    vg=1
    pg=0.4 + oscil(0.2,20/p3)

    mr=vFm*pFm*fmr+vg*pg*gr
    ml=vFm*(1-pFm)*fml+vg*(1-pg)*gl
    outs(mr,ml)

endinstrument

#score
        mixer:
            <<|times*4,1,'*'|

#patchboard
    mixer[0]<<Granular
    mixer[1]<<Fm


//#end Fm mixer
//#end(0,4)
#end


