# test

def addTwoNumbers(a, b):
    sum = a + b
    return sum


def addList(l1):
    sum = 0
    for i in l1:
        sum += i
    return sum



add = lambda x, y : x + y

num1 = 1
num2 = 2

print("The sum is ", addTwoNumbers(num1, num2))

numlist = (1, 2, 3)

print(add(10, 20))

print("The sum is ", addList(numlist))

for i in range(16, 11, -1):
    print(i)

print([x for x in range(16) if x > 2])

x = ('apple', 'banana', 'cherry')
y = enumerate(x)
print(list(y))

dict1 = {i: i**2 for i in range(1, 11)}

print(dict1)

txt = "The rain in Spain stays mainly in the plain"
x = "ain"  in txt
print(x)


def finite_sequence():
    num = 0
    while num < 10000:
        yield num
        num += 1


def tupletest():
    return 1, 2

x,y = tupletest()


print(tupletest(), x, y)
