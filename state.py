import sys
import getopt
import re
import math

def usage():
	print """Usage: python state.py [args]
    Options and arguments:
    -h	:	this message;
    -f file	:	specifies SM file;
    -o name	:	specifies output VHDL filename(name.vhd).
    """
	exit()

options, remainder = getopt.gnu_getopt(sys.argv, 'hf:o:', ['help', 'file=', 'output='])

file = ''
output = ''

for opt, arg in options:
	if opt in ('-h', '--help'):
		usage()

	if opt in ('-f', '--file'):
		file = arg

	if opt in ('-o', '--output'):
		output = arg

if file == '':
	print 'HDL file not defined'
	exit()

if output == '':
	print 'Output file not defined'
	exit()

buffer = ''
name = output
message = 'Reach simulation end.'

states = []
labels = []
instrs = []
inputs = []
outputs = []
states_dict = {}
state_count = 0

with open(file) as f:
    for line in f:
        line = line.replace('\n', '').replace('\t', '').replace('\r', '').replace(' ', '')
        state = line.split(':')
        states.append([state[0], state[1]])

def find_instr(ex):
	regex = r'(\d+)\-\>([a-zA-Z0-9]+)'
	match = re.findall(regex, ex)
	if match:
		return match
	return None

def find_outputs(ex):
	regex = r'out\=(\d*)'
	match = re.findall(regex, ex)
	if match:
		return match
	return None

def indent(n):
	return n*'\t'

def state_conditions(instr, ind):
	buffer = ''
	if instr != None:
		n = len(instr)
		buffer += indent(ind) + 'IF input = \"{}\" THEN\n'.format(instr[0][0])
		buffer += indent(ind + 1) + 'state <= {};\n'.format(instr[0][1])
		for i in instr[1:]:
			if n >= 2:
				buffer += indent(ind) + 'ELSIF input = \"{}\" THEN\n'.format(i[0])
			else:
				buffer += indent(ind) + 'IF input = \"{}\" THEN\n'.format(i[0])
			buffer += indent(ind + 1) + 'state <= {};\n'.format(i[1])
		buffer += indent(ind) + 'ELSE\n'
		buffer += indent(ind + 1) + 'state <= {};\n'.format(states[0][0])
		buffer += indent(ind) + 'END IF;\n'
	else:
		buffer += indent(ind) + 'state <= {};\n'.format(states[0][0])
	return buffer

def input_conditions():
	buffer = ''
	ind = 4
	for s in states:
		instr = states_dict[s[0]]['instr']
		buffer += indent(ind) + 'WHEN {}=>\n'.format(s[0])
		buffer += state_conditions(instr, ind+1)
	return buffer[:-1]

def output_conditions():
	buffer = ''
	ind = 4
	for s in states:
		if states_dict[s[0]]['out'] != None:
			buffer += indent(ind) + 'WHEN {}=>\n'.format(s[0])
			buffer += indent(ind + 1) + 'output <= \"{}\";\n'.format(states_dict[s[0]]['out'][0])
	return buffer[:-1]

def port(name, direction, size = 0):
	port_type = 'STD_LOGIC'
	direction = direction.upper()
	if size != 0:
		port_type += '_VECTOR({} downto 0)'.format(size)
	return '\t\t{}\t:\t{}\t{};\n'.format(name, direction, port_type)

def ports():
	input_size = len('{0:b}'.format(max(inputs))) - 1
	output_size = len('{0:b}'.format(max(outputs))) - 1
	ports = ''
	ports += port('clk', 'in')
	ports += port('reset', 'in')
	ports += port('input', 'in', input_size)
	ports += port('output', 'out', output_size)
	return ports[:-2]

def save(name, params):
    with open('template') as f:
        text = f.read()
    for var in params:
        text = text.replace('<<{}>>'.format(var[0]), var[1])

    f = open(name + '.vhd', 'w')
    f.write(text)
    print 'File {}.vhd created.'.format(name)
    f.close()

for state in states:
	labels.append(state[0])
	instrs.append(state[1])
	state_dict = {}

	instr = find_instr(state[1])
	if instr != None:
		for i in instr:
		    inputs.append(int(i[0]))

	outps = find_outputs(state[1])
	if outps != None:
		for o in outps:
			outputs.append(int(o))

	state_dict['instr'] = instr
	state_dict['out'] = outps
	states_dict[state[0]] = state_dict

arr = [
	['entity', name],
	['ports', ports()],
	['state_list', ', '.join(labels)],
	['first_state', labels[0]],
	['input_conditions', input_conditions()],
	['output_conditions', output_conditions()],
]

save(name, arr)
# print states_dict
