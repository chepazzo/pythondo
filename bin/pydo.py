#!/opt/bcs/bin/python -W ignore::DeprecationWarning

'''
Designed to allow other programming languages to access python classes
This python script is meant to be executed by any language (even bash).
It will take as args (encoded as a json string):
- class (absolute path)
- method
- args

It will return:
- output (return value) of method encoded as a json string
- instance id to be use to run methods on the same instance

Obviously, this works best with static classes, but hopefully, it will 
work out for some subset of instance classes as well.

The idea is to make this work like RPC/API on a web server, which would make 
adding functionality to use such an API relatively simple.
'''
__version__ = '0.1'

import sys
import json
import os
import pickle
import inspect

datalib = '/tmp/'
PEANUT_GALLERY = None
ORIG_STDOUT = None

class __ShutTheFUp(object):
    '''
        If we instantiate a noisy class that prints anything to the screen,
        the reply from this script will appear as *not* valid json.
        So, we need to quiet the noise.
        Then, we can send any comments from the chatty class 
        encoded into the json response.
        
        To shutup:
            tmpout = __ShutTheFUp()
            origout = sys.stdout
            sys.stdout = tmpout

        To restore:
            sys.stdout = origout

        To print suppressed output:
            print tmpout.output
    '''
    def __init__(self):
        self.output = ''
    def write(self, s): 
            self.output = self.output + s 

def main():
    suppressOutput()
    p = PyDo()
    action = p.args['action']
    if action == 'method':
        p.runMethodOnClass()
    elif action == 'set':
        p.setPropData()
    elif action == 'get':
        p.getPropData()
    elif action == 'cleanup':
        p.deleteClassData()
        p.reply('data',True)
        exit()
    else:
        ''' may as well assume method if no action set '''
        p.runMethodOnClass()
    p.storeClassData()
    p.reply('data',p.value)

def suppressOutput():
    global PEANUT_GALLERY
    global ORIG_STDOUT
    '''suppress class output'''
    PEANUT_GALLERY = __ShutTheFUp()
    ORIG_STDOUT = sys.stdout 
    sys.stdout = PEANUT_GALLERY
    return True

def restoreOutput():
    sys.stdout = ORIG_STDOUT
    return PEANUT_GALLERY.output

