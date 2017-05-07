from lexicale import Lexicale
from pprint import pprint
import copy
import pdb 
import sys 

sys.setrecursionlimit(100000000)

class Grammar(object):
    def __init__(self, scanner):
  
        # lecxicale handler
        self.scanner = scanner

        # result
        self.result = list()
        
        # non-terminal symbols
        self.non_ts = []

        # terminal symbols 
        self.ts = []

        # productions
        self.pros = []

        # closures
        self.states = []
        
        # analyze_table
        self.analyze_table = {}


    def initialize(self, productions):
        symbol_map = {"+":"ADD",
                      "-":"SUB",
                      "*":"MUL",
                      "/":"DIV",
		      ";":"SEMI",
                      "==":"EE",
                      "=":"EQ",
                      ">":"GT",
                      "<":"LT",
                      ">=":"GE",
                      "<=":"LE",
                      "<>":"NE",
                      "(":"LP",
                      ")":"RP"}
        keywords = ["WHILE", "IF", "DO", "ELSE", "THEN"]
        raw_productions = productions.replace(' ','').split('\n')
        self.pros = []
        for p in raw_productions:
            if not p:
                continue
            temp = list(eval(p[3:]))
            for i in range(len(temp)): 
                if temp[i].isalpha():
                    if not temp[i].isupper():
                        temp[i] = temp[i].upper()
                        if (temp[i] not in self.non_ts) and temp[i] not in self.ts:
                            self.ts.append(temp[i])
                if temp[i] in symbol_map.keys():
                    self.ts.append(symbol_map[temp[i]])
                temp[i] = temp[i].replace(temp[i], symbol_map.get(temp[i], temp[i]))
            self.pros.append([p[0]] + temp)
        for p in self.pros:
            if p[0] not in self.non_ts:
                self.non_ts.append(p[0])
        self.ts.append('$')
        self.print(self.pros, "Productions")
        self.print(self.ts, "Terminal symbols")
        self.print(self.non_ts, "Non-terminal symbols")
        self.get_all_states()
        #self.get_follow('Q')
        #self.print(self.states, "All States")
        #self.states = [[(0, 1)], [(0, -1), (1, 2)], [(2, -1), (3, 2)], [(4, -1)], [(5, 2)], [(6, -1)]]
        #self.forward([(0,-1),(1,2)])




    def forward(self, state):
        #pdb.set_trace() 
        self.print(state[0], "begin_state")
        goto = {'Action':{},'Goto':{}}
        for t in self.ts:
            goto['Action'][t] = None
        for nt in self.non_ts:
            if nt != 'Q':
                goto['Goto'][nt] = None 
        raw_closure = copy.deepcopy(state[0]) + self.get_closure(state[0])
        next_states = []

        X = []
        closure = []
        #self.print(raw_closure, "state_closure_before")
        #self.print(closure, "state_closure_before")
        for c in raw_closure:
            if  c[1] == -1 or self.pros[c[0]][c[1]] == "NULL":
                for i in self.get_follow(self.pros[c[0]][0]):
                    if i == '$' and self.pros[c[0]][0] == 'Q':
                        goto['Action'][i] = 'accept'
                    else:
                        goto['Action'][i] = 'r'+ str(c[0])

                continue
            closure.append(c)
            temp = self.pros[c[0]][c[1]]
            if temp not in X:
                X.append(temp)
        if not closure:
            #self.print(X, "Can NOT forward")
            return next_states
        #self.print(closure, "state_closure_before")
        self.print(X, "forward_symbol")
        for x in X:
            next_state=[]
            for pro in closure:
                if pro[1] == -1:
                    continue
                if self.pros[pro[0]][pro[1]] == x:
                    if (pro[0], pro[1]+1) not in next_state:
                        if (pro[1]+1) == len(self.pros[pro[0]]):
                            next_state.append((pro[0], -1))
                        else:
                            next_state.append((pro[0], pro[1]+1))
            if  next_state != []:
                
                index =  self.check_duplicate(next_state)
                if not index:
                    self.states.append(copy.deepcopy(next_state))
                    index =  len(self.states)-1 
                    next_states.append(index)
                print('x: '+x+' index:'+str(index))
                if x in self.ts:
                    goto['Action'][x] = 's' + str(index)
                elif x in self.non_ts:
                    goto['Goto'][x] = index
        
        self.print(goto, "goto")
        self.analyze_table[str(state[1])] = copy.deepcopy(goto)
        return copy.deepcopy(next_states)
            



    def get_all_states(self):
        nas_list = []

        # state 0
        self.states.append([(0,1)])
        nas_list.append(([(0,1)], 0))
        while(nas_list):
            nas_state = nas_list.pop()
            temp = self.forward(nas_state)
            for t in temp:
                nas_list.append((copy.deepcopy(self.states[t]), t))
        self.print(self.states, 'ALL_states')
        self.print(self.analyze_table, 'Analyze Table')
            
            

            
    def get_closure(self, pros):
        pprint(pros)
        #print("GET_CLOSURE===========START=")
        closure = []

        marked = []
        #self.print(pros, "Get_closure")
        while(pros):
            pro = pros.pop()
            if pro[1] == -1:
                continue
            for p in self.pros:
                if p[0] == self.pros[pro[0]][pro[1]]:
                    if (self.pros.index(p), 1) not in closure:
                        closure.append((self.pros.index(p), 1))
                    if p[1] not in marked:
                        pros.append((self.pros.index(p), 1))
                        marked.append(p[1])
        #pprint(closure)
        #print("GET_CLOSURE===========END=")
        return closure

    def print(self, list, flag):
        print("#----%s----len:%s#" % (flag, len(list)))
        pprint(list)
        print("#----%s----#\n" %flag)

    def check_duplicate(self, closure):
        #print("CHECK=======================")
        #self.print(self.states, "check_states")
        #self.print(closure, "check_closure")
        if self.states == []:
            return False
        index = 0
        for i in range(0, len(self.states)):
            if len(closure) != len(self.states[i]):
                continue
            flag1 = True
            for p in range(0, len(closure)):
                if closure[p] != self.states[i][p]:
                    flag1 = False
            index = i
            if flag1:
                #print("++CHECK================Exists,index:(%s)===" %index )
                return index
        #print("CHECK====================False===\n")
        return False

    def get_first(self, index):
        first = []
        has_check = []
        stack = [index]
        while(True):
            if not stack:
                break
            pro = stack.pop()
            if pro not in has_check:
                for p in self.pros:
                    if p[0] == pro:
                        stack.append(p[1])
            if pro in self.ts and pro not in first:
                first.append(pro)
            has_check.append(pro)
        #self.print(first, index)
        return first


    def dir_follow(self, non_ts, follow):
        #print("Search " + non_ts)
        #self.print(follow, "BEFORE " + non_ts)
        if non_ts == 'Q' and '$' not in follow:
            #print("ADD $")
            follow.append('$')
        for pro in self.pros:
            if non_ts in pro[1:]:
                #self.print(pro, "Found")
                index = pro[1:].index(non_ts) + 1
                #print("index" + str(index))
                if index > 0:
                    if index == len(pro) - 1:
                        #self.print(pro, "....")
                        self.dir_follow(pro[0], follow)
                    else:
                        #print(pro)
                        temp = self.get_first(pro[index+1])
                        for ts in temp:
                            if ts != 'NULL' and ts not in follow:
                                #print("ADD "+ ts)
                                follow.append(ts)
                        if 'NULL' in temp:
                            self.dir_follow(pro[0], follow)
        #self.print(follow, "non_ts FOLLOW:" + non_ts)

    def get_follow(self, non_ts):
        follow = []
        self.dir_follow(non_ts, follow)
        #self.print(follow, "result")
        return follow

                    
                

