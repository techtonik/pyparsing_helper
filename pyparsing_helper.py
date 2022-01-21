#!/usr/bin/python
'''
A GUI for getting immediate feedback while constructing and troubleshooting
pyparsing grammars.

See http://pyparsing.wikispaces.com/
http://pypi.python.org/pypi/pyparsing_helper

By Catherine Devlin (http://catherinedevlin.blogspot.com)
'''
from tkinter import *
from command_seq_reader import last_assignment_or_evaluatable
import pyparsing
import time, threading, functools, string, optparse, sys
__version__ = '0.1.2'

optparser = optparse.OptionParser()
optparser.add_option("-n", "--num-targets", help="Number of target panes to display",
                     dest="num_targets", default=3, action="store", type="int")
optparser.add_option("-l", "--lines", help="Height of grammar pane (in lines)",
                     dest="grammar_height", default=40, action="store", type="int")
optparser.add_option("-w", "--width", help="Width of pane (in characters)",
                     dest="grammar_width", default=40, action="store", type="int")

def _eq_monkeypatch(self, other):
    if isinstance(other, pyparsing.ParserElement):
        return self.__dict__ == other.__dict__
    elif isinstance(other, str):
        try:
            (self + StringEnd()).parseString(_ustr(other))
            return True
        except pyparsing.ParseBaseException:
            return False
    else:
        return super(pyparsing.ParserElement, self) == other

pyparsing.ParserElement.__eq__ = _eq_monkeypatch

class Application(Frame):
    grammar_height=40
    recalc_lag = 3.0
    def __init__(self, master=None, grammar_width=40, grammar_height=40, num_targets=3,
                 grammar = None):
        Frame.__init__(self, master)
        self.grid()
        self.recalc_timer = None
        self.grammar_height = grammar_height
        self.grammar_width = grammar_width
        self.num_targets = num_targets
        self.createWidgets()
        if grammar:
            self.grammar_text.insert(END, grammar)
        
    def restart_timer(self):
        if self.recalc_timer:
            self.recalc_timer.cancel()
        self.recalc_timer = threading.Timer(interval=self.recalc_lag, function=self.reparse)
        self.recalc_timer.start()
        
    def keypress(self, event):
        if event.keysym in string.printable:
            self.set_all_results('')
            self.restart_timer()
        
    def paste(self, event):
        event.widget.insert(CURRENT, self.clipboard_get())
    
    def keypress_i(self, event, i):
        if event.keysym in string.printable:
            self.set_result(i, '')
            self.restart_timer()

    def apply_grammar(self, i):
        try:
            target = getattr(self, 'target_text%d' % i).get(1.0, END)
            if self.parse_type.get() == 'scan':
                result = '\n----------\n'.join(r[0].dump() for r in self.grammar.scanString(target))
            elif self.parse_type.get() == 'transform':
                result = self.grammar.transformString(target)
            else:                
                result = self.grammar.parseString(target).dump()
        except Exception as e:
            result = f'{e.__class__}\n{e}'
        self.set_result(i, result)
        
    def set_result(self, i, txt):
        result = getattr(self, 'result_text%d' % i)
        result.config(state=NORMAL)
        result.delete(1.0, END)
        result.insert(END, txt)
        result.config(state=DISABLED)
    
    def set_all_results(self, txt):
        for i in range(self.num_targets):
            self.set_result(i, txt)
        
    def reparse(self, event=None):
        self.grammar = self.grammar_text.get(1.0, END).strip()
        if self.grammar:
            self.grammar = f'{self.import_type.get()}\n{self.grammar}'
            try:
                self.grammar = last_assignment_or_evaluatable(self.grammar, types_of_interest=(pyparsing.ParserElement))
                for i in range(self.num_targets):
                    self.apply_grammar(i)
            except Exception as e:
                if hasattr(e, 'text'):
                    errtxt = f'{e}\n\n{e.text}'
                else:
                    errtxt = str(e)
                self.set_all_results(errtxt)
        else:
            self.set_all_results('')
        self.restart_timer()

    def createWidgets(self):
        self.import_type = StringVar(self, value="from pyparsing import *")
        self.import_type_button1 = Radiobutton(self, variable=self.import_type, command=self.reparse,
                                               value="from pyparsing import *",
                                               text="from pyparsing import *")
        self.import_type_button2 = Radiobutton(self, variable=self.import_type, command=self.reparse, 
                                               value="import pyparsing",
                                               text="import pyparsing")
        self.import_type_button1.bind("<Activate>", self.reparse)
        self.import_type_button2.bind("<Activate>", self.reparse)
        self.import_type_button1.grid(column=0, row=0)
        self.import_type_button2.grid(column=0, row=1)
        self.parse_type = StringVar(self, value="parse")
        self.parse_type_button1 = Radiobutton(self, variable=self.parse_type,
                                              value="parse", text="parse", command=self.reparse)
        self.parse_type_button2 = Radiobutton(self, variable=self.parse_type,
                                              value="scan", text="scan/search", command=self.reparse)
        self.parse_type_button3 = Radiobutton(self, variable=self.parse_type,
                                              value="transform", text="transform", command=self.reparse)
        self.parse_type_button1.grid(column=1, row=0)
        self.parse_type_button2.grid(column=1, row=1)
        self.parse_type_button3.grid(column=1, row=2)
        self.go_button = Button(self, text='go')
        self.go_button.bind("<Button-1>", self.reparse)
        self.go_button.bind("<KeyPress-Return>", self.reparse)
        self.go_button.grid(column=2, row=0)
        Label(self, text='Grammar').grid(column=0, row=4)
        Label(self, text='Target').grid(column=1, row=4)
        Label(self, text='Result').grid(column=2, row=4)
        self.grammar_text = Text(self, width=self.grammar_width, height=self.grammar_height)
        self.grammar_text.bind("<FocusOut>", self.reparse)
        self.grammar_text.bind("<Any-KeyPress>", self.keypress)
        if not sys.platform[:3] == 'win':
            self.grammar_text.bind("<Control-v>", self.paste)
        self.grammar_text.grid(column=0, row=5, rowspan = self.num_targets)
        for target_num in range(0, self.num_targets):
            tgt = Text(self, height=self.grammar_height / self.num_targets, width=self.grammar_width)
            reparser = functools.partial(self.keypress_i, i=target_num)
            tgt.bind("<Any-KeyPress>", reparser)        
            tgt.bind("<FocusOut>", self.reparse)
            tgt.grid(column=1, row = 5 + target_num)
            if not sys.platform[:3] == 'win':
                tgt.bind("<Control-v>", self.paste)            
            setattr(self, "target_text%d" % target_num, tgt)
            scrl = Scrollbar(self)
            scrl.grid(column=3, row = 5 + target_num)
            result = Text(self, height=self.grammar_height / self.num_targets, width=self.grammar_width, 
                          takefocus=0, yscrollcommand=scrl.set)
            result.grid(column=2, row = 5 + target_num)
            setattr(self, "result_text%d" % target_num, result)
            scrl.config(command=result.yview)            
        self.last_parse_time = time.time()
          
def main():
    (opts, args) = optparser.parse_args()
    if args:
        grammarfile = open(args[0])
        grammar = grammarfile.read()
    else:
        grammar = ''
    app = Application(grammar=grammar, **opts.__dict__)
    app.master.title("PyParsing helper") 
    app.mainloop()

if __name__ == '__main__':
    main()
