def twoscomp(num):
	if (num & (1 << 31)) != 0:
		num = num - (1 <<32)
	return num

if __name__ == "__main__":
	input = open("sample.txt","r")
	sim = open("sample_simulation2.txt","w+")
	dis = open("sample_disassembly2.txt","w+")
	global pc
	pc=260
	linelist = input.readlines()
	registers = [0]*32
	data = [0]*16
	stop = False
	i, j, k, l = 0, 0, 0, 0
	while (linelist[j][:6] != "000110"):
		j += 1
	instructions = [None]*j
	for k in range(16):
		data[k] = twoscomp(int(linelist[j+1],2))
		j += 1
	while (stop is False):
		l += 1
		if (linelist[i][:3] == "000"):
			if (linelist[i][3:6] == "000"): #	J INSTRUCTION
				addr = int((linelist[i][7:32] + "00"),2)
				instructions[i] = "\t%d J #%d\n" % (pc,addr)
				pc = addr
			elif (linelist[i][3:6] == "001"): #	BEQ INSTRUCTION
				addr = int((linelist[i][16:32] + "00"),2)
				rs = int(linelist[i][6:11],2)
				rd = int(linelist[i][11:16],2)
				instructions[i] = "\t%d BEQ R%d R%d, #%d\n" % (pc,rs,rd,addr)
				if (registers[rs] == registers[rd]):
					pc += addr+4
				else:
					pc += 4
			elif (linelist[i][3:6] == "010"): #	BNE INSTRUCTION
				addr = int((linelist[i][16:32] + "00"),2)
				rs = int(linelist[i][6:11],2)
				rd = int(linelist[i][11:16],2)
				if (registers[rs] != registers[rd]):
					pc += addr+4
				else:
					pc += 4
				instructions[i] = "\t%d BNE R%d R%d, #%d\n" % (pc,rs,rd,addr)
			elif (linelist[i][3:6] == "011"): #	BGTZ INSTRUCTION
				addr = int((linelist[i][16:32] + "00"),2)
				rs = int(linelist[i][6:11],2)
				if (registers[rs] > 0):
					pc += addr+4
				else:
					pc += 4
				instructions[i] = "\t%d BGTZ R%d, #%d\n" % (pc,rs,addr)
			elif (linelist[i][3:6] == "100"): #	SW INSTRUCTION
				base = int(linelist[i][6:11],2)
				rt = int(linelist[i][11:16],2)
				offset = int(linelist[i][16:32],2)
				data[(base+offset-316)//4]=registers[rt]
				instructions[i] = "\t%d SW R%d, (%d)%d\n" % (pc,rt,offset,base)
				pc += 4
			elif (linelist[i][3:6] == "101"): #	LW INSTRUCTION
				base = int(linelist[i][6:11],2)
				rt = int(linelist[i][11:16],2)
				offset = int(linelist[i][16:32],2)
				registers[rt]=data[(base+offset-316)//4]
				instructions[i] = "\t%d LW R%d, (%d)%d\n" % (pc,rt,offset,base)
				pc += 4
			elif (linelist[i][3:6] == "110"):
				stop = True
				break
			else:
				print("Unknown operation")
		elif (linelist[i][:3] == "001"): #	CATEGORY-2 INSTRUCTIONS
			opcode = linelist[i][3:6]
			dest = int(linelist[i][6:11],2)
			src1 = int(linelist[i][11:16],2)
			src2 = int(linelist[i][16:21],2)
			if (opcode == "100"): #	SRL INSTRUCTION
				dest, src1, src2 = sa, rd ,rt
				registers[rd] = registers[rt] >> sa
				instructions[i] = "\t%d SRL R%d, R%s, R%s\n"%(pc,sa,rd,rt)
			elif (opcode == "101"):
				dest, src1, src2 = sa, rd ,rt
				registers[rd] = registers[rt] >> sa
				instructions[i] = "\t%d SRA R%d, R%s, R%s\n"%(pc,sa,rd,rt)
			elif (opcode == "000"):
				registers[dest] = registers[src1] + registers[src2]
				instructions[i] = "\t%d ADD R%d, R%d, R%d\n"% (pc,dest,src1,src2)
			elif (opcode == "001"):
				registers[dest] = registers[src1] - registers[src2]
				instructions[i] = "\t%d SUB R%d, R%d, R%d\n"% (pc,dest,src1,src2)
			elif (opcode == "010"):
				registers[dest] = registers[src1] & registers[src2]
				instructions[i] = "\t%d AND R%d, R%d, R%d\n"% (pc,dest,src1,src2)
			elif (opcode == "011"):
				registers[dest] = registers[src1] | registers[src2]
				instructions[i] = "\t%d OR R%d, R%d, R%d\n"% (pc,dest,src1,src2)
			elif (opcode == "110"):
				registers[dest] = registers[src1] * registers[src2]
				instructions[i] = "\t%d MUL R%d, R%d, R%d\n"% (pc,dest,src1,src2)
			pc += 4
		elif (linelist[i][:3] == "010"):
			dest = int(linelist[i][6:11],2)
			src = int(linelist[i][11:16],2)
			imm = twoscomp(int(linelist[i][16:32],2))
			if (linelist[i][3:6] == "000"):
				registers[dest] = registers[src] + imm
				instructions[i] = "\t%d ADDI R%d, R%d, #%d\n"%(pc,dest,src,imm)
			elif (linelist[i][3:6] == "001"):
				registers[dest] = registers[src] & imm
				instructions[i] = "\t%d ANDI R%d, R%d, #%d\n"%(pc,dest,src,imm)
			elif (linelist[i][3:6] == "010"):
				registers[dest] = registers[src] | imm
				instructions[i] = "\t%d ORI R%d, R%d, #%d\n"%(pc,dest,src,imm)
			else:
				print("Unknown instruction")
			pc += 4
		else:
			print("Unkown intruction")
		sim.write("--------------------\nCycle %d:%s\nRegisters\nR00:\t"%(l,instructions[i]))
		for a in range(4):
			sim.write("\nR0%d:\t"%a)
			for b in range(8):
				sim.write("%d\t"%registers[a*b])
		sim.write("\n\nData")
		for a in range(2):
			sim.write("\n%d:\t"%(316+32*a))
			for b in range(8):
				sim.write("%d\t"%data[a*b])
		sim.write("\n\n")
		i = (pc-260)//4
	for i in range(0,len(instructions)):
		dis.write(linelist[i]+instructions[i])
	dis.close()
	sim.close()
	input.close()

