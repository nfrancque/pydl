from pydl import Component, Bit, Regs, Inputs, Outputs, Boolean, Generics, Unsigned, UnsignedArray

class Template(Component):
    def __init__(self, invert=True, num_counters=5):
        pass
        # super().__init__()
        self.generics = Generics(
            {
                "invert" : Boolean(invert),
                "num_counters" : Unsigned(127, 0)
            }
        )
        self.regs = Regs(
            {
                "reg_val" : Bit(0),
                "counters" : UnsignedArray(num_counters, 127, 0)
            }
        )
        self.inputs = Inputs(
            {
                "val" : Bit()
            }
        )
        self.outputs = Outputs(
            {
                "result" : Bit(),
                "shift_reg" : Unsigned(127)
            }
        )

    def step(self):
        if self.generics.invert:
            self.regs.next.reg_val = not self.inputs.val
        else:
            self.regs.next.reg_val = self.inputs.val
        self.regs.next.counters[0] = Unsigned(self.regs.current.reg_val) + 1
        for i in range(1, self.generics.num_counters):
            self.regs.next.counters[i] = self.regs.current.counters[i-1]
    
    def always(self):
        self.outputs.result = self.regs.current.reg_val
        self.outputs.shift_reg = self.regs.current.counters[self.generics.num_counters-1]
        









