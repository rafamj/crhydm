#!/usr/bin/python3
from types import FunctionType
import sys
import copy

SILENCE_CHAR='x'
PROL_CHAR='_'
NOTE_CHAR='*'
NO_PAR_CHAR='.'

class Options:

    options=''

    def asString(self):
        res= '<CsOptions>\n'
        res+=self.options
        res+= '\n</CsOptions>\n'
        return res

    def insert(self,o):
        self.options+=o


class InstrumentBase:
    def __init__(self,n,par, pitchPar, midiPar):
        self.name=n
        self.params=['p1','p2','p3'] + par
        self.pitchPar=pitchPar
        self.midiPar=midiPar
        self.used=False

    def getPositionOfParameter(self,p):
        try:
            return self.params.index(p)
        except ValueError:
            print('Error. ' + p + ' is not a parameter of ' + self.name + '.')
            exit()
            #return -1

    def getPositionOfParameterNext(self,p):
        p += '_next'
        try:
            return self.params.index(p)
        except ValueError:
            return -1

    def asString(self):
        if self.used:
            text='instr ' + self.name + '\n' + self.text + '\n'
            return text
        else:
            return ''

class Instrument(InstrumentBase):

    def __init__(self,n,par,pitchPar, midiPar, table,instr, mod_params,inputs,outputs):
        InstrumentBase.__init__(self,n,par, pitchPar, midiPar)
        self.zakOuts=outputs # every element tuple with: (out,type,zak number)
        self.inputs=inputs
        self.table=table #symbol table
        self.instr=instr # instructions
        self.mod_params=mod_params
        self.text=''


    def insertZakOuts(self, zakOuts):
        self.zakOuts=zakOuts

    def insertInputs(self, inputs):
        self.inputs=inputs


class Instr(InstrumentBase):
    def __init__(self,name,text):
        InstrumentBase.__init__(self,name,[],[],[])
        self.text=text

class Opcode:
    def __init__(self,name,text):
        self.name=name
        self.text=text
        
    def asString(self):
        return 'opcode ' + self.name + self.text

class Orchestra:

    def __init__(self):
        self.instruments=[]
        self.opcodes=[]
        self.globalSection=[]
        self.globalFunctions=[]
        self.globalText=''
        self.zakNumbera=0
        self.zakNumberk=0

    def insertGlobal(self,g):
        self.globalSection +=g

    def insertGlobalFunction(self,f):
        self.globalFunctions +=f

    def insertInstrument(self,instr):
        self.instruments.append(instr)

    def insertOpcode(self,opcode):
        self.opcodes.append(opcode)

    def getZak(self):
        return (self.zakNumbera+self.zakNumberk)>0

    def getZakNumber(self, t):
        if t=='a':
            n=self.zakNumbera
            self.zakNumbera+=1
        else:
            n=self.zakNumberk
            self.zakNumberk+=1
        return n

    def asString(self, instr):
        res= '<CsInstruments>\n'
        res+=self.globalText
        res+='\n'
        if self.getZak():
            if self.zakNumbera==0:
                self.zakNumbera=1
            if self.zakNumberk==0:
                self.zakNumberk=1
            res+='zakinit ' + str(self.zakNumbera) +',' + str(self.zakNumberk) + '\n'
        for opcode in self.opcodes:
            res+=opcode.asString()
        for instrument in self.instruments:
            if  not instr or instrument.name in set(instr):
                res+=instrument.asString()
        res+= '</CsInstruments>\n'
        return res

class Score:

    def __init__(self):
        self.patterns=[]
        self.times={}
        self.list=[] 
        self.functions=[]
        self.tempo=[]
        self.line=[] #this is a auxiliar variable, that can be examined inside a function
         
    def  asString(self, instruments,t1,t2):
        res= '<CsScore>\n'
        for t in self.functions:
            res += t + '\n'
        if len(self.tempo)>0:
            res +='t'
            for t in self.tempo:
                res += ' ' + str(t[0]) + ' '+ str(t[1])
            res+=  '\n'



        if len(self.list)==0:
            res+= 'e\n</CsScore>\n'
            return res

        l=self.list
        for lin in l:
            instrumentName=lin.pop(0)
            try:
                instrName=str(int(instrumentName)) + ' '
            except ValueError:
                instrName='"' + instrumentName + '" '

            lin.pop(0) #last time
            for line in lin:
                if line[0]=='+': # + in p1 and . in p2
                    t+=ant_dur 
                else:
                    t=float(line[0])
                if line[1]!='.':
                    ant_dur=float(line[1])

                if(t1==-1 or t>=t1) and (t2==-1 or t<=t2):
                    if  instrumentName in instruments or len(instruments)==0:
                        if t1!=-1:
                            line[0] = str(float(line[0])-t1)
                        res+='i' + instrName + ' '.join(line)+'\n'

        res+= 'e\n</CsScore>\n'
        return res

    def insertFunction(self,f):
        self.functions.append(f)

    def insertParameters(self,instr,start,parameter,p):
        values=[parameter] + p
        segment=[]
        n=len(values)- 1
        for line in self.list:
            if line[0]== instr.name:
                for lin in line[2:]:
                        if float(lin[0])>=start: #time
                            segment.append(lin)
                            n-=1
                            if n<=0:
                                break #out of the for loop
                self.applyValues(instr,segment,values)

    def insertModification(self,instr,t1,t2,par,v1,v2):
        segment=[]
        for line in self.list:
            if line[0]== instr.name:
                i=2
                while i<len(line):
                    t=float(line[i][0])
                    if t>=t1 and t<t2: #time
                        segment.append(line[i])
                    i=i+1
                if v2==-1: #v1 is a function
                    self.applyFunction(instr,segment, ['callLater',par] + [v1])
                else:
                    self.applyVariations(instr,segment,[par,v1,v2])

    def insertLineInInstrument(self,instr,l):
        for score  in self.list:
            if score[0]==instr.name:
                if l[0]==PROL_CHAR:
                    d=float(score[-1][1])+float(l[1])
                    score[-1][1]=str(d)
                    return
                elif l[0]==SILENCE_CHAR:
                    return
                else:
                    d=score[1]
                    l[0]=str(float(l[0])+float(d))
                    score.append(l)
                    return
        #new instrument
        if l[0]!=PROL_CHAR and l[0]!=SILENCE_CHAR:
            self.list.append([instr.name, 0] + [l])
        if l[0]==SILENCE_CHAR:
            self.list.append([instr.name, 0])
        return 

    def updateTime(self,instr,incTime):
        for score  in self.list:
            if score[0]==instr.name:
                score[1]=str(float(score[1])+incTime)
    
    def getActualTime(self,instr):
        for score  in self.list:
            if score[0]==instr:
                return float(score[1])
        return 0

    def insertPattern(self,instr, pat):
        l=[]
        for p in pat:
            if p=='+':
                a1=l.pop()
                a1len=l.pop()
                a2=l.pop()
                a2len=l.pop()
                for ll in a1:
                    if ll[0]!=SILENCE_CHAR and ll[0]!=PROL_CHAR:
                        ll[0]=str(float(ll[0])+a2len)
                a2.extend(a1)
                l.append(a1len+a2len)
                l.append(a2)
            elif p=='*':
                v=l.pop()
                a=l.pop()
                self.applyVariations(instr,a,v)
                l.append(a)
            elif p=='.':
                v=l.pop()
                a=l.pop()
                self.applyValues(instr,a,v)
                l.append(a)
            else:
                if type(p).__name__=='Pattern':
                    v=p.asList(instr)
                    l.append(p.dur) #pusht the dur in order to calculate the total lenght later
                    l.append(v)
                else:
                    l.append(p)
        if len(l)>2:
            print('error in list and pattern expression')
            exit(0)
        if len(l)==1:
            return
        for p in l[1]: 
            self.insertLineInInstrument(instr,p)
        self.updateTime(instr,l[0])

    def applyVariations(self,instr,l,variation):
        if len(l)==0:
            return
        n=variation[0]
        if n=='callLater':
            self.applyFunction(instr,l,variation)
            return
        t0=0
        i=len(l)-1
        dur=0
        lastDur=float(l[i][1])
        while (l[i][0]==SILENCE_CHAR or l[i][0]==PROL_CHAR) and i>0:
            dur += float(l[i][1])
            i-=1
        if l[i][0]!=SILENCE_CHAR and l[i][0]!=PROL_CHAR:
            dur +=float(l[i][1])
            te=float(l[i][0]) 
        else:
            return
        
        parN=instr.getPositionOfParameter(n)
        glissN=instr.getPositionOfParameterNext(n)
        nVars=0
        for v in variation:
          if v!='>':
              nVars+=1
        nVars=(nVars-1)/2
        inct=(te+dur-t0)/nVars
        t1=t0
        i=1
        while i<len(variation):
            g=False
            t2=t1+inct
            v1=float(variation[i])
            if i+1>=len(variation):
                print('error in variation',variation)
                exit()
            v2=variation[i+1]
            if v2=='>':
                g=True
                i+=1
                if i+1>=len(variation):
                    print('error in variation',variation)
                    exit()
            v2=float(variation[i+1])
            if g and glissN==-1 or not g:
                t2-=lastDur
            for line in l:
                if line[0]!=SILENCE_CHAR and line[0]!=PROL_CHAR:
                    t=float(line[0])
                    if t>=t1 and t<=t2: #time
                        if t2==t1:
                            print('Trying to vary parameter ' + n + ', instrument ' + instr.name + ' in an instant of time')
                            exit()
                        line[parN-1]=str(v1+(v2-v1)*(t-t1)/(t2-t1))
                        if glissN!=-1:
                            if g:
                                line[glissN-1]=str(v1+(v2-v1)*(t+float(line[1])-t1)/(t2-t1))
                            else:
                                line[glissN-1]=line[parN-1]
            i+=2
            t1=t2

    def applyFunction(self,instr,l,variation):
        f=variation[2][2][0]
        if len(l)==0:
            return
        n=variation[1]
        i=len(l)-1
        dur=0
        lastDur=float(l[i][1])
        while (l[i][0]==SILENCE_CHAR or l[i][0]==PROL_CHAR) and i>0:
            dur += float(l[i][1])
            i-=1
        if l[i][0]!=SILENCE_CHAR and l[i][0]!=PROL_CHAR:
            dur +=float(l[i][1])
            te=float(l[i][0]) 
        else:
            return
        parN=instr.getPositionOfParameter(n)
        for line in l:
            if line[0]!=SILENCE_CHAR and line[0]!=PROL_CHAR:
                t=float(line[0])
                if t>=0 and t<=te+dur: #time
                    p1=line[parN-1]
                    p2=t/(te+dur)
                    func="f('" + p1 + "'," + str(p2) + ","
                    for p in variation[2][1]:
                        func += str(p) + ','
                    func=func[:-1]
                    func+=')'
                    self.line=line
                    line[parN-1]=eval(func)
        
    
    def applyValues(self,instr,lines,values):
        if len(lines)==0:
            return
        values=copy.deepcopy(values)
        val=self.translateValues(instr,values)
        if val[0]==-1:
            fromTheEnd=True
            val.pop(0)
        else:
            fromTheEnd=False
            
        for v in val:
            #par=v[0]
            par=v.pop(0)
            parN=instr.getPositionOfParameter(par)-1
            if fromTheEnd:
                i=len(lines)-1
                v=v[::-1] # reverse
            else:
                i=0
            j=0
            while j<len(v):
                if not (lines[i][0]==PROL_CHAR or lines[i][0]==SILENCE_CHAR):
                    if str(v[j])!='?':
                        lines[i][parN]=str(v[j])
                    j=j+1
                if fromTheEnd:
                    i=i-1
                    if i<0:
                        break
                else:
                    i=i+1
                    if i>=len(lines):
                        break 
    
    def joinList(self,l):
        if ',' in l:
            r=self.joinList(l[0]) + self.joinList(l[2])
            return r
        else:
            return [l]
                    
    def translateValues(self,instr,l):
        if l[0]==-1:
            fromTheEnd=True
            l.pop(0)
        else:
            fromTheEnd=False
            
        values=self.joinList(l)
        newValues=[]
        for v in values: # take care of the glissandi
            par=v[0]
            if instr.getPositionOfParameterNext(par)!=-1:
                nv=[par]
                nvg=[par + '_next']
                i=1
                while i< len(v):
                    if v[i]=='>':
                        nvg[-1]=v[i]
                    elif nvg[-1]=='>':
                        nvg[-1]=v[i]
                    else:
                        nv.append(v[i])
                        nvg.append(v[i])
                    i+=1
                newValues.append(nv)
                newValues.append(nvg)
            else:
                newValues.append(v)
        if fromTheEnd:
            newValues.insert(0,-1) #restore the -1 at the start
        return newValues
                
    def insertString(self,instr,s):
        l=s.split()
        for score  in self.list:
            if score[0]==instr:
                score.append(l)
                return
        #new instrument
        self.list.append([instr, 0] + [l])

    def setTempo(self,instr,t):
        pos=0
        for score  in self.list:
            if score[0]==instr:
                pos=float(score[1])
        self.tempo.append([pos, t])