if __name__ == "__main__":
    code = """
    int a;
    int b=5;
    float c=1.222;
while(a < 40)
    if (a>=4)
        b=5;
    then
        a=c;
    else
        a=b; """
    #code = input("Please input your code:\n")

    # lexicale section
    scanner = Lexicale()
    #tokens, symbol_table = scanner.scan(code)
    print("\nTOKENS:")
    #for token in tokens:
    #   print(token)
    print("\nSYMBOL_TABLE:")
    #for symbol in symbol_table:
    #    print(symbol)

    # grammar section
    productions1 = """
            Q->('E')
            E->('E','+','T')
            E->('T',)
            T->('T','*','F')
            T->('F',)
            F->('(','E',')')
            F->('id',)
    """
    productions2 = """
            P->('D','S')
            D->('id', ';', 'D')
            D->('null',)
            L->('int',)
            L->('float',)
            S->('id','=','E', ";")
            S->('if','(','C',')','S')
            S->('if','(','C',')','S','else','S')
            S->('while','(','C',')','S','do','S',';')
            S->('S',';','S')
            C->('E','>','E')
            C->('E','<','E')
            C->('E','==','E')
            E->('E','+','E')
            E->('E','-','E')
            E->('T',)
            T->('F',)
            T->('T','*','F')
            T->('T','/','F')
            F->('(','E',')')
            F->('id',)
            F->('int10',)
    """
    analyzer = Grammar(scanner)
    analyzer.initialize(productions1)
