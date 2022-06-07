from typing import Union



class HelperMixIn2:
    # attribute1: float
    # attribute2: float

    # import BigClass
    # import HelperMixIn1
    # from Testing_Interface.MixIns.BigClass import BigClass
    # from Testing_Interface.MixIns.HelperMixIn1 import HelperMixIn1

    # def complicated_expression(self: Union[BigClass.BigClass, HelperMixIn1.HelperMixIn1, 'HelperMixIn2']):
    #     return self.attribute1 + self.add_attributes()
    def complicated_expression(self):
        return self._attribute1 + self.add_attributes()

