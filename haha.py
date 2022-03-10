class Person(object):

    isinstance = None

    def __init__(self, name, age):
        self.haha = name
        self.age = age

    def get(self):
        print(self.name)

    # def __call__(self, *args, **kwargs):
    #     print(f"{self.name}今年{self.age}")

    def __str__(self):
        return self.name + "傻逼"


if __name__ == '__main__':
    p1 = Person("戴志强", 10)
    print(p1.haha)