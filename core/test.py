

import yaml    
from StringIO import StringIO

def dumpObj(obj):
    stream = StringIO()
    dumpMap("  ", obj, stream)
    return stream.getvalue()

def dumpMap(prefix, obj, out):
    for k, v in obj.iteritems():
        if type(v) is int:
            out.write("{0}{1}: {2}\n".format(prefix, k, v))
        elif type(v) is str:
            out.write("{0}{1}: \"{2}\"\n".format(prefix, k, v))
        else:
            pass
        

def main():
    print "Allo"
    obj = yaml.load(open("../../workbench/jdchive/testtable1/initial.yml"))
    
    obj1 =  obj['tables'][0]
    
    print "-----------------------------------------------"
    print yaml.dump(obj1)
    print "-----------------------------------------------"
    print dumpObj(obj1)
    
if __name__ == "__main__":
    main()


