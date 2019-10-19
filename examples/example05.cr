#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

  instrument drum vol freq
    Tanh=ftgen(0,0,257,"tanh",-1,1,0)

      dur=min(0.11,p3)
      env1=expon(1,dur,0.001)
      fr1=expon(freq,dur,freq/4)
      sig1=oscil(1,fr1)
      Amt=line(0,dur,0.5)
      sig2=distort(sig1, Amt, Tanh)
      sig=sig2*env1  * ampdbfs(vol)
      <<sig
  endinstrument

  instrument bass vol freq:
      Tanh=ftgen(0,0,257,"tanh",-2,2,0)

      env1=linseg(0,0.1,1,p3-0.1,0)
      sig1=oscil(1,freq)
      sig2=oscil(1,freq*2.1)
      Amt1=line(1,p3,0.5)
      sig1=distort(sig1, Amt1, Tanh)
      Amt2=line(0,p3,0.5)
      sig2=distort(sig2, Amt2, Tanh)
      sig=(sig1+sig2*0.5)*env1  * ampdbfs(vol)
      <<sig

  endinstrument

  instrument pad vol freq: car mod ndx
      sine=ftgen(0, 0, 16384, 10, 1)
      env=linseg(0,0.1,1,p3-0.2,1,0.1,0)    
      nd=linseg(0,p3/2,ndx,p3/2,0)
      v1=vibr(0.1,1,sine)
      v2=vibr(0.2,0.6,sine)
      nd=nd+v1+v2
      sig=foscil(ampdbfs(vol),freq,car,mod,nd,sine)
            
      <<sig*env

  endinstrument

  instrument mixer vol drp bp

  drum>>drum
  bass>>bass
  pad>>pad
 
  ph=phasor(1/p3)

  v=table(ph,vol,1)
  drump=table(ph,drp,1)
  bassp=table(ph,bp,1)
  padp=0.5


  druml,drumr=pan2(drum,drump)
  bassl,bassr=pan2(bass,bassp)
  padl,padr=pan2(pad,padp)

  sigl=druml+bassl+padl
  sigr=drumr+bassr+padr

  outs(sigl*v,sigr*v)

  endinstrument

