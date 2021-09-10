import numpy as np

M=np.arange(2,27,1)
print (M)
print()

M=M.reshape(5,5)
print(M)
print()

M[1:4,1:4]=0
print(M)
print()

M=M@M
print(M)
print()

N=M[0,0:]
a=np.sqrt(sum(i**2 for i in N))
print(a)
