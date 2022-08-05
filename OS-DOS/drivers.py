class KeyboardDriver:
    def GetInpt(self, msg):
        return input(msg)

class ScreenDriver:
    def display(self, msg, end='\n'):
        print(msg, end)
