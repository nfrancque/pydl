from pydl import Component, Bit, Regs, Inputs, Outputs, Boolean, Generics

class Template(Component):
    def __init__(self, invert=True):
        pass
        # super().__init__()
        self.generics = Generics(
            {
                "invert" : Boolean(invert)
            }
        )
        self.regs = Regs(
            {
                "reg_val" : Bit(0)
            }
        )
        self.inputs = Inputs(
            {
                "val" : Bit()
            }
        )
        self.outputs = Outputs(
            {
                "result" : Bit()
            }
        )

    def step(self):
        if self.generics.invert:
            self.regs.next.reg_val = not self.inputs.val
        else:
            self.regs.next.reg_val = self.inputs.val
    
    def always(self):
        self.outputs.result = self.regs.current.reg_val
        