class PyDo(object):

 def __init__(self):
    global datalib
    self.datalib = datalib
    self.args = {
        'lib':'',
        'class':'',
        'method':'',
        'prop':'',
        'value':'',
        'instid':'',
        'args':[],
        'action':'new'
    }
    self.instance = None
    self.parseArgs()
    self.loadModule()
    self.loadClassData()

 def parseArgs(self):
    #print "sys.argv: "+str(sys.argv)
    if len(sys.argv) < 2:
        self.fail("No data sent")
    argv = sys.argv[1]
    #print "arg: "+argv
    argo = json.loads(argv)
    ret = {}
    #print "argo: "+str(argo)
    ''' 
     class and method are required 
    '''
    if 'class' not in argo:
        self.fail("You need to specify a class name")
    if 'method' not in argo:
        self.fail("You need to specify a method name")
    '''
     no other args are required 
    '''
    for arg in argo:
        self.args[arg] = argo[arg]
    classname = self.args['class']
    clparts = classname.split('.')
    #print "clparts: "+str(clparts)
    self.classname = clparts.pop()
    self.modname = '.'.join(clparts)
    self.instid = self.args['instid']
    return self

 def loadModule(self):
    if self.args['lib']:
        lib = self.args['lib']
        #print "sys.path.append('"+lib+"')"
        sys.path.append(lib)
    '''
    Import module and assign to self.mymodule
    This allows us to do create a new class instance like so:
        myclass = getattr(self.mymodule,self,classname)
        n = myclass()
    '''
    __import__(self.modname)
    self.mymodule = sys.modules[self.modname]
    '''
    If we ever upgrade to python 2.7, the above 2 lines should be replaced with:
        import importlib
        self.mymodule = importlib.import_module(self.modname)
    '''
    # old code below.  Leaving in for a single git cycle purely for 
    # documentation purposes.
    # Please delete on next commit
    '''
    importmodule using exec
    imporant to know that 'mymodule' is a local namespace
    and is unavailable when the function exits even if 
    'global mymodule' is used!
    '''
    '''
    yay!  no more exec!!
    '''
    #exec("import "+self.modname+" as mymodule")
    #self.mymodule = mymodule
    '''
    importmodule using __import__
    commented out because with a hierarchy (like docommand.do.Do)
    it is not obvious what part is imported globally
    '''
    #print "importing "+self.modname
    #print dir(self.mymodule)
    #print str(globals())
    return self

 def storeClassData(self):
    if not self.instid:
        self.instid = os.urandom(8).encode('hex')
    fname = self.datalib+"pydo."+self.instid+".data"
    with open(fname,'w') as fw:
        pickle.dump(self.instance,fw,-1)
    return self

 def deleteClassData(self):
    if self.instid:
        fname = self.datalib+"pydo."+self.instid+".data"
        os.remove(fname)
    return self

 def loadClassData(self):
    if not hasattr(self.mymodule,self.classname):
        self.fail("Non-existant class: "+str(self.mymodule)+"."+self.classname)
    self.classobj = getattr(self.mymodule,self.classname)
    if self.instid:
        fname = self.datalib+"pydo."+self.instid+".data"
        with open(fname,'r') as fr:
            self.instance = pickle.load(fr)
    return self

 def runMethodOnClass(self):
    args = self.args['args']
    '''
    set the method reference.  If creating a new instance, 
    the method is the class itself.
    '''
    classname = self.args['class']
    methodname = self.args['method']
    #print "running "+classname+"."+methodname+"("+str(args)+")"
    if methodname == 'new':
        self.methodobj = self.classobj
    #elif 'instance' in self:
    elif self.instance:
        if not hasattr(self.instance,methodname):
            self.fail("Non-existant method: "+methodname)
        self.methodobj = getattr(self.instance,methodname)
    ''' 
    store ref in 4char variable for brevity 
    '''
    meth = self.methodobj
    self.value = False
    '''
    allow for args to be either [] (positon) or {} (explicit)
    '''
    if isinstance(args,list):
        args = [str(i) for i in args]
        #print "ARGS: "+str(args)
        self.value = meth(*args)
    elif isinstance(self.args,dict):
        strargs = {}
        for k,v in args.iteritems():
            k = str(k)
            #print "Parsing key:value: "+k+":"+str(v)
            if isinstance(v,list):
                newv = []
                for l in v:
                    newv.append(str(l))
                v = newv
            elif isinstance(v,dict):
                v = dict((str(nk), str(nv)) for nk,nv in args.iteritems())
            elif v == True:
                v = True
            else:
                v = str(v)
            #print "adding strargs["+k+"] = "+str(v)
            strargs[k] = v
        #args = dict((str(k), v) for k,v in args.iteritems())
        args = strargs
        #print "ARGS: "+str(args)
        self.value = meth(**args)
    else:
        self.value = meth()
    '''
    Need to store new instance in self.instance
    Instance can't be stored as JSON, so need to return only 'True'
    '''
    if self.args['method'] == 'new':
        self.instance = self.value
        self.value = True
    #else:
        #self.value = self.instance.data
    return self

 def getPropData(self):
    prop = self.args['prop']
    if not hasattr(self.instance,prop):
        self.fail("Non-existant property: "+prop)
    pval = getattr(self.instance,prop)
    self.value = pval
    return pval

 def setPropData(self):
    prop = self.args['prop']
    val = self.args['value']
    if not hasattr(self.instance,prop):
        self.fail("Non-existant property: "+prop)
    pval = setattr(self.instance,prop,val)
    self.value = pval

 def getClassMethods(self):
    methods = {}
    props = {}
    for methname,methobj in inspect.getmembers(self.classobj, predicate=inspect.ismethod):
        methods[methname] = methobj
    for propname,propobj in inspect.getmembers(self.instance):
        props[propname] = str(propobj)
    self.methods = methods
    self.props = props
    return methods

 '''
    These methods take stock reply/fail args
    only change was adding the 'instid' field
    so that the calling program can reinstantiate the instance
    and the 'methods' field so the calling prog can
    recreate the structure
 '''
 def reply(self,field='data',value=[]):
    methods = self.getClassMethods()
    robj = {}
    robj['stat'] = 'ok'
    robj['instid'] = self.instid
    robj['methods'] = methods.keys()
    #robj['props'] = self.props.keys()
    robj[field] = value
    robj['classchat'] = restoreOutput()
    print json.dumps(robj,default=to_json)
    exit()
    
 def fail(self,txt='Unknown Failure'):
    robj = {}
    robj['stat'] = 'fail'
    robj['msg'] = txt
    robj['classchat'] = restoreOutput()
    print json.dumps(robj)
    exit()

def to_json(python_object):
    #if type(python_object).__name__=='instance':
    if isinstance(python_object,object):
        return {'__class__': python_object.__class__.__name__,
                '__value__': str(python_object)}
    else:
        return str(python_object)
    #raise TypeError(repr(python_object) + ' is not JSON serializable')

if __name__ == '__main__':
    main()
