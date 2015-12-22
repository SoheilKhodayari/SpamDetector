from collections import defaultdict

#Mumur hash
def murmur3_x86(word, seed = 0):
    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    length = len(word)
    h1 = seed
    roundedEnd = (length & 0xfffffffc)  # round down to 4 byte block
    for i in range(0, roundedEnd, 4):
      # little endian load order
      k1 = (ord(word[i]) & 0xff) | ((ord(word[i + 1]) & 0xff) << 8) | \
           ((ord(word[i + 2]) & 0xff) << 16) | (ord(word[i + 3]) << 24)
      k1 *= c1
      k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17) # ROTL32(k1,15)
      k1 *= c2

      h1 ^= k1
      h1 = (h1 << 13) | ((h1 & 0xffffffff) >> 19)  # ROTL32(h1,13)
      h1 = h1 * 5 + 0xe6546b64

    # tail
    k1 = 0

    val = length & 0x03
    if val == 3:
        k1 = (ord(word[roundedEnd + 2]) & 0xff) << 16
    # fallthrough
    if val in [2, 3]:
        k1 |= (ord(word[roundedEnd + 1]) & 0xff) << 8
    # fallthrough
    if val in [1, 2, 3]:
        k1 |= ord(word[roundedEnd]) & 0xff
        k1 *= c1
        k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17)  # ROTL32(k1,15)
        k1 *= c2
        h1 ^= k1

    # finalization
    h1 ^= length

    # fmix(h1)
    h1 ^= ((h1 & 0xffffffff) >> 16)
    h1 *= 0x85ebca6b
    h1 ^= ((h1 & 0xffffffff) >> 13)
    h1 *= 0xc2b2ae35
    h1 ^= ((h1 & 0xffffffff) >> 16)

    return h1 & 0xffffffff

def Hash1(word):
	word=word.lower()
	Prime_Num=7
	h_code=Prime_Num
	for ch in word:
        #31 can be a bigger prime but causes less speed
		h_code=h_code*31+ord(ch)
	return h_code


def Hash2(num):
        res=0
        for i in range(0,len(num)):
            letter=num[i]
            value=ord(letter)
            res += value * (pow(31,i));
        return res

def Hash(word):
    #won't be zero anyway
    return Hash2(Hash1(word))


def overrides(interface_class):
    def overrider(method):
        assert(method.__name__ in dir(interface_class))
        return method
    return overrider

class D(defaultdict):
   def __init__(self,*arg,**kw):
      super(D, self).__init__(*arg, **kw)
      
   @overrides(defaultdict)
   def __hash__(self,*arg):
        return Hash(*arg) # TO DO : Stronger Hash Open Addressing

##############################Open Addressing
slot=list() # contains pair tuples
num_slots=len(slot)
def Hash(obj):
    pass
def pair(key,value):
    pair = (key,value)
    return pair

def find_slot(key):
    i=Hash % num_slots
    # search until we either find the key, or find an empty slot.
    while slot[i]  and slot[i][0] != key:
        i=(i+1)%num_slots
    return i

def lookup(key):
    i=find_slot(key)
    if slot[i]:
        return slot[i][1] # return slot[i].value
    else:
        return -1 #not found


def Set(key,value):
    i=find_slot(key)
    if slot[i] :
        slot[i][1]=value
        return 0
    #if the table is almost full
    #    rebuild the table larger (note 1)
    #    i = find_slot(key)
    slot[i][0]=key
    slot[i][1]=value

    return 0


