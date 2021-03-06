from random import uniform

class simulationclass:
    def __init__(self, **kwargs):
        self.error=False
        if ('minimum' not in kwargs) or ('maximum' not in kwargs):
            self.error=True
            return
        else:
            self.minimum=kwargs['minimum']
            self.maximum=kwargs['maximum']

    def get_value(self):
        if self.error:
            return -1.0
        else:
            return uniform(self.minimum, self.maximum)

