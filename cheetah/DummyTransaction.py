
'''
Provides dummy Transaction and Response classes is used by Cheetah in place
of real Webware transactions when the Template obj is not used directly as a
Webware servlet.

Warning: This may be deprecated in the future, please do not rely on any 
specific DummyTransaction or DummyResponse behavior
'''

import types

try:
    from cStringIO import StringIO
except ImportError:
    import StringIO

class DummyResponseFailure(Exception):
    pass

class DummyResponse(object):
    '''
        A dummy Response class is used by Cheetah in place of real Webware
        Response objects when the Template obj is not used directly as a Webware
        servlet
    ''' 
    def __init__(self):
        self._outputChunks = StringIO()
       
    def flush(self):
        pass
        
    def write(self, value):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        self._outputChunks.write(value)


    def writeln(self, txt):
        write(txt)
        write('\n')

    def getvalue(self, outputChunks=None):
        #chunks = outputChunks or self._outputChunks
        try:
            if outputChunks is not None:
                return ''.join(outputChunks)
            else:
                return self._outputChunks.getvalue().decode('utf-8')
        except UnicodeDecodeError, ex:
            #not sure about the best way to check for non-unicode in StringIO
            nonunicode = ''
            if outputChunks:
                nonunicode = [c for c in outputChunks if not isinstance(c, unicode)]
            raise DummyResponseFailure('''Looks like you're trying to mix encoded strings with Unicode strings
            (most likely utf-8 encoded ones)

            This can happen if you're using the `EncodeUnicode` filter, or if you're manually
            encoding strings as utf-8 before passing them in on the searchList (possible offenders: 
            %s) 
            (%s)''' % (nonunicode, ex))


    def writelines(self, *lines):
        ## not used
        [self.writeln(ln) for ln in lines]
        

class DummyTransaction(object):
    '''
        A dummy Transaction class is used by Cheetah in place of real Webware
        transactions when the Template obj is not used directly as a Webware
        servlet.

        It only provides a response object and method.  All other methods and
        attributes make no sense in this context.
    '''
    def __init__(self, *args, **kwargs):
        self._response = None

    def response(self, resp=None):
        if self._response is None:
            self._response = resp or DummyResponse()
        return self._response


class TransformerResponse(DummyResponse):
    def __init__(self, *args, **kwargs):
        super(TransformerResponse, self).__init__(*args, **kwargs)
        self._filter = None

    def getvalue(self, **kwargs):
        output = super(TransformerResponse, self).getvalue(**kwargs)
        if self._filter:
            _filter = self._filter
            if isinstance(_filter, types.TypeType):
                _filter = _filter()
            return _filter.filter(output)
        return output


class TransformerTransaction(object):
    def __init__(self, *args, **kwargs):
        self._response = None
    def response(self):
        if self._response:
            return self._response
        return TransformerResponse()

