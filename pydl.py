import ast
import inspect
import textwrap

class Component:
    def __init__(self):
        self.generics = None
        self.regs = None
        self.inputs = None
        self.outputs = None

class Bit:
    def __init__(self, initial_value=None):
        self.initial_value = initial_value

class Regs:
    def __init__(self, regs_dict):
        self.regs_dict = regs_dict
        self.current = type('Regs', (object,), regs_dict)()
        self.next = type('Regs', (object,), regs_dict)()

class Inputs:
    def __init__(self, inputs_dict):
        self.inputs_dict = inputs_dict
        self.__dict__.update(inputs_dict)

class Outputs:
    def __init__(self, outputs_dict):
        self.outputs_dict = outputs_dict
        self.__dict__.update(outputs_dict)

class Boolean:
    def __init__(self, value):
        self.value = value

class Generics:
    def __init__(self, generics_dict):
        self.generics_dict = generics_dict
        self.__dict__.update(generics_dict)

def parse_python_to_vhdl(node, generics, inputs, outputs, regs):
    if isinstance(node, ast.If):
        test = parse_python_expr_to_vhdl(node.test, generics, inputs, outputs, regs)
        body = '\n'.join([parse_python_to_vhdl(n, generics, inputs, outputs, regs) for n in node.body])
        if node.orelse:
            orelse = '\n'.join([parse_python_to_vhdl(n, generics, inputs, outputs, regs) for n in node.orelse])
            return f"if {test} then\n{textwrap.indent(body, '    ')}\nelse\n{textwrap.indent(orelse, '    ')}\nend if;"
        return f"if {test} then\n{textwrap.indent(body, '    ')}\nend if;"
    elif isinstance(node, ast.Assign):
        target = parse_python_expr_to_vhdl(node.targets[0], generics, inputs, outputs, regs, next_reg=True)
        value = parse_python_expr_to_vhdl(node.value, generics, inputs, outputs, regs)
        return f"{target} <= {value};"
    return ""

def parse_python_expr_to_vhdl(node, generics, inputs, outputs, regs, next_reg=False):
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return f"not {parse_python_expr_to_vhdl(node.operand, generics, inputs, outputs, regs, next_reg)}"
    elif isinstance(node, ast.Name):
        if node.id in generics:
            return f"G_{node.id.upper()}"
        elif node.id in inputs:
            return f"i_{node.id}"
        elif node.id in outputs:
            return f"o_{node.id}"
        elif node.id in regs:
            return f"{'n.' if next_reg else 'q.'}{node.id}"
    elif isinstance(node, ast.Attribute):
        if node.attr in generics:
            return f"G_{node.attr.upper()}"
        elif node.attr in inputs:
            return f"i_{node.attr}"
        elif node.attr in outputs:
            return f"o_{node.attr}"
        elif node.attr in regs:
            return f"{'n.' if next_reg else 'q.'}{node.attr}"
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, bool):
            return 'true' if node.value else 'false'
        return f"'{node.value}'"
    return ast.dump(node)

def parse_always_to_vhdl(node, generics, inputs, outputs, regs):
    if isinstance(node, ast.Assign):
        target = parse_python_expr_to_vhdl(node.targets[0], generics, inputs, outputs, regs)
        value = parse_python_expr_to_vhdl(node.value, generics, inputs, outputs, regs)
        return f"{target} <= {value};"
    return ""

def generate_vhdl(component):
    entity_name = component.__class__.__name__
    generics_dict = {name: gen for name, gen in component.generics.generics_dict.items()}
    inputs_dict = {name: sig for name, sig in component.inputs.inputs_dict.items()}
    outputs_dict = {name: sig for name, sig in component.outputs.outputs_dict.items()}
    regs_dict = {name: sig for name, sig in component.regs.regs_dict.items()}
    
    generics_vhdl = "\n".join(
        [f"    G_{name.upper()} : boolean := {'true' if gen.value else 'false'}"
         for name, gen in component.generics.generics_dict.items()]
    )
    inputs_vhdl = "\n".join(
        [f"    i_{name} : in std_logic" for name in inputs_dict.keys()]
    )
    outputs_vhdl = "\n".join(
        [f"    o_{name} : out std_logic" for name in outputs_dict.keys()]
    )
    regs_vhdl = "\n".join(
        [f"    {name} : std_logic;" for name in regs_dict.keys()]
    )
    c_regs_vhdl = "\n".join(
        [f"    {name} => '{reg.initial_value}'" for name, reg in component.regs.regs_dict.items()]
    )

    # Generate the comb_proc process from the step method
    step_func_source = textwrap.dedent(inspect.getsource(component.step))
    step_func_ast = ast.parse(step_func_source).body[0]
    comb_proc_body = "\n".join([parse_python_to_vhdl(node, generics_dict, inputs_dict, outputs_dict, regs_dict) for node in step_func_ast.body])

    # Generate the always combinational assignments
    always_func_source = textwrap.dedent(inspect.getsource(component.always))
    always_func_ast = ast.parse(always_func_source).body[0]
    always_body = "\n".join([parse_always_to_vhdl(node, generics_dict, inputs_dict, outputs_dict, regs_dict) for node in always_func_ast.body])

    vhdl_code = f"""
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity {entity_name} is
  generic (
{generics_vhdl}
  );
  port (
    i_clk : in std_logic;
    i_rstn : in std_logic;
{inputs_vhdl};
{outputs_vhdl}
  );
end entity;

architecture rtl of {entity_name} is

  type reg_t is record
{regs_vhdl}
  end record;

  constant C_REG : reg_t := (
{c_regs_vhdl}
  );

  signal q : reg_t;
  signal n : reg_t;

begin

  {always_body}

  comb_proc : process(all) is
  begin
    n <= q;
{textwrap.indent(comb_proc_body, '    ')}
  end process comb_proc;

  sync_proc : process(i_clk) is
  begin
    if rising_edge(i_clk) then
      if i_rstn = '0' then
        q <= C_REG;
      else
        q <= n;
      end if;
    end if;
  end process sync_proc;

end architecture rtl;
"""
    return vhdl_code.strip()
