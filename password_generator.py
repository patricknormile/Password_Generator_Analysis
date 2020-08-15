
# In[]:
"""

I created a password generator that generates a random password that has several features:
    8 characters
    first character always a letter
    uses uppercase and lowercase letters
    no special characters
    at least one number
    no repeat characters (same case)
    no character used more than twice
    when typed, will use at least 3 key strokes from each hand 
    
The generator tests a proposed password, and accepts if it meets all the above criteria. otherwise it will try again

I want to see how often the generator can't generate a password on the first try, and what is the distribution

"""


import numpy as np
import matplotlib.pyplot as plt
import string
import pandas as pd
import collections
import itertools as it


class Setup():
    """
    Create lookup key for random number letter value/LR of keyboard
    """
    def __init__(self):
        A = list(string.ascii_lowercase)
        B = [str(i) for i in range(10)]
        C = list(string.ascii_uppercase)   
        A.extend(B)
        A.extend(C)
        # A is a list of all lowercase, uppercase, and single digit characters
        vals = []
        # Ll and LL are letters you would hit with a left finger while typing
        # LN are the digits you would hit with a left finger while typing
        Ll = ['a','b','c','d','e','f','g','q','r','s','t','w','x','z']
        LL = [x.upper() for x in Ll]
        LN = ['1','2','3','4']
        for i in A:
            # construct the lookup dictionary that assigns each lc/UC/int to a key and identifies if it would be typed with left or right hand
            if i in Ll or i in LL or i in LN:
                vals.append([i,'L'])
            else:
                vals.append([i,'R'])
        self.vals = vals
        
        self.keys = [*range(len(self.vals))]
        self.lookup = dict(zip(self.keys, self.vals))
        #end of Setup class


# In[]:
"""
this class generates a password and lets you know how many tries it took, and which criteria weren't met when it failed
"""


class Pwd(Setup):
    """
    This class generates random passwords
    Each instance inherits the Setup class and a class attribute is assigned to the lookup created in Setup
    """
    lookup = Setup().lookup
    
    def __init__(self):
        pass
    def generate(self):
        i = 0
        end = False
        n = len(self.lookup.keys())
        smpl = [*range(n)]
        self.failreason = []
        self.fails = []
        #get a set of 8 random numbers to test a password
        while end != True and i < 100:
            
            i += 1
            #generate potential password
            test = np.random.choice(smpl, 8)
            test_pwd = ''.join([list(self.lookup.values())[x][0] for x in test])
            
            # Create tests to see if password will work
            
            LR = [list(self.lookup.values())[x][1] for x in test]
            n_lc = len([x for x in test if x < 26])
            n_UC = len([x for x in test if x >= 36])
            n_N = len([x for x in test if x >= 26 & x < 36])
            
            #check if you don't use the same character too many times
            ltest = [*test]
            freqval = max(set(ltest), key=ltest.count)
            freqvalfreq = len([x for x in test if x == freqval])
            if freqvalfreq < 3:
                valfreq = 1
            else:
                valfreq = 0
            
            #check if starting char is a letter
            strt = test[0]
            if strt < 26 or strt >= 36:
                strt_cond = 1
            else:
                strt_cond = 0
                
            #check if you use Left and Right hand to type the password enough times
            n_minLR = min([LR.count('L'), LR.count('R')]) 
            if n_minLR < 3:
                minLR = 0
            else:
                minLR = 1
            
            #check if consecutive character shows up multiple times
            same = [test[i] == test[i-1] for i in range(1,8)]
            if same.count(True) > 0 :
                rep_check = 0
            else:
                rep_check = 1
            
            #combine all checks
            all_check = [n_lc, n_UC, n_N, valfreq, strt_cond, minLR, rep_check]
            if min(all_check) > 0 :
                end = True
                self.password = test_pwd
                self.ntries = i
            else :
                """
                note: 
                0 - no lowercase
                1 - no UPPERCASE
                2 - no numbers
                3 - char appears too often
                4 - starts with number
                5 - not enough L/R
                6 - repeated chars
                """
                self.password = "Failed to generate password" #if exceeds 100 (highly unlikely)
                self.ntries = i
                self.fails.append(test_pwd)
                #keeps track if multiple criteria were not met
                fr = ','.join([str(i) for i,x in enumerate(all_check) if x == 0])
                self.failreason.append(fr)
                

            
            
            
        
# See examples:  
A = Pwd()
A.lookup
A.generate()
print(A.password)
print(A.ntries)
print(A.failreason)
print(A.fails)

# In[]:
"""

See distribution of attempts needed to make a password

"""
A = Pwd()
cmpl_dist = {}
for i in range(50000):
    A.generate()
    cmpl_dist.update({i : [A.ntries, A.failreason]})

# In[]:
df = pd.DataFrame.from_dict(data = cmpl_dist, orient='index', columns=['Tries', 'Fail Reason'])

print(max(df['Tries']))

print(df.groupby('Tries')['Tries'].agg('count'))
lb = min(df['Tries'])
ub = max(df['Tries'])
#center histogram around integers
bucks = np.arange(lb-0.5, ub+0.5, 1)
plt.figure(figsize=(10,7))
plt.hist(data = df, x = 'Tries', bins = bucks, density=True)
plt.title("No. tries until success")
plt.show()

# In[]:
#looks very much like exponential distribution
plt.figure(figsize=(10,7))
plt.hist(data = df, x = 'Tries', bins = bucks, density=True, log=True)
plt.title("No. tries until success (log)")
plt.show()

dist = df.groupby('Tries')['Tries'].agg('count').div(df.shape[0])
dist
print(df['Tries'].mean())


# In[]:
print(dist)

# probability 2 or more tries
print(dist.loc[2:].sum())


# In[]:
"""
fail reasons: 
0 - no lowercase
1 - no UPPERCASE
2 - no numbers
3 - char appears too often
4 - starts with number
5 - not enough L/R
6 - repeated chars
"""
# count up how many failures from each
F = df['Fail Reason']
packstr = ''
for i,v in F.items():
    if v != []:
        packstr = packstr  + ','.join(v) + ','
#packstr

# In[]:
#count up how many by fail reason (keep in mind, could have multiple failures per iteration)
upackstr = packstr[:-1].split(',')
print(len(upackstr))
errcnt = {}
for i in range(7):
    errcnt.update({i : upackstr.count(str(i))})
cnts = pd.DataFrame.from_dict(data = errcnt, orient = 'index', columns = ['Count'])
cnts.index = ['0 - no lowercase', '1 - no UPPERCASE', '2 - no numbers', '3 - char appears too often', 
              '4 - starts with number', '5 - not enough L/R', '6 - repeated chars']
print(cnts.div(len(upackstr)))
_, ax = plt.subplots()
ax.pie(cnts.values.flatten(), labels = cnts.index, autopct='%1.1f%%')
ax.axis('equal')
plt.show()

# In[]:
ls = [*df['Fail Reason'].values]
mrgls = list(it.chain.from_iterable(ls))
print(len(mrgls))

inst = collections.Counter(mrgls)
inst.items()

