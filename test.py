import function
import parser

name = "최소실버가목표"
function.userInfo(parser.parseOPGG(name))
temp = open("temp.txt","r")
data = temp.read()

print(str(data))