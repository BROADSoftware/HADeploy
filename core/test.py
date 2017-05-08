

class Plugin:
    def __init__(self):
        self.name = None
        self.path = None
    

class Context:
    def __init__(self):
        pass
        
        
        
    

def main():
    print "Allo"
    ctx = Context()
    ctx.xxx = "xxx"
    
    print ctx.xxx
    #print ctx.pluginByName['abc'].path

    x = ( 1, 3, 9)
    for a in x:
        print a
    
    y = [1, 2, 3]
    #y = [1]
    #y = [1,2]
    print y[:-1]
    print y[-1:]

if __name__ == "__main__":
    main()


