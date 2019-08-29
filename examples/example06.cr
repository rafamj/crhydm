#options
  -odac

#orchestra
  sr = 44100
  nchnls = 2
  0dbfs = 1

  instrument Bass vol freq: pan
    env=linseg(0,0.1,1,p3-0.2,1,0.1,0)
    sig=pluck(ampdbfs(vol),cpspch(freq),cpspch(freq)*10,0,1)
    outs(sig*pan*env,sig*(1-pan)*env)
  endinstrument


#score

    //defined functions have python syntax, but have to declare return value (string, number, list, void)
    


      //in functions called from within a pattern, the first argument is the actual value 
      //and the second argument is a number between 0 and 1 that indicates the point in time inside the pattern
      define string vary(v, g, q):
          return str(float(v) * q)
      enddefine


      define list generate():
           #return 'a4 b_ c'
           return [ [ 4.08, 1] , [4.10, 2] ,[4.00, 1]]  #it's equivalent to the string 'a4 b_ c'
      enddefine
     

      Bass:
        pattern=|2,4,'freq':generate()| + /vol -15/   //the pattern is the return value of a function
        <<pattern * 'pan':[1,0] * 'pan':vary(0.5)    // the function vary changes the values of the pattern
        pattern=|2,8,'__x(**)__*'| + 'vol':'-20 ? -10'   // the ? indicates than this value is not changed
        pattern += 'freq':{e5,  f} + ('freq':{g} + 'pan':[1,0])
        <<pattern
        <<pattern + 'freq':{?,  ?, g+}
        <<pattern + 'freq':'e5  f g'
        p=|4,8,'freq':'a4_ b c z a__'|
        <<p
        p=|4,8,'freq':{a4_, b, c, z, a__}|
        <<p

        <<p + 'pan':'0.5' 
        p=|4,4,'freq':'a4_ b c'| + 'pan':[0]

        pattern += 'freq':'e5  f g'

        x='pan'
        a=0.5
        <<pattern 
        pattern += 'freq':'e5 f g'
        <<pattern * x:'1 0'
        <<pattern * x:[1,0] * x:vary(a)
        <<pattern * 'pan':[0,1] * 'pan':vary(0.1) - /freq e5 d c/   // makes the 3 last notes e d c

        var(10,14,'pan',0,1)  // ensure that there is a  value and not a '.'
        var(10,14,'pan',vary(0.5))

#end

