#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1


#score
    tempo(120)
    times=16


#orchestra
  instrument Granular amp freq: grtab wintab dens gdur

      env=madsr(0.0001, 0.04 ,0.9,0.01) * amp
      outl=grain3(freq, 0, 0.04, 0, gdur, dens, 2000, grtab,   wintab,  0, 0)
      outr=grain3(freq, 0, 0.04, 0, gdur, dens, 2000, grtab,   wintab,  0, 0)

      <<env*outl, env*outr


  endinstrument

#score
      Granular:
          define any generateValues():
              import random

              gdur=0.1 + random.random()
              gdens=random.randint(200,900)
              return '/gdur {}, dens {}/'.format(gdur,gdens)
          enddefine

          ftgen(1, 0,16384,20,2,1)
          ftgen(2, 0 1024 10 1 0 .5 0 .33 0 .25 0 .2 0 .167)

          notes=/freq c7 e6 b f    a g a f    e c7 d a6    g a d7 g/
          pattern=|1,16,'*'*16| 
          pattern += /amp 0.01/ + /grtab 2/ + /wintab 1/ 
          pattern += notes 

          for i=1 to 4*times
              <<pattern + generateValues()
          endfor
#orchestra

  instrument Fm amp freq: car mod index

      t=ftgen(0,0,2048, 10, 1)
         
      env=linseg(0, 0.02, 1,p3-0.02, 0)
      sig=foscili(amp, freq, car, mod, index, t)

      <<env*sig,env*sig

  endinstrument

#score
        Fm:
          define string stacatto(v, g, s):
              return str(float(v)*float(s))
          enddefine

          define void transpose(list,semitones): #not python functions must be passed as parameters
              for i in range(1,len(list)):
                  list[i]=inter.execTranspose(list[i],semitones)
          enddefine

          define void reverse(list):
              p=list.pop(0)
              list.reverse()
              list.insert(0,p)
          enddefine

          notes=array(eval('2*2')) //testing the function eval

          notes[0]= /freq c5  b     a  a     e  d    /
          notes[1]= /freq d5  a     b  e     f  c    /
          notes[2]= /freq e5  g     a  g     f  e    /
          notes[3]= /freq f5  d     g  e     g  f    /
  
          pattern=|2,8,'***_*_**'| + /amp 0.3/ + /index 3/ + /mod 1/ 
          for n=0 to times-1
              pattern += notes[n%4] 
              reverse(notes[n%4])
              transpose(notes[n%4],4)
              <<silence(2)
              <<pattern * 'p3'::stacatto(1-(n+1)/(3*times))
          endfor
          t=getTime()
          var(0,t,'car',1,3)         
#orchestra

  instrument scanTable amp freq:

    pos=  ftgen(0, 0, 128, 10, 1);Initial Shape, sine wave range -1 to 1
    mass= ftgen(0, 0, 128, -7, 1, 128, 1) ;Masses(adj.), constant value 1
    stiff=ftgen(0, 0, 128, -7, 50, 64, 100, 64, 0) ;Stiffness; unipolar triangle range 0 to 100
    damp= ftgen(0, 0, 128, -7, 1, 128, 1) ;Damping; constant value 1
    vel=  ftgen(0, 0, 128, -7, 0, 128, 0) ;Initial Velocity; constant value 0

    env=adsr(0.1,0.3,0.5,0.01)
    a0=scantable(amp, freq, pos, mass, stiff, damp, vel)
    a1=oscil3(amp, freq, pos)
    a1=dcblock2(a1)
    <<a1*env, a1*env
  endinstrument

#score

  scanTable:

     define list generateChord(root,type): #0 major 1 minor 2 dominant 3 mb5
         root=root[0]
         if type==0 or type==2:
             third=inter.execTranspose(root,4)  #inter.execTranspose is a function defined in the interpreter
         else:
             third=inter.execTranspose(root,3)

         if type==3:
             fifth=inter.execTranspose(root,6)
         else:
             fifth=inter.execTranspose(root,7)

         if type==0:
             seventh=inter.execTranspose(root,11)
         else:
             seventh=inter.execTranspose(root,10)

         return ['list',[ ['string',root],['string',third],['string',fifth],['string', seventh]]] #types inside a list must be defined 
     enddefine

      pattern=|4,1,"*"|^4  + /amp 0.1/  //4 note chord in parallel with 2 notes bass (pattern * string)
      
      for i=0 to (times-1)/8
          <<pattern + 'freq':generateChord({a6},1)
          <<pattern + 'freq':generateChord({b6},3) 
          <<pattern + 'freq':generateChord({c7},0) 
          <<pattern + 'freq':generateChord({d7},1) 
          <<pattern + 'freq':generateChord({d7},1)
          <<pattern + 'freq':generateChord({c7},0)
          <<pattern + 'freq':generateChord({b6},3) 
          <<pattern + 'freq':generateChord({a6},1) 
      endfor

