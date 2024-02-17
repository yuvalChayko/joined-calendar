import dis

def hellof(name):
    print(f"hello {name}")

def hello(name):
    print("hello {}".format(name))

def add(a, b):
    return a + b

print(dis.dis(hello))
print("\n\n 111111111111111 \n\n")
print(dis.dis(hellof))
print("\n\n 111111111111111 \n\n")
print(dis.dis(add))
