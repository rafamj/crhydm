#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

  instrument String vol freq: pan
    envf=linseg(freq*3,p3/4,freq*2,3*p3/4,freq)
    nd=line(4,p3,1)
    env=linseg(0,0.05,1,p3-0.3,1,0.1,0)
    sig=wgbow(ampdbfs(vol),freq,1,0.127236,0,0)
    sig=butterlp(sig,envf)
    outs(2*sig*pan*env,2*sig*(1-pan)*env)
  endinstrument

  sine1=ftgen(0, 0, 65536, 10, 1)

  ioctfn=ftgen(0, 0,  1024,  -19,  1,  0.5,  270,  0,   2.5, 0.1, 0, 0,  4, 0.1, 0, 0)

  instrument Drone vol freq:

      k:nd=2*(2+oscil(0.2,0.25,-1) + oscil(0.3,0.31,-1,-1)+ oscil(0.2,0.11,-1,-1))
      
      sig1=foscil(ampdbfs(vol),freq,4,1,nd,sine1,-1)
      k:brill=1.5+oscil(0.2,0.22,-1,-1)+oscil(0.3,0.31,-1,-1)+oscil(0.2,0.15,-1,-1)+ oscil(1,0.51,-1,-1) + oscil(0.1,0.32,-1,-1)
      k:f= 1+oscil(0.3,0.5,-1,-1) + oscil(0.2,0.3,-1,-1)+oscil(0.13,0.24,-1,-1) + oscil(0.26,0.21,-1,-1)
      sig2=hsboscil(ampdbfs(vol),f*freq,brill,freq,sine1,ioctfn,3,-1)
      k:pan=oscil(1,freq/400,-1,-1)
      outs((sig1+sig2*0.4)*pan,(sig1*0.8+sig2*0.6)*(1-pan))
  endinstrument

  sine=ftgen(0, 0, 65536, 10, 1)
  curve=ftgen(0,0,257,9, .5,1,270,1.5,.33,90,2.5,.2,270,3.5,.143,90,4.5,.111,270)

  instrument Synth vol freq: nh

      env=adsr(0.1,0.4,0.6,0)
      dis=linseg(0,0.2,0.2,p3/2-0.2,0,p3/2,1)
      sig=buzz(ampdbfs(vol),freq,nh,sine)
      sig=distort(sig, dis, curve)
      outs(sig*env,sig*env)
  endinstrument

#score
  String:
       define list gC(root,type): #0 major 1 minor 2 dominant 3 mb5
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

         bassRoot=inter.execTranspose(root,-12)
         bassFifth=inter.execTranspose(fifth,-12)
         t=inter.execTranspose(third,12)
         #return ['list',[ ['string',root],['string',third],['string',fifth],['string', seventh],['string', bassRoot],['string', bassFifth]]] #types inside a list must be defined 
         return ['list',[ ['string',root],['string',third],['string',fifth]]]
     enddefine


  pattern=|2,16,'*___*__*__*_*_*_'|^3 + /vol 1, pan 0.5/
  notes=/freq/
  notes +='freq':gC({c6},0) + 'freq':gC({c6},0)+'freq':gC({c6},0)+'freq':gC({d6},1)+ 'freq':gC({c6},0)+'freq':gC({d6},1)+'freq':gC({d6},1)
  for i = 1 to 10
  <<(pattern + notes)*4
  notes += 1
  endfor
  <<|16,64,'*'*64|^4 + /vol -5, freq b6 d+7 f+ a+/

  Drone:
    pattern=|8,1,'*'| + /vol -30/
    notes=/freq c5/
    for i = 1 to 10
      <<pattern + notes
      notes +=1
    endfor
    <<|16,1,'*'| + notes
  Synth:
    <<|8,16,/freq c7______ f_ f+ g z____/| + /vol -30/ + /nh 3/
    <<|8,16,/freq z______ c7+_ f+ g+ z___ d7/| + /nh 4/
    <<|8,16,/freq d7____ d7+ f_ f+ g z____/| + /nh 5/
    <<|8,16,/freq z__ d7+___ a+_ b a+__ d+ e_/| + /nh 6/
    <<|8,16,/freq e7________ b______ /| + /nh 7/
    <<|8,16,/freq z_____ f_ f+ g z__ f__/| + /nh 8/
    <<|8,16,/freq g7_____ b_ c8 d e__ g+__/| + /nh 9/
    <<|8,16,/freq g+7______ c+9_ e f+ a+8____/| + /nh 10/
    <<|8,16,/freq a7______ c9_ e f a8____/| + /nh 11/
    <<|8,16,/freq a+7______ c+9_ f g+ a+8____/| + /nh 12/
    <<|16,1,/freq b/| + /nh 13/
#end
options='-odac'

