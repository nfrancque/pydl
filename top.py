from template import Template
from pydl import generate_vhdl

template = Template(invert=True)
vhdl_output = generate_vhdl(template)
print(vhdl_output)
