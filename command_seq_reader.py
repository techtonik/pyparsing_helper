r"""
last_assignment_or_evaluatable should return the last value assigned or otherwise
referred to in a stack of Python commands.

>>> last_assignment_or_evaluatable('a=1')
1
>>> last_assignment_or_evaluatable('a = 1\nb = 2')
2
>>> last_assignment_or_evaluatable('beast = "cow"\nx = 22\nbeast')
'cow'
>>> last_assignment_or_evaluatable('f=4.0\ni=7\ntarget=f')
4.0
>>> last_assignment_or_evaluatable('f=4.0\ni=7\ntarget=f', types_of_interest=(int,))
7
"""

import unittest, doctest, re

commandUnfinished = re.compile('unexpected EOF while parsing|EOL while scanning|unexpected character after line continuation character')
                    
def items_of_interest(dct, types_of_interest):
    return [(k, v) for (k, v) in dct.items() if isinstance(v, types_of_interest)]

def recordingexec(arg, types_of_interest = (int, basestring)):
    cmdbuf = []
    lastlocals = []
    for line in arg.strip().splitlines():
        cmdbuf.append(line)
        try:
            oldlocals = items_of_interest(locals(), types_of_interest)
            commnd = '\n'.join(cmdbuf)
            exec(commnd)
            newlocals = [itm for itm in 
                         items_of_interest(locals(), types_of_interest)
                         if itm not in oldlocals]
            if newlocals:
                lastlocals = newlocals
            lastcmd = '\n'.join(cmdbuf)
            cmdbuf = []
        except SyntaxError, e:
            if not commandUnfinished.search(str(e)):
                raise
        except Exception, e:
            raise Exception, '%s:\n%s' % (e, commnd)
    return (lastcmd, dict(lastlocals))
                   
def last_assignment_or_evaluatable(s, types_of_interest=(basestring, int, float)):
    s = s.strip()
    if not s:
        return None
    exec(s)
    (lastcmd, lastlocals) = recordingexec(s, types_of_interest)
    try:
        return eval(lastcmd)
    except SyntaxError, e:
        if 'invalid syntax' not in str(e):
            raise
    if len(lastlocals) > 1:
        raise ValueError, "Multiple assignments - couldn't determine which one"
    return eval(lastlocals.keys()[0])

class RecordingExecTestSuite(unittest.TestCase):
    def testSimpleAssignments(self):
        (lastcmd, lastlocals) = recordingexec('''
a = 1
b = "cow"
c = 3''')
        self.assertEqual(lastcmd, 'c = 3')
        self.assertEqual(lastlocals, {'c': 3})
    def testIgnoreObj(self):
        (lastcmd, lastlocals) = recordingexec('''
a = 1
b = 2
uts = unittest.TestSuite()
''', (unittest.TestSuite))
        self.assertEqual(lastcmd, 'uts = unittest.TestSuite()')
        self.assertEqual(lastlocals.keys(), ['uts'])
    def testExecutableLastLine(self):
        (lastcmd, lastlocals) = recordingexec('''
a = 1
print "hi mom"''')
        self.assertEqual(lastcmd, 'print "hi mom"')
        self.assertEqual(lastlocals, {'a': 1})
    def testEvalLastLine(self):
        (lastcmd, lastlocals) = recordingexec('''
a = 1
a''')
        self.assertEqual(lastcmd, 'a')
        self.assertEqual(lastlocals, {'a': 1})

class last_assignment_or_evaluatableTestSuite(unittest.TestCase):
    def testSimpleAssignments(self):
        lv = last_assignment_or_evaluatable('''
a = 1
b = "cow"
c = 3''')
        self.assertEqual(lv, 3)
    def testSimpleAssignments(self):
        lv = last_assignment_or_evaluatable('''
a = 1
b = "cow"
c = 3
b''')
        self.assertEqual(lv, 'cow')
    def testMultiAssignFail(self):
        self.assertRaises(ValueError, last_assignment_or_evaluatable, '''
a = 1
(b, c) = (2, 3)''')
    def testEmpty(self):
        lv = last_assignment_or_evaluatable('')
        self.assertEqual(lv, None)
    
if __name__ == '__main__':
    #unittest.main()
    doctest.testmod()