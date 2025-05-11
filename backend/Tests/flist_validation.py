import sys
import re
import struct
def flist_validation(filepath):
    line_number = 0
    xop_total = 0
    r_total = 0
    RESULT = 0
    with open(filepath, 'r') as file:
        for line in file:
            #print(len(line))
            line_number += 1
            if re.match('^r', line):
                r_total = len(line.split(' '))
                if (r_total==4 and line.split(' ')[0]=='r'  and line.split(' ')[1]=='<<' and line.split(' ')[2].isalnum() and line.split(' ')[3].strip().isnumeric()  ):
                    tfile = line.split(' ')[2]
                    #RESULT=1
                    continue
                else:
                    return ('ERROR:Invalid input starting with r',line_number)
                    #print(line)
            elif (re.match('^0', line) and len(line.split(' ')) != 1):
                    #print(line)
                    continue
            elif (re.match('^1', line) and len(line.split(' ')) != 1):
                #print(line)
                    continue
            elif (re.match('^2', line) and len(line.split(' ')) != 1):
                    #print(line)
                    continue
            elif (re.match('^3', line) and len(line.split(' ')) != 1):
                    #print(line)
                    continue
            elif (line.isspace()):
                    return('ERROR:Empty line at line number',line_number)
            elif (len(line) == 1 and line != tfile):
                    return('ERROR:Invalid closure of file at line number',line_number)
            elif(len(line.split(' ')) < 1):
                    return ('Error :Invalid closure line number', line_number)
                    #print(line)
            elif re.match('^xop', line):
                xop_total = len(line.split(' '))
                #print (xop_total)
                if (xop_total==4 and line.split(' ')[0]=='xop'  and line.split(' ')[1].isascii() and line.split(' ')[2].isalnum()and line.split(' ')[3].strip().isdigit()):
                    # return ('VALID')
                    RESULT = 1
                    #print(RESULT)
                else:
                    return('Error :Invalid opcode call at line number',line_number)

            if (RESULT == 1):
                    return 'VALID'