class Dictionary:
    
    def __init__(self):
        self.dict={}
        self.addTranslation(['x', SILENCE_CHAR])
        self.addTranslation(['_', PROL_CHAR])
        self.addTranslation([NOTE_CHAR, ''])

    def delete(self,k):
        del self.dict[k]

    def addTranslation(self,t):
        t=self.processTranslation(t)
        for item in t:
            k=item.pop(0)
            v=self.dict.get(k,[])
            v.append(item)
            self.dict.update({k : v})

    def processTranslation(self,t):
        res=[]
        if t[1]=='':
            t[1]=NO_PAR_CHAR

        if  t[1]==SILENCE_CHAR:
                return [[t[0],SILENCE_CHAR]]
        elif t[1]==PROL_CHAR:
                return [[t[0],PROL_CHAR]]
        elif t[1]==NO_PAR_CHAR:
                return [[t[0],NO_PAR_CHAR]]
        params=t[1].split()
        if len(params)%2==1:
            print('error in translation. ',t)
            exit()
        i=0
        while i<len(params):
            x=[t[0],params[i],params[i+1]]
            i+=2
            res.append(x)
        return res


class Pattern:

    def __init__(self,d,part,p,modp,n):
      p=p.replace(" ","")
      self.translation={}
      self.pattern=[[p]]
      self.dur=d
      self.parts=part
      self.durations=[0]*int(part)
      for i in range(part):
          self.durations[i]=self.dur/self.parts
      if modp!='':
          mods=[0]*part
          j=0
          l=len(modp)
          for i in range(l):
              ch=modp[i]
              if ch==NOTE_CHAR:
                  mods[j]=self.dur/l
                  j+=1
              elif ch==PROL_CHAR:
                  mods[j-1]+=self.dur/l
              else:
                  print('error defining pattern',p,modp)
                  exit()
          for i in range(part):
              self.durations[i]=self.durations[i]*(1-n)+mods[i]*n
 
    def setDictionary(self,d):
         self.translation=d.dict
    
    def duration(self):
        return  self.dur
    
    def merge(self, p):
        p=p.replace(" ","")
        self.pattern.append([p])

    def reply(self, n):
        np=0
        while np< len(self.pattern):
            i=0
            l=[]
            while i <n:
                l= l + self.pattern[np]
                i=i+1
            self.pattern[np]=l
            np=np+1

    def translateMain(self, line, p, instr, t, legato,duration):
        parN=1
        time=t
        line[0]=str(time)
        if legato:
            line[1]=str(-duration)
        else:
            line[1]=str(duration)
            
        keys=sorted(self.translation.keys()) # the longest keys before
        keys.reverse()
        for item in keys:
            if p.startswith(item):
                trans=self.translation.get(item)
                for t in trans:
                    if t[0]==SILENCE_CHAR:
                        line[0]=SILENCE_CHAR
                    elif t[0]==PROL_CHAR:
                        line[0]=PROL_CHAR
                    elif len(t)==1: #it has only a value. The parameter is assumed to be the next
                        parN+=1
                        if parN<len(line): # in case there are no parameters
                            line[parN]=t[0] 
                    else:
                        parN=instr.getPositionOfParameter(t[0])-1
                        if parN>=0:
                            line[parN]=t[1]
                        else:
                            print('parameter '+t[0]+' not found')
                            exit()
                time+=duration
                p=p[len(item):]
                return p,time
        return None,time        

    def translateMore(self, instr, line, p):
        parN=1
        keys=sorted(self.translation.keys()) # the longest keys before
        keys.reverse()
        for item in keys:
            if p.startswith(item):
                trans=self.translation.get(item)
                for t in trans:
                    if not (t[0]==SILENCE_CHAR or t[0]==PROL_CHAR):
                        if line[0]==PROL_CHAR or line[0]==SILENCE_CHAR:
                            print("can't add parameters to a silence or prolongation, ",p)
                            exit()
                        if len(t)==1: #it has only a value. The parameter is assumed to be the next
                            parN+=1
                            line[parN]=t[0] 
                        else:
                            parN=instr.getPositionOfParameter(t[0])-1
                            if parN>=0:
                                line[parN]=t[1]
                            else:
                                print('unknown parameter ' + t[0])
                                exit()
                p=p[len(item):]
                return line,p
        return None,p 

    def asList(self, instr):
        pat=copy.deepcopy(self.pattern) #copy of the patterns
        mainPat=pat.pop(0) #here are the main patterns
        res=[]
        for i in range(len(mainPat)): #problems with python
            res.append([])
        parts=[0] * len(mainPat)
        t=[0] *len(mainPat)
        line=[['.']*(len(instr.params) -1)]*len(mainPat)
        legato=False
        while len(mainPat[0])>0:
            np=0
            while np<len(mainPat): #loops over every main pattern
                line[np]=['.'] * (len(instr.params) -1)
                if mainPat[np][0]=='(':
                    mainPat[np]=mainPat[np][1:]
                    legato=True
                elif mainPat[np][0]==')': #the last note have p2 positive
                    mainPat[np]=mainPat[np][1:]
                    res[np][-1][1]=str(float(res[np][-1][1])* -1)
                    legato=False
                    if  len(mainPat[np])==0: # ( at the end
                        np+=1
                        continue
                mainPat[np],t[np]=self.translateMain(line[np],mainPat[np],instr, t[np], legato,self.durations[parts[np]])
                parts[np]+=1 #only verify parts in the main pattern
                if mainPat[np]==None:
                    print('error 1 in pattern ',self.pattern[np])
                    exit()
                #now, for every main pattern, add the secondary patterns
                nnp=0
                while nnp<len(pat):
                    line[np],pat[nnp][np]=self.translateMore(instr,line[np], pat[nnp][np])
                    if line[np] is None :
                        print('error 2 in pattern '+self.pattern[nnp][np]+' translation not found')
                        exit()
                    nnp+=1
                res[np].append(line[np])    
                np+=1
        i=0
        for p in parts:
            if p!=self.parts:
                print('error in pattern length ',self.pattern[i],' expected length '+str(self.parts)+' actual length '+str(p))
                exit()
            i=i+1
                            
        resul=[]
        for r in res:        
            for l in r:
                resul.append(l)       
        return resul

class Song:

    def __init__(self):
        self.options=Options()
        self.orchestra=Orchestra()
        self.score=Score()

    def insertInstrument(self,instr):
        self.orchestra.insertInstrument(instr)

    def insertOpcode(self,opcode):
        self.orchestra.insertOpcode(opcode)

    def insertGlobal(self,g):
        self.orchestra.insertGlobal(g)

    def insertGlobalFunction(self,f):
        self.orchestra.insertGlobalFunction(f)

    def insertScoreFunction(self,f):
        self.score.insertFunction(f)

    def insertPattern(self,n,p):
        self.score.insertPattern(n,p)

    def insertString(self,instr,s):
        self.score.insertString(instr,s)

    def insertTime(self,instr,name):
        self.score.insertTime(instr,name)

    def insertParameters(self,instr,start,parameter,p):
        self.score.insertParameters(instr,start,parameter,p)    

    def insertModification(self,instr,t1,t2,par,v1,v2):
        self.score.insertModification(instr,t1,t2,par,v1,v2)

    def getActualTime(self,instr):
        return self.score.getActualTime(instr)

    def insertOption(self,o):
        self.options.insert(o)

    def setTempo(self, instr, tempo):
        self.score.setTempo(instr, tempo)

    def getZakNumber(self, t):
        return self.orchestra.getZakNumber(t)

    def getZak(self):
        return self.orchestra.getZak()

    def asList(self):
        self.score.asList([])

    def asString(self, instruments,t1, t2):
        res= '<CsoundSynthesizer>\n' 
        res+= self.options.asString()
        res+= self.orchestra.asString(instruments)
        res+= self.score.asString(instruments,t1,t2)
        res+='</CsoundSynthesizer>\n'
        return res


#------------------------------------------------