#score
        tempo(120)
    pad:
        notes1= /freq c5 g c6 g/
        notes2= /freq d5 a d6 a/
        notes3= /freq c5 a c6 g/
        notes4= /freq d5 b d6 a/
        pattern=|15,1,'*'|^4   + /vol -43/  + /car 2, mod 2, ndx 4/

        <<pattern *2 + (notes1 + notes2)
        |<|20,8,'x**_____'| + |10,1,'_'|+/freq d7 e/ +  /car 2, mod 1, ndx 4/  
        <<pattern *2 + (notes1 + notes2)
        |<|20,8,'x**_____'| + |10,1,'_'|+/freq e7 d/ +  /car 2, mod 2, ndx 4/  

        <<pattern *2 + (notes2 + notes1)
        |<|20,8,'x**__*__'| + |10,1,'_'|+/freq e7 d f / +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes2 + notes1)
        |<|20,8,'x**__*__'| + |10,1,'_'|+/freq d7 e f / +  /car 2, mod 2, ndx 4/ 

        <<pattern *2 + (notes1 + notes2)
        |<|20,8,'x*__*___'| + |10,1,'_'|+/freq d7 e / +  /car 2, mod 1, ndx 4/  
        <<pattern *2 + (notes1 + notes2)
        |<|20,8,'x*___*__'| + |10,1,'_'|+/freq e7 d / +  /car 2, mod 2, ndx 4/  

        <<pattern *2 + (notes2 + notes1)
        |<|20,8,'x**__**_'| + |10,1,'_'|+/freq e7 d f g/ +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes2 + notes1)
        |<|20,8,'x**__*_*'| + |10,1,'_'|+/freq d7 e f a/ +  /car 2, mod 2, ndx 4/ 

        t1=getTime()
    drum:

        'a' > 'freq 80'
        'b' > 'freq 60'

        pattern=|4,16,'xxxxxxabxxxxaxbb'|
        break=|4,16,'xaaxxbaaxxbbxxxb'|

        setTime(pad.t1)
        <<pattern*4 + /vol -10 /  
        <<pattern + break
        <<silence(4)
        <<pattern*4

        <<|4,16,'xaxxaxbbxaxxaxbb'| * 8

        <<|4,16,'xxaxxxxxbbxxxxaa'| * 11

        setTime(400)
        <<|4,16,'xxxxxxxxbxxxbxaa'| * 45
    bass:
        setTime(pad.t1)
        notes1='c5 a a   g c d f  e a  a  b a b g'
        pattern1=|4,16,'***_******_*****'| + 'freq':notes1
        notes2='a5 a4 a5 g  a f d   a c'
        pattern2=|4,16,'****__*_*__*xx**'| + 'freq':notes2

        <<pattern2*4  * /vol -30 -15/
        <<pattern2 + silence(4)
        <<pattern2 *4


        <<pattern2*4 
        <<pattern2 + silence(4)
        <<pattern2 *4

        <<(pattern1 + pattern2) * 5

        setTime(400)
        p=array(5)
        

        p[0]=|4,16,'*_**____xxxxxxxx'| +/vol -15/ + /freq a5 d e g/
        p[1]=|4,16,'*__*____xxxxxxxx'| +/vol -15/ + /freq d5 f /
        p[2]=|4,16,'*_*___*_xxxxxxxx'| +/vol -15/ + /freq g5 e g/
        p[3]=|4,16,'*_**_**_xxxxxxxx'| +/vol -15/ + /freq a5 g d a e g/
        p[4]=|4,16,'*_**____xxxxxxxx'| +/vol -15/ + /freq a5 d e/
        for i=0 to 40
            <<p[random.randint(0,4)]
        endfor


    pad:
        <<pattern *2 + (notes3 + notes4)
        |<|20,8,'x*___*__'| + |10,1,'_'|+/freq d7 f/ +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes4 + notes3)
        |<|20,8,'xx*____*'| + |10,1,'_'|+/freq d7 a/ +  /car 2, mod 2, ndx 4/ 

        <<pattern *2 + (notes3 + notes4)
        |<|20,8,'xx*__**_'| + |10,1,'_'|+/freq e7 f  g/ +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes4 + notes3)
        |<|20,8,'x*___*_*'| + |10,1,'_'|+/freq d7 a f/ +  /car 2, mod 2, ndx 4/ 

        <<pattern *2 + (notes3 + notes4)
        |<|20,8,'x**__**_'| + |10,1,'_'|+/freq e7 d f g/ +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes4 + notes3)
        |<|20,8,'x**__*_*'| + |10,1,'_'|+/freq d7 e f a/ +  /car 2, mod 2, ndx 4/ 

        <<pattern *2 + (notes3 + notes4)
        |<|20,8,'x**__**_'| + |10,1,'_'|+/freq d7 f d g/ +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes4 + notes3)
        |<|20,8,'x**__*_*'| + |10,1,'_'|+/freq d7 a g a/ +  /car 2, mod 2, ndx 4/ 

        <<pattern *2 + (notes3 + notes4)
        |<|20,8,'x**__**_'| + |10,1,'_'|+/freq e7 g f g/ +  /car 2, mod 1, ndx 4/
        <<pattern *2 + (notes4 + notes3)
        |<|20,8,'x**__*_*'| + |10,1,'_'|+/freq d7 a f e/ +  /car 2, mod 2, ndx 4/ 

        <<|35,1,'*'|^4  + notes1  
        |<|20,8,'x**__*_*'| + |20,1,'_'|+/freq f7 a e c/ +  /car 2, mod 2, ndx 4/ 

        end=getTime()

    mixer:
       
        ftgen(1,0,1024,7,0,112,1,800,1,112,0)
        ftgen(2,0,1024,7,0.1,(400/pad.end)*1024,0.1,(pad.end-400)/pad.end*1024,0.9)
        ftgen(3,0,1024,7,0.1,(400/pad.end)*1024,0.9,(pad.end-400)/pad.end*1024,0.1)

        <<|pad.end,1,'*'| + /vol 1/ + /drp 2/ + /bp 3/
#end
options = '-odac'

