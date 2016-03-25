# g = (x * x for x in range(5))
# for i in g:
#     print(i)
#
# for i in g:
#     print('hello')
#     print(i)
#
#
# class Hello:
#     def say(self):
#         print('Hello')
#
#     @classmethod
#     def f(cls):
#         print('hello')
#
#     @staticmethod
#     def sf():
#         print('hello world')
#
# print('helo')
# Hello.f()
# Hello.sf()
# Hello().sf()
# h = Hello()
# h.f()
# h.say()
# h.sf()

gifts = [1, 2, 2, 2, 3, 2]

n = 6
d = {}

for x in gifts:
    d[x] = 0

for i in gifts:
    d[i] += 1
    if d[i] > n / 2:
        print(i)