#orchestra


        opcode Oscillator, a, kk  ;testing opcode

              kamp, kcps      xin             ; read input parameters
              a1      vco2 kamp, kcps         ; sawtooth oscillator
              xout a1                 ; write output

        endop


  instrument additive amp1 amp2 amp3 amp4 amp5 amp6 freq: a1 d1 a2 d2 a3 d3 \
                                                          a4 d4 a5 d5 a6 d6

    env1=expseg(0.01, a1, 1, d1, 0.01)
    env2=expseg(0.01, a2, 1, d2, 0.01)
    env3=expseg(0.01, a3, 1, d3, 0.01)
    env4=expseg(0.01, a4, 1, d4, 0.01)
    env5=expseg(0.01, a5, 1, d5, 0.01)
    env6=expseg(0.01, a6, 1, d6, 0.01)

    s1=Oscillator(amp1,freq)
    s2=Oscillator(amp2,freq*2)
    s3=Oscillator(amp3,freq*3)
    s4=Oscillator(amp4,freq*4)
    s5=Oscillator(amp5,freq*5)
    s6=Oscillator(amp6,freq*6)

    out=env1*s1+env2*s2+env3*s3+env4*s4+env5*s5+env6*s6

    <<out
  endinstrument

#score

    additive:
    
        define number random(n):
            import random

            return random.randint(0,n)
        enddefine

        pattern=array(5)

        pattern[0]=|4,16,/freq c8_ d f_ g__  a e_ f d_ z_/|
        pattern[1]=|4,16,/freq c8 d f g  a e f d z_______/|
        pattern[2]=|4,16,/freq d8_ c g_ f__  e a_ d f_ z_/|
        pattern[3]=|4,16,/freq e8 f_ e_ g_ b   e_ g a_ g_ a/|
        pattern[4]=|4,16,/freq a8_ g a_ g__  e b_ g e_ f_/|
  
        preset =/amp1 1/ + /a1 0.001/ + /d1 0.4/
        preset +=/amp2 0.5/ + /a2 0.002/ + /d2 0.5/
    

        n=times/8

        for i=1 to 8
            <<pattern[random(4)] * n + preset
        endfor

        t=getTime()


        var(0,t/2,'amp4',0.01,0.05)
        var(t/2,t,'amp4',0.05,0.01)

#orchestra
  
  instrument mixer
      >>gl,gr
      >>fml,fmr
      >>sctl,sctr
      >>add

    vol=linseg(0,0.1,1,p3-2.1,1,2,0)
    vFm=1
    pFm=0.4
    vg=1
    pg=0.4 + oscil(0.2,20/p3)
    vsct=1
    psct=0.6
    vadd=0.4
    x=p3/8
    padd=linseg(0.1,x,0.9,x,0.1,x,0.9,x,0.1,x,0.9,x,0.1,x,0.9,x,0.5)

    a:mr=vFm*pFm*fmr+vg*pg*gr+vsct*psct*sctr+vadd*add*padd
    a:ml=vFm*(1-pFm)*fml+vg*(1-pg)*gl+vsct*(1-psct)*sctl+vadd*add*(1-padd)
    outs(mr*vol,ml*vol)

endinstrument

#score
        mixer:
            <<|times*4,1,'*'|

#patchboard
    mixer[0]<<Granular
    mixer[1]<<Fm
    mixer[2]<<scanTable
    mixer[3]<<additive

//#end additive mixer
//#end scanTable mixer
//#end Fm mixer
//#end(0,1)
#end 
options='-W -o example10.wav'
;options='  -odac'
;this file can't be rendered in real time
