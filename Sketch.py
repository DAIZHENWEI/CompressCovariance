from sklearn.utils import murmurhash3_32 
import numpy as np
import array
import math
import heapq
np.random.seed(101)
from random_number_generator import ConsistentRandomNumberGenerator as CRNG

def Hfunction(m, seed):
    #if seed is None:
    #  seed = np.random.randint(0,100000)
    return lambda x : murmurhash3_32(key=x, seed=seed, positive=True) % m

def Gfunction(seed):
    #if seed is None:
    #  seed = np.random.randint(0,100000)
    return lambda x : np.sign(murmurhash3_32(key=x, seed=seed))


class TopKDs() :
    ''' This is a data structure for top k elements 
        To optimize find, insert, delete minimum and update operations
        we implement the datastructure by maintaining a hashmap (dictionary) 
        and heap. Note that O(log(n)) time is not possible by maintaining only 
        one of these
    '''
    def __init__(self,k):
        self.capacity = k;
        self.dictionary = {}
        self.heap = []
    def show(self):
        print(self.capacity)
        print(self.dictionary)
        print(self.heap)
    def insert(self,key, count):
        # if size of dictionary < capactiy then just ad
        if key in self.dictionary :
            self.dictionary[key] = count
        elif len(self.dictionary) < self.capacity:
            self.dictionary[key] = count
            heapq.heappush(self.heap, (count, key))
        else :
            # size = capacity and key is not present
            while True:
                top = heapq.nsmallest(1, self.heap)[0]
                if count <= top[0]:
                    # incoming element is of lesser count
                    break
                elif top[0] < self.dictionary[top[1]]:
                    # top elements count is not updated
                    heapq.heappop(self.heap)
                    heapq.heappush(self.heap, (self.dictionary[top[1]], top[1]))
                elif top[0] < count:
                    # incoming element is greater. remove old element and add new one
                    heapq.heappop(self.heap)
                    del self.dictionary[top[1]]
                    heapq.heappush(self.heap, (count, key))
                    self.dictionary[key] = count
                    break
                    
    def getTop(self):
        return self.dictionary
   
    
    

class CountSketch() :
    def __init__(self,d, R, topK=None):
        ''' d: number of hash functions
            R: range of the hash function. i.e. the memory
                to be used for count sketch
        '''
        self.d = d
        self.R = R
        # set of hash functions h and g
        self.hs = []
        self.gs = []
        self.h_crng = CRNG(101)
        self.g_crng = CRNG(501)
        self.h_seeds = self.h_crng.generate(self.d)
        self.g_seeds = self.g_crng.generate(self.d)
        for i in range(0, self.d):
            self.hs.append(Hfunction(self.R, self.h_seeds[i]))
            self.gs.append(Gfunction(self.g_seeds[i]))
        self.sketch_memory = np.zeros((self.d, self.R))

        self.topkds = None
        if topK is not None:
            self.topkds = TopKDs(topK)

    def insert(self, key, value=1): 
        for i in range(0, self.d):
            self.sketch_memory[i][self.hs[i](key)] = self.sketch_memory[i][self.hs[i](key)]  +  value * self.gs[i](key);
        if self.topkds is not None:
            count = self.query(key)
            self.topkds.insert(key, count)

    def query(self,key): 
        vs = []
        for i in range(0, self.d):
            vs.append(self.sketch_memory[i][self.hs[i](key)]*self.gs[i](key))
        vs = np.sort(vs)
        #print(vs)
        if self.d %2 == 1:
            return vs[self.d//2]
        else:
            return (vs[self.d//2 - 1] + vs[self.d//2])/2



class CountMinSketch() :
    def __init__(self,d, R, topK=None):
        ''' d: number of hash functions
            R: range of the hash function. i.e. the memory
                to be used for count sketch
        '''
        self.d = d
        self.R = R
        # set of hash functions h and g
        self.hs = []
        self.crng = CRNG(101)
        self.seeds = self.crng.generate(self.d)
        for i in range(0, self.d):
            self.hs.append(Hfunction(self.R, self.seeds[i]))
        self.sketch_memory = np.zeros((self.d, self.R))
        self.topkds = None
        if topK is not None:
            self.topkds = TopKDs(topK)

    def insert(self,key, value=1): 
        for i in range(0, self.d):
            self.sketch_memory[i][self.hs[i](key)] = self.sketch_memory[i][self.hs[i](key)]  +  value
        if self.topkds is not None:
            count = self.query(key)
            self.topkds.insert(key, count)

            
    def query(self,key): 
        value = None
        for i in range(0, self.d):
            if value is None:
                value = self.sketch_memory[i][self.hs[i](key)]
            else:
                value = min(value, self.sketch_memory[i][self.hs[i](key)])
        return value

