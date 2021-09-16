# read the file
filename = "secret_data access time3.txt" # input the file name
try:
	file = open(filename, "r") # if the file exist, open it 
except:
	print("File does not exist") # if the file doesn't exist, close the program
	exit()
	
max_time = 999999999
for line in file:
	time = int(line[line.find(":")+1:].strip())
	max_time = min(max_time, time)

print(max_time)