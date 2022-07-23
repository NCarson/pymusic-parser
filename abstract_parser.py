class AbstractParser:

    # if data kinds are the same we need not create 
    # a scratch file for interchange on the next parser pass
    data_kind = None

    def open(self, fname):
        raise NotImplimentedError()
    
    def parse(self, data):
        raise NotImplimentedError()
    
    def write(self, data):
        raise NotImplimentedError()