class Interpreter:
    SEPARATORS=set([' ','\t'])
    SPECIAL=set(['=', "'", '[', ']','<', '>','|','\n','*','/','-','+','(', ')','#',':',',','^','{','}','&','!','%',';','\\'])
    START=0
    GLOBAL=2
    ORCHESTRA=3
    INSTRUMENT=4
    SCORE=5
    PATCH=6

    def __init__(self,fileName):
        self.file=open(fileName,"r")
        self.state=self.START
        self.song=Song()
        self.symbolTable={}
        self.env='general'
        self.symbolTable['general']={}
        self.symbolTable['general']['dictionary']={}
        self.symbolTable['general']['orcFunction']={}
        self.symbolTable['general']['scoFunction']={} 
        self.lineNumber=0
        self.charNumber=0
        self.line=''
        self.linePrint=''
        self.song=Song()
        self.initSignatures();
        self.initScoreFunctions() ####
        self.include=''
        self.includeFile=''
        self.octave=0 #used in translatePitch
        self.connections=[]

    def readLine(self):
        if self.include=='':
            self.line=self.file.readline()
            self.linePrint=self.line
            self.lineNumber+=1
            self.charNumber=0
        else:
            self.line=self.includeFile.readline()
            if self.line=='':
                self.include=''
                self.includeFile.close()
                self.readLine()

    def nextChar(self):
        if self.line=='':
            self.readLine()
            if self.line=='':
                return ''

        c=self.line[0]
        self.line=self.line[1:]
        self.charNumber+=1
        return c
 
    def unread(self,ch):
        self.charNumber-=len(ch)
        self.line=ch + self.line
    
    def peekNextChar(self):
        c=self.nextChar()
        self.unread(c)
        return c

    def printError(self,e):
        if self.charNumber>=0:
            print('error in line ' + str(self.lineNumber)+',' + str(self.charNumber) +':' + e)
            print(self.linePrint)
        else:
            print('error in line ' + str(self.lineNumber)+':' + e)
        exit()

    def insertSymbol(self,key,typ,value):
        v=self.symbolTable['general'].get(key)
        if v==None:
            self.symbolTable[self.env][key]=[typ, value]
        else:
            self.symbolTable['general'][key]=[typ, value]

    def insertOrcFunction(self,key,value):
        self.symbolTable['general']['orcFunction'][key]=value #there are not local functions

    def insertScoFunction(self,key,value): 
        self.symbolTable['general']['scoFunction'][key]=value #there are not local functions

    def getSymbol(self,key):
        if '.' in key:
            l=key.split('.')
            if len(l)!=2:
                self.print('error :'+key)
            try:
                v=self.symbolTable[l[0]].get(l[1])
                if v!=None:
                    return v[0],v[1]
                else:
                    return ['','']
            except KeyError:
                self.printError("Unknown identifier: " + l[0])
        else:
            v=self.symbolTable[self.env].get(key)
            if v!=None:
                return v[0],v[1]
            elif self.env!='general':
                v=self.symbolTable['general'].get(key)
            if v!=None:
                return v[0],v[1]
            else:
                return ['',''] ######

    def getOrcFunction(self,key):
        return self.symbolTable['general']['orcFunction'].get(key,['',''])

    def getScoFunction(self,key):
        return self.symbolTable['general']['scoFunction'].get(key,['',''])

    def cleanSymbolTable(self,key):
        self.symbolTable.pop(key,None)

    def readIdentifier(self,ch):
        token=''
        while ch not in self.SEPARATORS and ch not in self.SPECIAL:
            token+=ch
            ch=self.nextChar()
            if len(ch)==0:
                return token 
        self.unread(ch)        
        return token   

    def expectToken(self,v):
        value,t=self.nextToken()
        if t not in v:
            s=''
            for e in v:
                s += "'" +e + "' "
            self.printError('expected '+ s + ". Read '" + value + "'")
        return value,t


    def extractPattern(self,patt,parts):
        pat=copy.deepcopy(patt)
        pat=self.getListValue(pat)
        param=pat.pop(0)
        param,t=self.getValue(param)
        trans=''
        notes=[param]
        j=0
        for i in range(len(pat)):
            pati,t=self.getValue(pat[i])
            if len(pati)!=2:
                self.printError('trying to extract pattern (it must be a pitch: parameter)')
            note=pati[0]
            dur=pati[1]
            if note=='0.00' or note ==-36:
                trans+=SILENCE_CHAR
            else:
                trans+=NOTE_CHAR
                notes.append(note)
            j+=1
            while dur>1:
                trans+=PROL_CHAR
                j+=1
                dur-=1
        
        while len(trans)<parts:
            trans+=SILENCE_CHAR
        if len(trans)>parts:
            self.printError('Pattern too long')
        return trans,notes
    
    def readPattern(self):
        time,tt=self.readExpression() #time
        self.expectToken([','])
        parts,tp=self.readExpression() #parts
        self.expectToken([','])
        pat,tpat=self.readExpression() #string or list
        p,t=self.expectToken([',','|'])
        if p=='|':
            return [time,parts,pat,['string',''],['number',0]]
        modPat,tpat=self.readExpression() #string or list
        p,t=self.expectToken([',','|'])
        if p=='|':
            return [time,parts,pat,modPat,['number',1]]
        n,t=self.readExpression() #string or list
        self.expectToken(['|'])
        return [time,parts,pat,modPat,n]

    def readString(self,d):
        token=''
        ch=self.nextChar()
        while ch !=d:
            token+=ch
            ch=self.nextChar()
            if len(ch)==0:
                return None
        return token

    def readNumber(self,ch):
        token=''
        while ch.isdigit() or ch=='.':
            token+=ch
            ch=self.nextChar()
        self.unread(ch)
        return token

    def readComment(self,c):
        ch=self.nextChar()
        if c==';' or c==ch: # ';' or '//'
            ch=self.nextChar()
            while ch!='\n':
                ch=self.nextChar()
            self.unread('\n')
            return 'comment',''
        elif c=='/' and ch=='*':
            while c!='*' or ch!='/':
                c=ch
                ch=self.nextChar()
            return 'comment',''
        else:
            self.unread(ch)
            return 'unknown',''

    def nextToken(self):
        token=''
        ch=self.nextChar()
        while ch in self.SEPARATORS:
            ch=self.nextChar()
        if len(ch)==0:
            return 'eof','section'
        elif ch=='\\':
            tok,t=self.nextToken()
            if tok!='\n':
                self.printError('end of line expected after \\')
            return self.nextToken()
        elif ch=="'" or ch=='"':
            return self.readString(ch),'string'
        elif ch in ['=','[',']','>','<','*','+','-','/','(',')',':',',','^','|','{','}','?','&','%']:
            if ch=='/':
                t,s=self.readComment(ch)
                if t=='comment':
                    return self.nextToken()
            if ch in ['+','*','-','/','=','<','>','|','&','{','}','!']:
                ch1=self.nextChar()
                c=ch+ch1
                if c in ['+=','-=','*=','/=','==','<=','<<','>=','>>','||','&&','{{','}}','!=']: 
                    return c,c
                else:
                     self.unread(ch1)
                     return ch,ch
            return ch,ch
        elif ch=='\n':
            return '\n','\n'
        elif ch==';':
            t,s=self.readComment(ch)
            if t=='comment':
                return '\n','\n'
        elif ch=='#':
                tok,t=self.nextToken()
                if tok=='include':
                    name,t=self.nextToken()
                    try:
                        self.includeFile=open(name)
                        self.include=name
                        return self.nextToken()
                    except IOError:
                        self.printError('error opening file '+name)
                else:
                    self.unread(tok)
                    return '#','section'
        elif ch.isdigit() or ch=='.':
            return self.readNumber(ch),'number'
        else:
            return self.readIdentifier(ch),'identifier'
        return None,'fail' ## 


    def readOrchestra(self):
        result=[]
        line=self.readOrchestraLine()
        while line!=0:
            result.append(line)
            line=self.readOrchestraLine()
        return result

    def printSymbol(self,sp,par,instrName):
        text=''
        typeExpression=''
        if type(sp).__name__=='tuple':
            return self.printSymbol(sp[0],par,instrName)
        else:
            s=sp

        if type(s)==list:
            for i in s:
              text += self.printSymbol(i,par,instrName) 
        else:
            if s in ['if','goto','kgoto','igoto', 'tigoto']:
                text+=s+' '
            elif typeExpression=='string':
                text +='"' + s +'"'
            else:    
                n=self.getParNumber(par,s)
                if n>-1 :
                    text += 'p'+ str(n+4)  #in order to not adding the type at the start
                else:   
                    if s.isnumeric():
                        text +=s
                    elif s[0] in ['"',"'"]:
                        text +=s
                    else:
                        try:
                            float(s)
                            text +=s
                        except ValueError:
                            t,v=self.getSymbol(s)
                            if t=='orcFunction' or t=='instrument' or s=='p3':
                                t=''
                            #if v=='global table':
                            #    s=instrName + '_' +s
                            #if style=='old' and (s=='=' or s=='(' or s==')'):
                            #    s=' '
                            if t=='l':
                                t=''
                                s=v
                            t=self.printType(t)    
                            text += t + s 
        return text        

    def printType(self,t):
        if t=='A':
            t='a'
        if t=='B':
            t='k'
        if t=='boolean':
            t='i'
        return t
    
    def printInstrument(self,instrument,par,instr):
        zak=self.song.getZak()#####
        name=instrument.name
        text=''
        nInput=0
        inputsAtoClear=[]
        inputsKtoClear=[]
        for l in instr:
            if l[0]=='<<': #output
                if zak:
                    #for out in instrument.zakOuts:
                    out=l[1:]
                    for o in out:
                        if o!=',':
                            if o[2]!=-1:
                                text +='z' + self.printType(o[1]) +'wm('+ self.printSymbol(o[0],par,name) + ',' + str(o[2]) + ')\n'
                            else:
                                print(';;output ' + self.printSymbol(o[0],par,name) + ' in ' + instrument.name + ' not connected')
                                #exit()

                else:    #instrument no connected. #########
                    self.printError('instrument ' + instrument.name + ' not connected')
                    for out in instrument.zakOuts:
                        l=len(out)
                        if l==0:
                            ret=''
                        elif l==1:
                            ret='out('+self.printSymbol(out[0][0],par,name)+')\n'
                        elif l==2:
                            ret='outs('+self.printSymbol(out[0][0],par,name)+','+self.printSymbol(out[1][0],par,name)+')\n'
                        else:
                            print('error in output instruction') ####
                            exit()
                        text +=ret  
            elif l[0]=='>>': #zak input
                l.pop(0)
                insOrigin=l.pop(0)
                l.pop(0) # pop the '>>'
                if insOrigin!=[]:#connected to a variable or an instrument
                    nOutput=int(insOrigin[1])
                    insOrigin=insOrigin[0]
                    if len(instrument.inputs[nInput])!=0:
                        no=0
                        for item in l:
                            if item!=',':
                                if self.isInstrument(insOrigin): #instrument
                                    t,i=self.getSymbol(insOrigin)
                                    s=self.printSymbol(item,par,name)
                                    t=s[0]
                                    o=i[1].zakOuts[nOutput][no]
                                    if o[2]==-1:
                                        print(';;output ' +  self.printSymbol(o[0],par,name) + ' in ' + insOrigin + ' not connected.')
                                    else:
                                        text += s
                                        text +='=z' + t +'r('
                                        text += str(o[2])
                                        text +=')\n'
                                        if t=='a':
                                            inputsAtoClear.append(str(o[2]))
                                        else:
                                            inputsKtoClear.append(str(o[2]))
                                else:                               #variable, expression? no
                                    if not insOrigin.isnumeric():
                                        t1,v=self.getSymbol(insOrigin) #is defined?
                                        if t1=='':
                                            self.printError('variable ' + insOrigin + ' not defined')
                                    s=self.printSymbol(item,par,name)
                                    t=s[0]
                                    text += s
                                    text +='=z' + t +'r('
                                    text += self.printSymbol(insOrigin,par,name)
                                    text +=')\n'
                                    if t=='a':
                                        inputsAtoClear.append(str(self.printSymbol(insOrigin,par,name)))
                                    else:
                                        inputsKtoClear.append(str(self.printSymbol(insOrigin,par,name)))

                                no=no+1
                    elif len(instrument.inputs[nInput])==0: #not connected
                        for item in l:
                            if item!=',':
                                text += self.printSymbol(item,par,name)
                                text +='=0\n' #put the input to 0
                                print(';;input ' +  item + ' in ' + instrument.name + ' not connected. Set to 0')
                else: #input not connected
                    n=0
                    for item in l:
                        if item!=',':
                            if len(instrument.inputs[nInput])!=0:
                                if len(instrument.inputs[nInput])>n+1:
                                    t=instrument.inputs[nInput][n+1][2]
                                    t=self.printType(t)
                                    zn=instrument.inputs[nInput][n+1][3] 
                                    text+=t + item + '=z' + t +'r('+  str(zn) + ')\n'
                                    #print('//input ' +  item + ' in ' + instrument.name + ' not connected. Set to 0')
                                    if t=='a':
                                        inputsAtoClear.append(str(zn))
                                    else:
                                        inputsKtoClear.append(str(zn))
                                    n+=1
                                else: #not enough outputs to feed the inputs
                                    self.printError('In instrument '+ name + ', input ' + str(nInput) + ', there are too many variables at the right of >>')
                nInput+=1
                if nInput>=len(instrument.inputs): #last input has been written
                    inputsAtoClear=sorted(set(inputsAtoClear))
                    inputsKtoClear=sorted(set(inputsKtoClear))
                    text+=self.printCl(inputsAtoClear,'a')
                    text+=self.printCl(inputsKtoClear,'k')
            else: # normal instruction
                t,v=self.getSymbol(l[0])
                if len(l)>1 and (self.oldStyle(l[-1][0]) or  l[1]==',' or v=='multi'): #complicated and prone to error
                    l[-2]=' '         # delete the = sign and the parenthesis
                    l[-1][1]=' '
                    l[-1][-1]=' '
                for i in l:
                    text += self.printSymbol(i,par,name)
                text +='\n'
        text += 'endin\n\n'    
        return text

    def printCl(self,z,t):
        if len(z)==0:
            return ''
        text=''
        pairs=[[z[0],z[0]]]
        i=0
        for zc in z:
            if zc.isnumeric() and int(zc)<=int(pairs[i][1])+1:
                     pairs[i][1]=zc
            else:
                i=i+1
                pairs.append([zc,zc])
        for zn in pairs:
            text+='z' + t + 'cl('+ zn[0] + ',' + zn[1] + ')\n'
        return text

    def oldStyle(self, f):
        return f in ['tablei','init','loscil','loscil3','ftgen']
        
    def getParNumber(self,params,p): #the instrument has not been created yet
        try:
            return params.index(p)
        except ValueError:
            return -1

    def renameInstrument(self):
        name,t=self.nextToken()
        newName,t=self.nextToken()
        parameters=[]
        p,t=self.nextToken()
        while p!='\n':
            parameters.append(p)
            p,t=self.nextToken()
        for instrument in self.song.orchestra.instruments:
            if instrument.name==newName:
                self.printError('Instrument '+ newName + ' already defined.')

        for instrument in self.song.orchestra.instruments:
            if instrument.name==name:
                instrument.name=newName
                instrument.params=['p1','p2','p3'] + parameters
                self.insertSymbol(newName,'instrument',[newName,instrument])
                self.symbolTable[newName]={}
                self.symbolTable[newName]['dictionary']={}
                self.cleanSymbolTable(name)
                return
        return

    def readOrchestraLine(self):
        token,t=self.nextToken()
        if token=='0': # 0dbfs
            tok,t=self.nextToken()
            if tok=='dbfs':
                token='0dbfs'
            else:
                self.printError('syntax error')
        if token=='#':
            self.unread('#')    
            return 0
        if token=='instrument':
            name,parameters,par,pitchPar,midiPar,table,instr,inputs,outputs=self.readInstrumentText() #par is like parameters but with some of then anulled
            i=Instrument(name,parameters,pitchPar,midiPar,table,instr,par,inputs,outputs)
            self.insertSymbol(name,'instrument',[name,i])
            self.song.insertInstrument(i)
            return ''
        if token=='instr':
            name,text=self.readInstrText() 
            i=Instr(name,text)
            self.insertSymbol(name,'instrument',[name,i])
            self.song.insertInstrument(i)
            return ''
        if token=='opcode':
            name,outTypes,inTypes,text=self.readOpcodeText() 
            o=Opcode(name,', '+outTypes+', '+inTypes+'\n'+text+'\n')
            outTypes,inTypes=self.translateTypes(outTypes,inTypes)
            self.insertOrcFunction(name,[outTypes,inTypes])
            self.song.insertOpcode(o)
            return ''
        if token=='rename':
            self.renameInstrument()
            return ''
        if token=='reserveZak':
            self.expectToken(['('])
            valuea,t=self.readExpression()
            self.expectToken([','])
            valuek,t=self.readExpression() # t is integer??
            self.expectToken([')'])
            self.song.orchestra.zakNumbera=int(valuea) 
            self.song.orchestra.zakNumberk=int(valuek)
            return ''
        if token=='\n':
            return ''

        result=[token]
        token,t=self.nextToken()

        while token==',': #multiple assignation
            token,t=self.nextToken()
            result.append(',')
            result.append(token)
            token,t=self.nextToken()

        if token=='=':  #variable declaration or assignation
            value,t=self.readExpression()
            for var in result:
                if var!=',':
                    t1,v=self.getSymbol(var)
                    if t1=='':
                        if self.env=='general':
                            if var not in ['sr','kr','nchnls','0dbfs','ksmps']:
                                self.insertSymbol(var,'g'+t,'')
                        else:
                            self.insertSymbol(var,t,'')
            result.append('=')
            #self.insertSymbol(var,t,'')
            result.append(value)
        else:
            self.printError("Syntax error. Assignation or call to function expected")
        return result    

    def translateTypes(self,outTypes,inTypes):
        rin=inTypes
        rout=outTypes
        rin=rin.replace('j','i')
        rin=rin.replace('K','k')
        rin=rin.replace('o','i')
        rin=rin.replace('p','i')
        rin=rin.replace('S','i')
        rout=rout.replace('K','k')
        
        return rout,rin
        
    
    def readInstrumentLine(self,name):
        token,t=self.nextToken()
        if token=='#':
            self.printError("endinstrument expected")
        if token=='endinstrument':
            return 0
            
        if token=='\n':
            return ''
        if t=='<<':    #zak output with nothing to the left
            result=['<<'] #use this for marking the output
            value,tv=self.readExpression()
            result.append([value,tv])
            token,t=self.nextToken()
            while  t==',':
                value,tv=self.readExpression()
                result.append(',')
                result.append([value,tv])
                token,t=self.nextToken()
            return result
        elif t=='identifier':
            if token in ['if','while','until']:
                result=[token]
                token,t=self.nextToken()
                while token not in ['then','goto','igoto','kgoto','do','\n']:
                    result.append(token)
                    token,t=self.nextToken()
                if token=='\n':
                    self.printError("then expected")
                elif token=='then':
                    result.append(' ')
                    result.append(token)
                    return result
                else:
                    result.append(' ')#####
                    result.append(token)
                    token,t=self.nextToken()
                    result.append(token)
                    return result
            elif token in ['endif','od','else','elseif']:
                return [token] ####
            elif token in ['goto','igoto','kgoto','tigoto']:
                 tok,t=self.nextToken()
                 return [token, tok]
            else:
                tok,to=self.nextToken()
                if tok==':':
                    tok,to=self.nextToken()
                    if tok=='\n':  # label
                        return [token+':']
                    else: #variable init with type
                        self.insertSymbol(tok,token,'')
                        token=tok

                else:
                    self.unread(tok)
                result=[token]     
                token,t=self.nextToken()
        elif t=='>>': #input from zak system, with nothing to the left
            result= ['>>', [] ]   #put <= in front in order to mark the input
            result.append('>>')
            result.extend(self.readCommaSeparatedList())
            return result
        elif t=='number':
            tok,t=self.nextToken()
            if t=='>>': #input from number
                result= ['>>', [token, 0] ]   #put <= in front in order to mark the input
                result.append('>>')
                result.extend(self.readCommaSeparatedList())
                return result
        else:
            self.printError("identifier or '<<' expected")

        while token==',': #multiple assignation
            token,t=self.nextToken()
            result.append(',')
            result.append(token)
            token,t=self.nextToken()
        if token=='=':  #variable declaration or assignation
            value,t=self.readExpression()
            #print(value,t)
            for var in result:
                if var!=',':
                    t1,v=self.getSymbol(var)
                    #print(var,v,t1,t)
                    if t1=='':
                        if t=='gi':
                            for i in range(len(result)):
                                result[i] = t+name + '_' + result[i]
                            self.song.insertGlobalFunction([result + ['='] + [value]])
                            self.insertSymbol(var,t+ name + '_','')
                        else:
                            self.insertSymbol(var,t,'')
                    elif t1=='i':
                        self.insertSymbol(var,t,'')
            if t=='gi':
                return ''
            result.append('=')
            result.append(value)
        elif token=='>>':  #input from zak system
            if len(result)>1:
                self.printError("only one element for input is allowed") #for the moment?
            result.append(0) #it can be an instrument or a parameter, 0 in case it is an instrument
            result= ['>>',result] #put <= in front in order to mark the input

            result.append('>>')
            result.extend(self.readCommaSeparatedList())
        elif token=='(':  #call to instrument that doesn't return value
            self.unread('(')          #parse again
            self.unread(result[0])
            value,t=self.readExpression()
            result=value
        elif token=='[': 
            value,t=self.readExpression()
            if t!=']': #input from zak system
                self.expectToken([']'])
            token,t=self.nextToken() #in case there is a subscript [n]
            if t=='=': #assignation to array
                self.expectToken(['='])
                result.append('[')
                result.append(']')
                result.append('=') #the same that with '='
                val,t=self.readExpression()
                t1,v=self.getSymbol(token1)
                t=self.printType(t)
                self.insertSymbol(token1,t,'multi')
                result.append(val)
            elif t=='>>':  #input from zak system
                result.append(value)
                result= ['>>' ,result]#put <= in front in order to identify the input
                result.append('>>')
                result.extend(self.readCommaSeparatedList())
        else:
            self.printError("Syntax error. Assignation or call to function expected")
        return result    

    def readCommaSeparatedList(self):
        token,t=self.nextToken()
        r=[]
        while t=='identifier':
            self.insertSymbol(token,'a','') #we don't know the type
            r.append(token)
            token,t=self.nextToken()
            if token!=',':
                self.unread(token)
                return r
            r.append(',')
            token,t=self.nextToken()
        self.unread(token)
        return r

        
        
    def readInstrumentText(self):
        self.env='general'
        name,t1=self.nextToken()
        if self.isInstrument(name):
            self.printError('instrument already defined '+ name)
        else:
            self.symbolTable[name]={}
            self.symbolTable[name]['dictionary']={}
        par=[]
        glissPar=[]
        pitchPar=[]
        midiPar=[]
        inputs=[]
        outputs=[]
        p,t1=self.nextToken()
        if p=='=':
            n,t=self.nextToken()
            t,v=self.getSymbol(n) 
            i=copy.deepcopy(v[1])
            par = i.params[3:]
            mod_params=i.mod_params
            pitchPar=i.pitchPar
            midiPar=i.midiPar
            table=i.table
            inputs=i.inputs
            zakOuts=i.zakOuts
            #get new zakOuts
            for o in zakOuts:  #new zak  number for every output
                for out in o:
                    t=self.printType(out[1])
                    out[2]=self.song.getZakNumber(t)
            tok,t=self.nextToken()
            if tok=='(':
                while tok!=')':
                    n,t=self.nextToken()        
                    t,v=self.getSymbol(n) 
                    self.expectToken(['='])
                    nn,t=self.nextToken()        
                    par.remove(n)
                    mod_params.remove(n)
                    table[n]=['l',nn] #literal
                    tok,t=self.expectToken([')',','])
            return name, par, mod_params, pitchPar, midiPar,table, i.instr, inputs, zakOuts
        else:
            while p!='\n':
                if p=='+': #glissable parameter
                    glissPar.append(par[-1])
                elif p==':': #octave.pitch notation
                    pitchPar.append(par[-1])
                elif p=='%': #midi notation
                    midiPar.append(par[-1])
                else:
                    par.append(p)
                p,t1=self.nextToken()
        parameters= list(par )
        self.env='local'
        self.symbolTable['local']={}
        instr=[]
        i=4
        #par = ['p1','p2','p3'] + par
        self.insertSymbol('p3','i','p3')
        for p in par:
            self.insertSymbol(p,'i','p'+str(i))
            i=i+1
        for p in pitchPar:
            if p not in glissPar:
                n=par.index(p)
                line=[p , '=', 'cpspch' , '(', 'p' + str(n+4)  ,')']
                instr.append(line)
                par[n]='__deleted_parameter'
        for p in glissPar:
            self.insertSymbol(p + '_next','i','p'+str(i))
            n=par.index(p)
            self.insertSymbol(p,'k','') #from now on the meaning of this parameter is redefined below
            parameters.append(p + '_next')
            par[n]='__deleted_parameter'
            if p in pitchPar:
                line=[p , '=', 'line' , '(', 'cpspch' , '(','p' + str(n+4) ,')', ',', 'abs(p3)', ',' ,'cpspch' , '(', 'p' + str(i) ,')',')']
            else:
                line=[p , '=', 'line' , '(', 'p' + str(n+4) , ',', 'abs(p3)', ',' , 'p' + str(i) ,')']
            instr.append(line)
            i=i+1
        line=self.readInstrumentLine(name)
        while line!=0:
            if len(line)>0:
                instr.append(line)
                if line[0]=='>>':
                    inputs.append(line[1])
                elif line[0]=='<<':  ####revisar cuando se asigne la salida
                    ou=[]
                    for o in line:
                        if o!='<<' and o!=',':
                            t=self.printType(o[1])
                            n=self.song.getZakNumber(t)
                            o.append(n) #new zak number for every output
                            ou.append(o)
                            outputs.append(ou)
            line=self.readInstrumentLine(name)
        table=self.symbolTable['local']
        self.cleanSymbolTable('local')
        self.env='general'
        return name, parameters, par, pitchPar, midiPar, table, instr, inputs, outputs

    def isEndin(self,line,end):
        n=line.find(end)  ###
        return n!=-1

    def readInstrText(self):
        name,t1=self.nextToken()
        if self.isInstrument(name):
            self.printError('instrument already defined '+ name)
        text=''
        self.readLine()
        line=self.line
        while not self.isEndin(line,'endin'):
            text +=line
            self.readLine()
            line=self.line
        text +=line
        self.readLine()
        return name,text    


    def readOpcodeText(self):
        name,t1=self.nextToken()
        self.expectToken([','])
        outTypes,t1=self.nextToken()
        self.expectToken([','])
        inTypes,t1=self.nextToken()
        r,s=self.searchFunctionSignature(name)
        if not (r=='' and s==''):
            self.printError('opcode already defined '+ name)
        text=''
        self.readLine()
        line=self.line
        while not self.isEndin(line,'endop'):
            text +=line
            self.readLine()
            line=self.line
        text +=line
        self.readLine()
        
        return name,outTypes,inTypes,text    

    
    def coerce(self,t1,t2):
        if t1[0]=='g':
            t1=t1[1:]
        if t2[0]=='g':
            t2=t2[1:]
 
        if t1=='x':
            return 'x'
        if t2=='x':
            return 'x'
        if t1=='i':
            return t2
        if t1=='k':
            if t2=='a':
                return 'a'
            else:
                return 'k'
        if t1=='a':
            return 'a'
        if t1=='A': 
            if t2=='i':
                return 'A'
            elif t2=='k':
                return 'A'
            else:
                return t2
        if t1=='B': 
            if t2=='i':
                return 'B'
            else:
                return t2

        return 'i'   


    def isParPitch(self,par):
        t,instr=self.getSymbol(self.env)
        return par in instr[1].pitchPar
        
    def isParMidi(self,par):
        t,instr=self.getSymbol(self.env)
        return par in instr[1].midiPar
        
        
    def createVarlist(self,v1,t1,v2,t2,isPattern=False):
        #v1 is always of type string
        if True or t1 == 'string':
             if t2 in ['call','callLater']: #####
                 if isPattern:
                     v2,t2=self.callFunction(v2[0],v2[1]) ##getValue???
                 else:
                     v1,t1=self.getValue(v1)
                     return ['callLater',v1 , v2],'callLater'
             if t2 in ['list'] :
                 if v1[0][0]=='identifier':  #why not call getValue???
                     #v1,t1=self.getValue(v1[0])
                     v1=[[t1,v1]]
                 for i in range(len(v2[1])):
                     e,t=self.getValue(v2[1][i])
                     v2[1][i]=[t,e]
                 res=['listVar', [[t1,v1]] + v2[1]]
                 return res,'listVar'
             if t2 in ['listPitch','listMidi']:
                 #v2,t=self.getValue(v2)
                 if not isPattern:
                     r=[]
                     v2=self.getListValue(v2) #the first element must be 'list...'
                     for e in v2:
                     #    e,t=self.getValue(e)
                         r.append(e[0])
                     v2=r     
                 else:
                     v2=v2[1]
                 #v2=v2[1][0]
                 res=['listVar',[[t1,v1]] + v2]
                 return res,'listVar'
             if t2 in ['string']:
                 v2=v2.replace('>',' > ').split()
                 v1,t=self.getValue(v1)
                 m=self.isParMidi(v1)
                 if self.isParPitch(v1) or m:
                     r=[[t1,v1]]
                     for e in v2:
                         p,d=self.translatePitch(e)
                         if m:
                             p=self.pitchToMidi(p)
                         if isPattern:    
                             r.append(['list',[['string',p],['number',d]]]) ##['list'... ???
                         else:
                             r.append(['string',p])
                 else:
                     r=[[t1,v1]]
                     for e in v2:
                         r.append(['string',e])
                 #v1=['list',v1]
                 res=['listVar',r]
                 return res,'listVar'
             if t2 in ['number']:
                 v1,t1=self.getValue(v1)
                 res=['listVar',[[t1,v1],[t2,v2]]]
                 return res,'listVar'
        self.printError('types '+t1+' and '+t2+" can't be joined")
    
    
    def sumValues(self,v1,t1,v2,t2):
        if t1=='number':
            if t2=='number':
                return v1+v2,'number'
        elif t1=='string':
            if t2=='string':
                return v1+v2,'string'
            elif t2=='number':
                return v1 + str(v2),'string'
            elif t2=='pattern':
                for p in v2:
                    if type(p).__name__=='Pattern':
                        p.merge(v1)
                return v2,'pattern'
        elif t1=='pattern':
            if t2=='pattern':
                p=copy.deepcopy(v1) 
                p.extend(v2)
                p.extend('+')
                return p,'pattern'
            elif t2=='string':
                for p in v1:
                    if type(p).__name__=='Pattern':
                        p.merge(v2)
                return v1,'pattern'
            elif t2=='listVar':
                p=copy.deepcopy(v1)
                v2=self.getListValue(v2) #listVar[0] is 'listVar'
                p.append(v2)
                p.extend('.')
                return p,'pattern'
        elif t1 in ['list','listPitch','listMidi']:
             if t2==t1:
                 return v1+v2,t1
        elif t1=='listVar':
             #v1,t1=self.getValue(v1)
             
             if t2=='listVar': #if the lists are of the same parameter, they are concatenated
                #v1,t1=self.getValue(v1)
                #v2,t2=self.getValue(v2)
                if False and v1[0][1]==v2[0][1]:
                    return v1 + v2[1:] , 'listVar'
                else:
                    res= ['listVar'] + [[v1] +  [[ 'string',',']] +  [v2]]
                    return res,'listVar'
        self.printError('types '+t1+' and '+t2+" can't be added")


    def sum(self,v1,t1,v2,t2):
        if self.state==self.ORCHESTRA:
            return [v1, '+', v2],self.coerce(t1,t2)
        else:
            return ['+',v1,v2],''
       
    def subValues(self,v1,t1,v2,t2):
        if t1=='number':
            if t2=='number':
                return v1-v2,'number'
        elif (t1=='pattern' or t1=='listVar') and  t2=='listVar':
            v2[1].insert(0,-1)
            return self.sumValues(v1,t1,v2,t2)
        self.printError('types '+t1+' and '+t2+" can't be substracted")

    def orValues(self,v1,t1,v2,t2):
        if t1=='boolean' and t2=='boolean':
            return (t1 or t2),'boolean'
        self.printError('types '+t1+' and '+t2+" can't be ored")
        
    def substract(self,v1,t1,v2,t2):
        if self.state==self.ORCHESTRA:
            return [v1, '-', v2],self.coerce(t1,t2)
        else:
            return ['-',v1,v2],''
      
    def addVariation(self,v1,v2):  #####
       if len(v2)!=3:
           self.printError('error. Variations must have 3 parameters')
           v1.append(v2)
           v1.append('*')
       return v1


    def readSum(self): # product { + product}*
        value,t=self.readProduct()
        ch,cht=self.nextToken()
        while ch in ['+','-','||']:
            v,ty=self.readProduct()
            if ch=='+': 
                value,t=self.sum(value,t,v,ty)
            elif ch=='-':
                value,t=self.substract(value,t,v,ty)
            elif ch=='||':
                value,t=self.logical(value,t,v,ty,'||')
            ch,cht=self.nextToken()
        self.unread(ch) 
        return value,t 

    def multiplyPattern(self,p,n):
        if n<1:
            return [[]]
        p1=list(p)#copy of p
        while n>1:
            p1.extend(p)
            p1.extend('+')
            n-=1
        return p1

    def mulValues(self,v1,t1,v2,t2):
        if t1=='number':
            if t2=='number':
                return v1*v2,'number'
            if t2=='pattern':
                return self.multiplyPattern(v2,v1),'pattern'
            if t2=='string':
                return int(v1)*v2,'string'
            if t2 in ['list','listPitch','listMidi']:
                return int(v1)*v2,t2
            if t2=='listVar':
                return [v2[0] , [v2[1][0]] +  v2[1][1:]*int(v1)],'listVar'
        elif t1=='pattern':
            if t2=='number':
                return self.multiplyPattern(v1,v2),'pattern'
            if t2=='listVar':
                v1,t=self.getValue(v1)
                v2=self.getListValue(v2)
                v1.append(v2)
                v1.extend('*')
                return v1,'pattern'
            if t2=='callLater':
                v1.append(v2)
                v1.extend('*')
                return v1,'pattern'
        elif t1=='string':
            if t2=='number':
                return v1*int(v2),'string'
        elif t1 in ['list','listPitch','listMidi']:
            if t2=='number':
                res=[v1[0],v1[1]*int(v2)]
                return res,t1
        elif t1 == 'listVar':
            if t2=='number':
                v1,t=self.getValue(v1)
                res= [v1[0]]+ v1[1:]*int(v2)
                return res,'listVar'
        self.printError('types '+t1+' and '+t2+" can't be multiplied")

    def multiply(self,v1,t1,v2,t2):
        if self.state==self.ORCHESTRA:
            return [v1, '*',  v2],self.coerce(t1,t2)
        else:
            return ['*',v1,v2],''

    def divValues(self,v1,t1,v2,t2):
        if t1=='number':
            if t2=='number':
                return v1/v2,'number'
        self.printError('types '+t1+' and '+t2+" can't be divided")

    def modValues(self,v1,t1,v2,t2):
        if t1=='number':
            if t2=='number':
                return v1%v2,'number'
        self.printError('types '+t1+' and '+t2+" can't be %[6~")

    def divide(self,v1,t1,v2,t2):
        if self.state==self.ORCHESTRA:
            return [v1, '/',  v2],self.coerce(t1,t2)
        else:
            return ['/',v1,v2],''

    def module(self,v1,t1,v2,t2):
        if self.state==self.ORCHESTRA:
            return [v1, '%',  v2],self.coerce(t1,t2)
        else:
            return ['%',v1,v2],''

    def expValues(self,v1,t1,v2,t2):
        if t1=='pattern':
            if t2=='number':
                v=copy.deepcopy(v1)
                for p in v:
                    p.reply(v2)
                return v,'pattern'
        self.printError('types '+t1+' and '+t2+" can't be divided")

    def andValues(self,v1,t1,v2,t2):
        if t1=='boolean' and t2=='boolean':
            return (v1 and v2),'boolean'
        self.printError('types '+t1+' and '+t2+" can't be Anded")

    def compareValues(self,v1,t1,v2,t2,op):
        if t1=='number' and t2=='number':
            if op=='==':
                return (v1 == v2),'boolean'
            elif op=='!=':
                return not (v1 == v2),'boolean'
            elif op=='>=':
                return (v1>=v2),'boolean'
            elif op=='<=':
                return (v1<=v2),'boolean'
            elif op=='>':
                return (v1>v2),'boolean'
            elif op=='<':
                return (v1<v2),'boolean'

        self.printError('types '+t1+' and '+t2+" can't be compared")
    
    def exponential(self,v1,t1,v2,t2):
        if self.state==self.ORCHESTRA:
            return [v1, '^',  v2],self.coerce(t1,t2)
        else:
            return ['^',v1,v2],''

    def logical(self,v1,t1,v2,t2,op):
        if self.state==self.ORCHESTRA:
            return [v1, op,  v2],'boolean'
        else:
            return [op,v1,v2],''


    def readProduct(self):  # value { * value}*
        value,t=self.readValue()
        ch,cht=self.nextToken()
        while ch in ['*','/','%','^','&&','==','!=','>=','<=','<','>','?',':']:
            v,ty=self.readValue()
            if ch=='*': 
                value,t=self.multiply(value,t,v,ty)
            elif ch=='/':
                value,t=self.divide(value,t,v,ty)
            elif ch=='%':
                value,t=self.module(value,t,v,ty)
            elif ch=='^':
                value,t=self.exponential(value,t,v,ty)
            elif ch in ['&&','==','!=','>=','<=','<','>','?',':']:
                value,t=self.logical(value,t,v,ty,ch)
            ch,cht=self.nextToken()
        self.unread(ch)  
        return value,t

    def adaptParameterType(self,value,t,pt):
        if t==pt:
            return
        if type(value)==list:
            for v in value:
                self.adaptParameterType(v,t,pt)
            return
        elif type(value).__name__=='tuple':
            self.adaptParameterType(value[0],value[1],pt)
        elif value in self.SPECIAL:
            return
        else:
            r,s=self.searchFunctionSignature(value)
            if(r!='' or s!=''):
                return
            if (t=='A' or t=='B') and (pt=='x' or pt=='k'): ####revise
                 t='k'
                 self.insertSymbol(value,t,'')
            elif (t=='A' or t=='B') and (pt=='x' or pt=='a'):
                 t='a'
                 self.insertSymbol(value,t,'')


    def readValueOrchestra(self): # i | k | a | ( expr ) | call()
        value,t=self.nextToken()
        if t=='number':
            return value,'i'
        elif t=='string':
            return '"' + value + '"', t
        elif t=='-':
            v,t=self.readValueOrchestra()
            return '-' + v,t
        elif t=='(':
            value,t=self.readExpression()
            v,ty=self.nextToken()
            if ty==')':
                return ['(', value ,')'],t
            else:
                self.printError(') expected')
        elif t=='identifier':
            vah,tah=self.nextToken()
            if vah=='(': ## call to function
                r,s=self.searchFunctionSignature(value)
                if r=='':
                    if value=='ftgen':
                        r='gi'
                    else:
                        self.printError('unknown function '+value)
                res=[value,'('] 
                ty=self.peekNextChar()
                if ty==')': #probe for ')'
                    v,ty=self.nextToken()
                    res.append(')')
                    return res,r
                else:
                    value,t1=self.readExpression()
                i=0                 ###limpiar esto
                if res[0]!='ftgen':
                    self.adaptParameterType(value,t1,s[i])
                res.append(value)
                v,ty=self.nextToken()
                i=1
                while ty!=')':
                    res.append(',')
                    value,t=self.readExpression()
                    if res[0]!='ftgen':
                        self.adaptParameterType(value,t,s[i])
                    res.append(value)
                    v,ty=self.nextToken()
                    if i<len(s)-1:
                        i+=1
                res.append(')')
                if r=='y' or r=='X':
                    return res,t1#the type of the first argument
                return res,r
            elif vah=='[': # array
                val,tv=self.readExpression()
                self.expectToken([']'])
                return [value,'[',val,']'],t
            elif vah=='=': # Short condition
                self.expectToken(['='])
                e1,t1=self.readExpression()
                self.expectToken(['?'])
                e2,t2=self.readExpression()
                self.expectToken([':'])
                e3,t3=self.readExpression()
                return [value, '==',e1,'?',e2,':',e3] ,t3 #return type t3
            else:  #variable
                self.unread(vah)
                t1,v=self.getSymbol(value)
                if t1=='':
                    self.printError('unknown variable '+value)
                return value,t1
        else:        
           return value,'x'


    def readList(self):
        l=[]
        t=self.peekNextChar() 
        while t!=']':
            value,t=self.readExpression()
            #key=self.generateVar(value,t)
            l.append(value)
            value,t=self.expectToken([',',']'])
        return l,'list'

    def readListPitch(self):
        l=[]
        value,t=self.nextToken()
        ch=self.peekNextChar()
        if ch in ['+','-']:
            self.expectToken([ch])
            value +=ch
        while t!='}':
            value,d=self.translatePitch(value)
            l.append(['list', [['string',value],['number',d]]])
            value,t=self.expectToken([',','}'])
            if t!='}':
                value,t=self.nextToken() 
                ch=self.peekNextChar()
                if ch in ['+','-']:
                    self.expectToken([ch])
                    value +=ch
        return l,'listPitch' #no ['listPitch', l], because readValue adds the type
                
    def readListMidi(self):
        l=[]
        value,t=self.nextToken() 
        while t!='}}':
            value,d=self.translatePitch(value)
            value=self.pitchToMidi(value)
            if value!=-1:
                l.append(['list',[['string',value],['number',d]]])
            else:
                value,t=self.nextToken() ## read the ',' and the next note
                value,t=self.nextToken()
            value,t=self.expectToken([',','}}'])
            if t!='}}':
                value,t=self.nextToken() 
        return l,'listMidi'


    def pitchToMidi(self, value):
        # 8.00 == middle C == 60
        if value=='>':
            return -1
        octave,note=value.split('.')
        try:
            octave=int(octave)
            note=int(note)
        except ValueError:
            self.printError('error converting ' + value + ' to midi note')
            
        mn= octave*12 + note - 36
        
        if value!='0.00' and (mn<0 or mn>127):
            self.printError('error converting ' + value + ' to midi note')
        return mn
        
    def translatePitch(self,value):
        try:
            float(value)
            return value #it is pitch class notation
        except ValueError: #it is abc notation
            if value[0]=='z' or value[0]=='Z':
                octave='0'
                i=1
                duration=1
                while i<len(value):
                    ch=value[i]
                    if ch=='_':
                        duration+=1 
                    else:
                        self.printError('unexpected char')
                    i+=1
                    if i<len(value):
                        ch=value[i]
                    else:
                        break
                return '0.00', duration
            elif value[0]=='>':
                return value[0],0
            elif value[0]=='?':
                return value[0],0
            else:
                octave=''
                note=ord(value[0])
                if (note >= ord('A') and note <= ord('G')):
                    v=note-ord('A')
                elif(note >= ord('a') and note <= ord('g')):
                    v=note-ord('a') 
                else:
                    self.printError('error in music notation ' + value)
                v=(v+5)%7    
                v=v*2
                if v>=6:
                    v=v-1

            inc=0 
            duration=1
            i=1
            ch=''
            while i<len(value):
                ch=value[i]
                if ch.isdigit():
                    octave+=ch
                else:
                    break
                i+=1
            
            if octave=='':
                octave=self.octave

            while ch=='+':
                inc+=1
                i+=1
                if i<len(value):
                    ch=value[i]
                else:
                    break
           
            while ch=='-':
                inc-=1
                i+=1
                if i<len(value):
                    ch=value[i]
                else:
                    break
            
            while ch=='_':
                duration+=1 
                ch=value[i]
                i+=1
                if i<len(value):
                    ch=value[i]
                else:
                    break
            if inc!=0:
                octave = str(int(octave)+(v+inc)//12)
                v = (v+inc)%12
            v='0'+str(v)
            v=v[-2:]

        self.octave=octave
        return octave + '.' + v, duration

    def readVarlist(self):
        t=[]
        token=''
        ch=self.nextChar()
        while ch !='/':
            token+=ch
            ch=self.nextChar()
            if len(ch)==0:
                return None
            if ch==',':
                t.append(token)
                token=''
                ch=self.nextChar()
        t.append(token)
        token=t.pop(0)
        l=token.split()
        par=l.pop(0)
        res=['++',['string', par] , ['string', ' '.join(l)]] #the name of the parameter is in a list
        for token in t:        
            l=token.split()
            par=l.pop(0)
            res=['+',res,['++',['string',par], ['string', ' '.join(l)]]] #++ means createVarlist
        return res,'' #no type, because is an expression

        
    def readValueScore(self): # number | string | pattern | ( expr )
        value,t=self.nextToken()
        if t=='number':
            if '.' in value:
                return float(value),t
            else:
                return int(value),t
        elif t=='-':
            value,t=self.readValueScore()
            return ['number', -1 * value],''  
        elif t=='string':
            return value,t
        elif t=='pattern':
            return value,t
        elif t=='identifier':
            if t=='':
                self.printError('undefined identifier ' + value)
            v1=self.peekNextChar()
            if v1=='(':  # call to function
                v1,t1=self.nextToken()
                par=[]
                while v1!=')':
                  v1=self.peekNextChar()
                  if v1 not in [',',')']:
                      v1,t1=self.readExpression()
                      par.append(v1)
                  else:
                      v1,t1=self.nextToken()
                if value=='ftgen':
                    return  [value,par],'ftgen'
                elif value=='var':
                    return [value, par],'var' 
                elif value=='put':
                    return [value, par],'put' 
                else:
                    return [value, par],'call'
            else: #variable
                return value,t
        elif t=='|':
            return self.readPattern(),'pattern' #a pattern is a list of literal patterns
        elif t== '[':
            return self.readList()
        elif t== '{':
            return self.readListPitch()
        elif t== '{{':
            return self.readListMidi()
        elif t== '/':
            return self.readVarlist()
        elif t=='(':
            value,t=self.readExpression()
            v,ty=self.nextToken()
            if ty==')':
                return value,t
            else:
                self.printError('")" expected')
        else:
            self.unread(value)
            self.printError('unexpected char '+value)
            return '','nothing'

    def readComplexValue(self):
        v1,t1=self.readValueScore()
        c=self.peekNextChar()
        if c==':':                    #listVar
            self.expectToken([':'])
            c=self.peekNextChar()
            if c==':':
                self.expectToken([':'])
            v2,t2=self.readValueScore()
            if c==':' and t2=='call':
                t2='callLater'
            #if t2!='':
            #    v2=[t2,v2]
            if t2 in ['listMidi','listVar']: ##???
                res= ['++',[t1,v1],v2[0]] #++ means createVarlist
            elif t2=='identifier':
                res= ['++',[t1,v1],[t2,v2]]
            elif t2=='':
                res= ['++',[t1,v1],v2]
            else:
                res= ['++',[t1,v1], [t2,v2]]
            ####the first element (the par name) is always a list [type, name]
            return  res,''
        elif c=='[': #list element
            var=[t1,v1]
            while c=='[':
                self.expectToken(['['])
                v,t=self.readList()
                for i in v:
                    var=['index',var]+ [i]
                c=self.peekNextChar()
            return var,'' #it's an operation
        else:  #normal value
             return v1,t1
        
        
    def readValue(self): # number | string | pattern | ( expr )
        if self.state==self.ORCHESTRA:
            return self.readValueOrchestra()
        else:
            v,t=self.readComplexValue()
            if t=='':
                return v,''
            else:
                return [t,v],t


    def readExpression(self):
        return self.readSum()

    def readAssignation(self,varName):
        v,t=self.nextToken()
        if t in ['=','+=','-=','*=','/=']:
            value,ty=self.readExpression()
            result= [t,varName,value]
        else:
            self.printError('syntax error')
        v,t=self.nextToken()
        return result

    def readDictionaryEntry(self,key):
        token,t=self.nextToken()
        if t=='>':
            value,t=self.readExpression()
        else:
            self.printError('">" expected')
        return ['>',key,value]

    def insertPattern(self,value,t):
        #value=self.getListValue(value)
        instr=self.getSymbol(self.env)
        if t=='pattern':
            for p in value:
                if type(p).__name__=='Pattern':
                    self.insertTranslations(p)
            self.song.insertPattern(instr[1][1],value)
            
        elif t=='string':
            self.song.insertString(instr[1][0],value)

    def isInstrument(self,name):
        t,instr=self.getSymbol(name)
        if t=='instrument':
            return True
        else:
            return False

    def readParameters(self):
       l=[]
       token,t=self.readExpression()
       l.append(token)
       token,t=self.nextToken()
       while token!='\n':
           token,t=self.readExpression()
           l.append(token)
           token,t=self.nextToken() ##expect ,
       return l

    def readInstruction(self,token,t):
        if t=='identifier':
            if token=='if':
                return [self.lineNumber] + self.readIf()
            elif token=='while':
                return [self.lineNumber] + self.readWhile()
            elif token=='for':
                return [self.lineNumber] + self.readFor()
            elif token=='define':
                return [self.lineNumber] + self.readDefine()
            else:
                if self.isInstrument(token):
                    t,instr=self.getSymbol(token)
                    instr[1].used=True
                    self.expectToken([':'])
                    return [self.lineNumber,':',token]
                else:
                    tok=self.peekNextChar()
                    if tok=='(':  #call to procedure
                        self.unread(token)
                        value,t=self.readExpression()
                        return [self.lineNumber] + value
                    elif tok=='[': # list element
                        token=['index',[t,token]]
                        while tok=='[':
                            self.expectToken(['['])
                            vi,ti=self.readExpression()
                            self.expectToken([']'])
                            token.append(vi)
                            tok=self.peekNextChar()
                        ass=self.readAssignation(token)
                        return [self.lineNumber] +ass
                    else:          # assignation
                        return [self.lineNumber] +self.readAssignation([t,token])
        elif t=='string':
            return [self.lineNumber] + self.readDictionaryEntry(token)
        elif t=='<<':
            value,t=self.readExpression()
            return [self.lineNumber,'<<',value]
        elif t=='\n':
            return None
        else:
            self.printError('unknown instruction:: '+token+' '+t)

    def readIf(self):
        instructionsif=[]
        instructionselse=[]
        condition,t=self.readExpression()
        token,t=self.expectToken(['identifier'])
        if token!='then':
            self.printError('then expected')
        token,t=self.nextToken()
        while token!='endif' and token!='else':
            i=self.readInstruction(token,t)
            if i != None:
                instructionsif.append(i)
            token,t=self.nextToken()
        if token=='else':
            token,t=self.nextToken()
            while token!='endif':
                i=self.readInstruction(token,t)
                if i != None:
                    instructionselse.append(i)
                token,t=self.nextToken()
        return ['if',condition,instructionsif,instructionselse]
        
    def readWhile(self):
        instructions=[]
        condition,t=self.readExpression()
        token,t=self.nextToken()
        while token!='endwhile':
            i=self.readInstruction(token,t)
            if i != None:
                instructions.append(i)
            token,t=self.nextToken()
        return ['while',condition,instructions]


    def readFor(self):
        instructions=[]
        var,t=self.readExpression()
        self.expectToken(['='])
        init,t=self.readExpression()
        token,t=self.expectToken(['identifier'])
        if token!='to':
            self.printError('to expected')
        condition,t=self.readExpression()
        token,t=self.nextToken()
        while token!='endfor':
            i=self.readInstruction(token,t)
            if i != None:
                instructions.append(i)
            token,t=self.nextToken()
        return ['for',var,init,condition,instructions]

         
    def readDefine(self):
        retval,t=self.nextToken()
        name,t=self.nextToken()
        instructions='def ' + name
        stop=False
        stopPars=False
        pars=''
        while not stop:
            c=self.nextChar()
            if not stopPars:
                pars +=c
            if c==')':
                stopPars=True
            if stopPars and c=='e': # enddefine?
               k=c
               i=0
               while i <len('enddefine') and k[i]=='enddefine'[i]:
                   c=self.nextChar()
                   k+=c
                   i+=1
               if i==len('enddefine'):
                   stop=True
               else:
                   instructions+=k
            else:
                instructions+=c
        return ['define',name, instructions,retval,len(pars[1:-1].replace(',',' ').split())] 

    
    def readScore(self):
        instructions=[]
        token,t=self.nextToken()
        while t!='section':
            i=self.readInstruction(token,t)
            if i != None:
                instructions.append(i)
            token,t=self.nextToken()
        self.execInstructions(instructions)
        
    def execInstructions(self,instructions):
        ant_lineNumber=self.lineNumber
        ant_charNumber=self.charNumber
        self.charNumber=-1
        for instr in instructions:
            self.lineNumber=instr[0]
            if instr[1]=='=':#assignation
                right_value,t=self.getValue(instr[3]) #en la lista debe preservar los tipos
                if instr[2][0]=='index': #list element
                    var=instr[2][1][1]
                    varValue,tv=self.getValue(instr[2][1])
                    n=2
                    index,ti=self.getValue(instr[2][n])
                    if t in  ['list','listVar','listMidi','listPitch']:
                        varValue[1][int(index)]=right_value #varValue[0] is the type
                    else:
                        varValue[1][int(index)]=[t,right_value]
                    self.insertSymbol(var,tv,varValue)
                else:                    #variable
                    if t=='ftgen':
                        #don't call getListValue to get the values
                        #because we have to process the strings
                        r=instr[2][1]
                        v1=right_value[0][1]
                        for i in range(len(v1)):
                            v,t=self.getValue(v1[i])
                            if t=='string':
                                r += ' "' + v+ '"'
                            else:
                                r += ' ' +str(v) 
                        self.song.insertScoreFunction(r)
                    else:
                        self.insertSymbol(instr[2][1],t,right_value)
            elif instr[1] in ['+=','-=','*=','/=','^=']:
                op=instr[1][0]
                self.execInstructions([[instr[0],'=',instr[2],[op,instr[2],instr[3]]]])
            elif instr[1]=='<<':
                v,t=self.getValue(instr[2])
                p=copy.deepcopy(v)
                self.insertPattern(p,t)
            elif instr[1]=='>':
                value,t=self.getValue(instr[3])
                self.symbolTable[self.env]['dictionary'][instr[2]]=value
            elif instr[1]==':':
                self.env=instr[2]
            elif instr[1]=='if':
                cond,t=self.getValue(instr[2])
                if cond:
                    self.execInstructions(instr[3])
                else:
                    self.execInstructions(instr[4])
            elif instr[1]=='while':
                cond,t=self.getValue(instr[2])
                while cond:
                    self.execInstructions(instr[3])
                    cond,t=self.getValue(instr[2])
            elif instr[1]=='for':
                init=[[instr[0],'=',instr[2],instr[3]]]
                incr=[[instr[0],'+=',instr[2],['number',1]]]
                self.execInstructions(init)
                finalCondition=['<=',instr[2],instr[4]]
                cond,t=self.getValue(finalCondition)
                while cond:
                    self.execInstructions(instr[5])
                    self.execInstructions(incr)
                    cond,t=self.getValue(finalCondition)
            elif instr[1]=='call':
                self.getValue(instr[1:])
            elif instr[1]=='var':
                if instr[2][0]=='var':
                    t1,t=self.getValue(instr[2][1][0])
                    t2,t=self.getValue(instr[2][1][1])
                    parameter,t=self.getValue(instr[2][1][2])
                    instrum=self.getSymbol(self.env)
                    if instr[2][1][3][0]=='call':
                        instr[2][1][3][0]='callLater'
                        func,t=self.getValue(instr[2][1][3])
                        if len(func[1])+2!=func[2][2]:
                            self.printError('Wrong number of parameters calling function '+func[0])
                        self.song.insertModification(instrum[1][1],float(t1),float(t2),parameter,func,-1) #-1 -> is function
                    else:
                        v1,t=self.getValue(instr[2][1][3])
                        if t not in ['string','number']:
                            self.printError('string or number expected as fourth parameter of function var')
                        v2,t=self.getValue(instr[2][1][4])
                        if t not in ['string','number']:
                            self.printError('string or number expected as fifth parameter of function var')
                        self.song.insertModification(instrum[1][1],float(t1),float(t2),parameter,float(v1),float(v2))                       
            elif instr[1]=='put':
                if instr[2][0]=='put':
                    t1,t=self.getValue(instr[2][1][0])
                    parameter,t=self.getValue(instr[2][1][1])
                    instrum=self.getSymbol(self.env)
                    #v1,t=self.getValue(instr[2][1][2])
                    t=instr[2][1][2][0]
                    v1=self.getListValue(instr[2][1][2])
                    if t!='list':
                        self.printError('list expected as third parameter of function put')
                    #v1=self.getListValue(v1)
                    self.song.insertParameters(instrum[1][1],t1,parameter,v1)
            elif instr[1]=='define':
                code=compile(instr[3],'','exec')
                func_code = FunctionType(code.co_consts[0], globals(), instr[2])
                self.insertScoFunction(instr[2],[func_code,instr[4],instr[5]])
            else:
                self.printError('Unkown instruction '+instr[1])
        self.lineNumber=ant_lineNumber
        self.charNumber=ant_charNumber

    def getValue(self,a,isList=False):
        if isList and a[0] in ['number','string']: ### more?
            return a,a[0]
        if a[0] =='number':
            return a[1],a[0]
        elif a[0]=='string':
            return a[1],a[0]
        elif a[0]=='literal':
            return a[1],'identifier'
        elif a[0]=='identifier':
            t,v=self.getSymbol(a[1])
            if t=='':
                f=self.getScoFunction(a[1])
                if f[0]=='':
                    self.printError('Unkown variable ' + a[1])
                else:
                    return f[0],'function'
            return v,t
        elif a[0] in ['list','listVar','listMidi','listPitch']:
            a[1],t=self.getValue(a[1])
            return a,a[0]
        elif a[0]=='pattern':
            time,t=self.getValue(a[1][0])
            parts,t=self.getValue(a[1][1])
            if a[1][2][0]=='++': ### the '++' is here
                a[1][2][0]='+++' #create listVar inside a pattern definition
            pat,tp=self.getValue(a[1][2])
            modPat,t=self.getValue(a[1][3])
            n,t=self.getValue(a[1][4])
            if tp== 'listVar':
                pat,notes=self.extractPattern(pat,parts)
                pattern=[Pattern(time,parts,pat,modPat,n) ,notes, '.']
            else:  # string
                pattern=[Pattern(time,parts,pat,modPat,n)] #pat without the ' or "
            return pattern,'pattern'
        elif a[0]=='call':
            return self.callFunction(a[1][0],a[1][1])
        elif a[0]=='callLater':
            r=[]
            for e in a[1][1]:
                if type(e)==list:
                    ne,t=self.getValue(e,isList)
                    r.append(ne)
                else:
                    r.append(e)
            f=self.getScoFunction(a[1][0])
            if len(r)+2 !=f[2]:
                self.printError('Wrong number of parameters calling function '+a[1][0])
            return [a[1][0],r,f],'callLater'
        elif a[0]=='ftgen':
            return a[1:],'ftgen'
        elif a[0]=='index':
             array,tv=self.getValue(a[1])
             i,ti=self.getValue(a[2])
             if tv in ['list']: #,'listVar','listPitch','listMidi']:
                 element=array[1][int(i)]
                 t=array[1][int(i)][0]
                 if t not in ['list','listVar','listPitch','listMidi']:
                     element=element[1] #get off the type
             else:
                 self.printError(a[1][1] + ' is not an array')
                 #element,t=self.getValue(array[int(i)])
             return element,t
        elif a[0] in ['+++','++','+','-','*','/','%','^','||','&&','==','!=','>=','<=','<','>']:
            v1,t1=self.getValue(a[1])
            v2,t2=self.getValue(a[2]) 
            if a[0]=='+':
                return self.sumValues(v1,t1,v2,t2)
            elif a[0]=='++':
                return self.createVarlist(v1,t1,v2,t2) # normal`
            elif a[0]=='+++':
                return self.createVarlist(v1,t1,v2,t2,True) #inside a pattern definition
            elif a[0]=='-':
                return self.subValues(v1,t1,v2,t2)
            elif a[0]=='*':
                return self.mulValues(v1,t1,v2,t2)
            elif a[0]=='/':
                return self.divValues(v1,t1,v2,t2)
            elif a[0]=='%':
                return self.modValues(v1,t1,v2,t2)
            elif a[0]=='^':
                return self.expValues(v1,t1,v2,t2)
            elif a[0]=='&&':
                return self.andValues(v1,t1,v2,t2)
            elif a[0]=='||':
                return self.orValues(v1,t1,v2,t2)
            elif a[0]in['==','!=','>=','<=','<','>']:
                return self.compareValues(v1,t1,v2,t2,a[0])
        else:
            return a,'literal'
            #self.printError('Unkown instruction '+a[0])

    def callNotDefinedFunction(self,name,params):
        r=[]
        for x in params:
            val,t=self.getValue(x)
            if t=='string':
                val="'" + val + "'"
            r.append(str(val))
        try:
            f= name + '(' + ','.join(r) +')'
            v=eval(f)
            if v==None:
                return
        except Exception as e:
            self.printError(str(e))
        return self.execEval(str(v))


    def callFunction(self,name,params):
        v=self.getScoFunction(name)
        f=v[0]
        tf=v[1]
        if f=='' : #### or tf=='':
            return self.callNotDefinedFunction(name,params)
            self.printError('Function ' +  name + ' not defined')
        numParams=v[2]
        if numParams!=-1 and numParams!=len(params):
            self.printError('Wrong number of parameters calling function '+name)
        p=[]
        for x in params:
            val,t=self.getValue(x)
            if t in ['list','listVar','listPitch','listMidi'] :
                val=self.getListValue(val)
                if t in ['listPitch','listMidi'] :
                    for i in range(0,len(val)):
                        val[i]=val[i][0] #only the note, not the duration
                p.append(val)
            else:
                p.append(val)

        if f!='':
            if tf=='':
                f(*p)
            elif tf==0:
                return f(*p) #execEval
            elif tf=='any':
                r=f(*p)
                if isinstance(r,str):
                    return self.execEval(f(*p))
                else:
                    self.printError('Function ' +name +' should return a string')
            else:
                return f(*p),tf

    def getListValue(self,l):
        if not type(l)==list:
            return l
        r=[]
        t=l[0]
        if t in ['list','listVar','listPitch','listMidi'] :
            for e in l[1]:
                v=self.getListValue(e)
                r.append(v)
            return r
        elif t == 'identifier':
            r,t=self.getValue(l)
            return r
        else:
            return l[1]
                
        for e in l:
            if type(e)==list:
                v=e
                if True or t in ['list','listVar','listPitch','listMidi'] :
                    v=self.getListValue(v)
                    r.append(v)
                    
                else:
                    v,t=self.getValue(e)
                    r.append(v)
            else:
                v=e
                r.append(v)
        return r
                
    def readPatch(self):
        result=[]
        token,t=self.nextToken()
        while t!='section':
            if t=='\n':
                token,t=self.nextToken()
                continue

            if t=='identifier':
                t,v=self.getSymbol(token)
                if t=='instrument':
                    instrument1=v[1]
                else:
                    self.printError('instrument name expected')
            else:
                self.printError('instrument name expected')
            token,t=self.nextToken()
            n1=0
            if t=='[':
                n1,t=self.readExpression()
                n1=int(n1[1])
                self.expectToken([']'])
                token,t=self.nextToken()
            if t=='<<':
                s=t
            elif t=='>>':
                s=t
            else:
                self.printError('syntax error')
            token,t=self.nextToken()
            t,v=self.getSymbol(token)
            if t=='instrument':
                    instrument2=v[1]
            else:
                self.printError('instrument name expected')
            token,t=self.nextToken()
            n2=0
            if t=='[':
                n2,t=self.readExpression()
                n2=int(n2[1])
                self.expectToken([']'])
            if s=='<<':
                result.append([instrument1, n1, instrument2, n2])
            else:
                result.append([instrument2, n2, instrument1, n1])

            token,t=self.nextToken()
        return result 

    def connectInstruments(self):
        for c in self.connections:
            inputInstrument=c[0]
            ni=c[1]
            outputInstrument=c[2]
            no=c[3]
            if len(inputInstrument.inputs[ni])==0:
               if len(outputInstrument.zakOuts)>no:
                   inputInstrument.inputs[ni]=[outputInstrument] 
                   n=0
                   for o in outputInstrument.zakOuts[no]:
                       t=self.printType(o[1])
                       if o[2]==-1: #get a new zak number###all outputs must have a zak number
                           num=self.song.getZakNumber(t)
                           outputInstrument.zakOuts[no][n]=[o[0],t,num]
                       else:
                           num=o[2]
                       oi=[ni,n,t,num]
                       inputInstrument.inputs[ni].append(oi)
                       n+=1
               else:
                   self.printError('instrument '+ outputInstrument.name + " doesn't have output " + str(no))
            else:
                instr=inputInstrument.inputs[ni][0]
                self.printError('instrument ' + inputInstrument.name + ', input '+ str(ni)+ ' already connected to '+instr)
            
    def readEnd(self):
        token,t=self.nextToken()
        t1=-1
        t2=-1
        if token=='(':
            n,t=self.readExpression()
            if t=='number':
                n=self.getValue(n)[0]
                t1=float(n)
            token,t=self.nextToken()
            if t==',':
                n,t=self.readExpression()
                if t=='number':
                    n=self.getValue(n)[0]
                    t2=float(n)
            else:    
                self.printError('syntax error')
            token,t=self.nextToken()
            if t!=')':
                self.printError('syntax error')
            token,t=self.nextToken()
        i=[]
        while t=='identifier':
            i.append(token)
            token,t=self.nextToken()
        while token!='eof' and token!='#':
            token,t=self.nextToken()
            if t=='identifier':
                self.expectToken(['='])
                value,t=self.nextToken()
                if token=='options':
                    self.song.insertOption(value)
                token,t=self.nextToken()
            
        return self.write(i,t1,t2) 
            

    def insertTranslations(self,pattern):
        d=Dictionary()
        for k,v in self.symbolTable['general']['dictionary'].items():
            d.addTranslation([k,v])
        for k,v in self.symbolTable[self.env]['dictionary'].items():
            d.addTranslation([k,v])    
        pattern.setDictionary(d)

    def write(self,instr,t1,t2): 
        self.charNumber=-1
        self.env='local'

        self.connectInstruments()

        for instrument in self.song.orchestra.instruments: #second pass
            if type(instrument) is Instrument:
                par=instrument.mod_params
                instructions=instrument.instr
                name=instrument.name
                self.symbolTable['local']=instrument.table
                text=self.printInstrument(instrument,par,instructions)    
                instrument.text=text
                self.cleanSymbolTable('local')

        self.env='general'
        for line in self.song.orchestra.globalSection + self.song.orchestra.globalFunctions :
            r=''
            if line=='':
                continue
            if self.oldStyle(line[2][0]): # old style
                line[-2]=' '         # delete the = sign and the parenthesis
                line[-1][1]=' '
                line[-1][-1]=' '
            for i in line:
                r+=self.printSymbol(i,[],[])
            self.song.orchestra.globalText+=r+'\n'
        return self.song.asString(instr,t1,t2)

    def read(self):
        token,t=self.nextToken()
        while not token is None: # end of file
            if token=='#':
                token,t=self.nextToken()
            if token=='orchestra':
                self.state=self.ORCHESTRA
                g=self.readOrchestra()
                self.song.insertGlobal(g)
            elif token=='score':
                self.state=self.SCORE
                self.readScore()
            elif token=='patchboard':
                self.state=self.PATCH
                self.connections=self.readPatch()
            elif token=='end':
                return self.readEnd()
            elif token=='eof':
                return self.write([],-1,-1) 
            elif token=='\n':
                pass
            else:
                self.printError('unknown section '+token)
            token,t=self.nextToken()
            
    def searchFunctionSignature(self,fname):
        r,s=self.getOrcFunction(fname)
        return r,s  # return, arguments
        
    def initSignatures(self):
                                  #y=any (out type = first param type)
                                  #K=i or k, 
                                  #A=a or k, in doubt, a
                                  #B=a or k, in doubt, k 
                                  #x=a or k or i
        func=[
            ['abs',['y','y']],  
            ['ampdb',['y','y']],  
            ['ampdbfs',['y','y']],
            ['cent',['y','y']],
            ['cpspch',['y','y']],
            ['int',['y','y']],
            ['init',['y','y']],
            ['ftlen',['i','i']],
            ['octave',['y','y']],
            ['release',['k','']],
            ['sqrt',['y','y']],
        
            ['adsr',['B','iiiii']],
            ['ampmidi',['i','ii']],
            ['biquad',['a','akkkkkki']],
            ['bqrez',['a','axxi']],
            ['butterbp',['a','akki']],
            ['butterbr',['a','akki']],
            ['butterhp',['a','aki']],
            ['butterlp',['a','aki']],
            ['buzz',['a','xxkii']],
            ['comb',['a','akiii']],
            ['cpsmidi',['i','']],
            ['cpsmidinn',['i','K']],
            ['dcblock2',['a','aii']],
            ['diskin2',['a','ikiiiiii']],
            ['downsamp',['k','ai']],
            ['envlpx',['a','Xiiiiiii']], 
            ['expseg',['B','iii']], 
            ['expsegr',['B','iii']], 
            ['foscil',['a','xkxxkii']], 
            ['foscili',['a','xkxxkii']],
            ['grain',['a','xxxkkkiiii']], 
            ['grain3',['a','kkkkkkikikkii']],
            ['line',['B','iii']],
            ['linseg',['B','iiii']],
            ['loscil',['a','xkiiiiiiii']],
            ['loscil3',['a','xkiiiiiiii']],
            ['madsr',['B','iiiiii']],
            ['midiout',['_','kkkk']],
            ['midion',['_','kkk']],
            ['midion2',['_','kkkk']],
            ['moog',['a','kkkkkkiii']],
            ['moogladder',['a','aBBi']],
            ['moogvcf',['a','axxi']],
            ['moogvcf2',['a','axxi']],
            ['mxadsr',['B','iiiiiii']],
            ['noise',['a','xk']],
            ['noteon',['_','iii']],
            ['noteondur',['_','iiii']],
            ['noteondur2',['_','iiii']],
            ['nreverb',['a','akkiiiii']],
            ['oscil',['A','xxii']], 
            ['oscil3',['A','xxii']], 
            ['oscili',['A','xxii']], 
            ['oscils',['a','iiii']], 
            ['out',['_','a']],
            ['outs',['_','aa']],
            ['pan2',['a','axi']], 
            ['phasor',['B','xxi']], 
            ['pluck',['a','kkiiiii']], 
            ['poscil',['a','BBii']], ### return type?
            ['print',['_','i']], 
            ['pvsanal',['f','aiiiiii']], 
            ['pvsmaska',['f','fik']], 
            ['pvsynth',['a','fi']], 
            ['rand',['B','xiii']],
            ['reson',['a','axxi']],
            ['rezzy',['a','axxii']],
            ['reverb',['a','aki']],
            ['scantable',['a','kkiiii']],
            ['seed',['_','i']],
            ['sum',['a','aaaa']],
            ['table',['y','yiiii']],
            ['tablei',['y','yiiii']],
            ['table3',['y','yiiii']],
            ['tival',['i','']],
            ['turnoff',['_','']],
            ['vco',['a','xxikiiiiii']], 
            ['vco2',['a','kkikki']],
            ['vco2init',['i','iiiiii']],
            ['vdelay',['a','aaii']],
            ['vibrato',['k','kkkkkkkkii']],
            ['wgbow',['a','kkkkkkii']],
            ['xadsr',['B','iiiiii']],
            ['zacl',['_','kk']],
            ['zar',['a','k']],
            ['zaw',['_','ak']],
            ['zawm',['_','ak']],
           ]

        for f in func:
            self.insertOrcFunction(f[0],f[1])

    def initScoreFunctions(self):#####borrar
        func=[
              ['array',[lambda x: ['list']+[[['list',None]] * x],'list',1]], #the types inside the list must be defined
              ['eval',[self.execEval,0,1]],
              ['getTime',[self.execGetTime,'number',0]],
              ['getZakOut',[self.execGetZakOut,'list',2]],
              ['silence',[self.execSilence,'pattern',1]],
              ['tempo',[self.execTempo,'',1]],
              ['transposeNote',[self.execTranspose,'string',2]],
             ]
        for f in func:
            self.insertScoFunction(f[0],f[1])



    def execGetTime(self):
        instrument=self.env 
        if self.isInstrument(instrument):
            return self.song.getActualTime(instrument)
        else:
            return 0
    
    def execGetZakOut(self,instrument,n):
        for instru in self.song.orchestra.instruments:     
            if instrument==instru.name:
                if n>=len(instru.zakOuts):
                    self.printError('Instrument ' + instrument + '  does not have output ',str(n))
                out=instru.zakOuts[n]
                res=[]
                for o in out:
                    res.append(['number',o[2]])
                return ['list', res]
        self.printError('Instrument ' + instrument + '  not found') 

    def execEval(self,s):
        self.line = s+self.line
        value,t=self.readExpression()
        value,t=self.getValue(value)
        return value,t

    def execTempo(self,t):
        self.song.setTempo(self.env,t)

    def execTranspose(self,note,semitones):
    #the note is a string in octave pitch format    
        so,sn=note.split('.')
        n=int(sn)+semitones
        o=int(so)+ n//12
        n=n%12
        return str(o) + '.' + str(n).zfill(2)
        
    def execSilence(self,t):
        return [Pattern(t,1,'x','',0)]
             



inFile=''
outFile=''
if len(sys.argv)==2:
    inFile=sys.argv[1]
elif len(sys.argv)==3:
    inFile=sys.argv[1]
    outFile=sys.argv[2]
#elif len(sys.argv)==1:
#    inFile=sys.stdin
else:
    print('Error reading input')
    exit()

inter=Interpreter(inFile)
res=inter.read()
if outFile!='':
    f=open(outFile,'w')
    f.write(res)
    f.close()
else:    
    print(res)

