print('imported: xuquant.strategy module')

class Dog():

    def __init__(self, sound='woof!', color='black') -> None:
        self.sound = sound
        self.color = color

    def bark(self):
        print(self.sound)