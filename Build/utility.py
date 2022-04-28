from locale import currency
import numpy as np
import math
import os
import matplotlib.pyplot as plt


def print_SwitchStatement():
	print(
'''Generate List where: 
1. Contents N are all the same
2. Contents N are randomly generated
-------------------------------------''')

def userInput_prompt():

	print_SwitchStatement()
	print("Input two values on the same line seperated by space.")
	arrayType, arraySize = input("List Type / List Size: ").split()
	print("")
	
	arrayType = int(arrayType)
	arraySize = int(arraySize)
	while not (arrayType == 1 or arrayType == 2 and arraySize > 1):
		if arraySize < 2:
			os.system("cls")
			print_SwitchStatement()
			print(f"Input: {arrayType} {arraySize} is invalid. Make sure List Size is greater than 1.")
			print("The two values must be on the same line seperated by space.")

		else:
			os.system("cls")
			print_SwitchStatement()
			print(f"Input: {arrayType} {arraySize} is invalid. Make sure List Type is a valid index.")
			print("The two values must be on the same line seperated by space.")
		
		arrayType, arraySize = input("List Type / List Size: ").split()
		arrayType = int(arrayType)
		arraySize = int(arraySize)
		print("")
	
	return arrayType, arraySize

def back_directory(folder_name):
	#go back one step from parent directory, and create folder of name "folder_name" from input parameter.
	filepath = os.path.dirname(os.path.realpath(__file__))
	backslash_index = filepath.rfind("\\")
	back_path = filepath[0: backslash_index+1]
	new_path = f"{back_path}{folder_name}\\"
	
	return new_path

def export_report(presort, postsort, total_time1, avgCase_List, avgCase_ComputeTime):
	path = back_directory("Exports")
	indexNum = 0

	#check if Exports folder directory exists, create Exports folder if not.
	if not os.path.isdir(path):
		os.makedirs(path)

	#check last indexNum of created files under Exports Folder.
	while os.path.exists(f"{path}listOutput_%s.txt"%indexNum):
		indexNum += 1

	with open(f"{path}listOutput_%s.txt"%indexNum, "w") as f:
		f.write("Pre-Sorted \t Post-Sorted\n")
		for index in range(len(presort)):
			f.write(str(presort[index]) + " \t\t " + str(postsort[index]) + "\n")
		f.write(f"\nComputation Time: {'{0:.2f}'.format(total_time1)}ms\nTime Complexity: O(nlogn)\n")
		f.write("------------------------------------\n\n")

		f.write("Average Case Compute Time:\nT(N) for N = 10, 100, 1000, 10000\n")
		f.write("with five different runs for each value.\n\n")
		for index, comp_time in enumerate(avgCase_ComputeTime):
			f.write((f"{avgCase_List[index]} * 5 Runs Compute Time: {'{0:.2f}'.format(comp_time)}ms\n"))

	print(f"Output to File: listOutput_%s.txt\n"%indexNum)

def plotFunc(avgCase_List, avgCase_ComputeTime):
	np.seterr(divide = 'ignore') 
	np.seterr(invalid = 'ignore') 
	
	#nlogn
	plt.plot(avgCase_List, avgCase_ComputeTime, label = "O(nlogn)")
	
	#n
	avgCase_N = avgCase_ComputeTime/np.log(avgCase_ComputeTime)
	plt.plot(avgCase_List, avgCase_N, label = "O(n)")

	#logn
	avgCase_logn = np.log(avgCase_N)
	avgCase_logn = [0 if math.isnan(x) else x for x in avgCase_logn]
	plt.plot(avgCase_List, avgCase_logn, label = "O(logn)")

	#n^2
	avgCase_N2 = avgCase_N ** 2
	plt.plot(avgCase_List, avgCase_N2, label = "O(n^2)")

	print("-------------------------------------)")
	print("logn:", ["%.2f"%item for item in avgCase_logn])
	print("nlogn:", ["%.2f"%item for item in avgCase_ComputeTime])
	print("N:", ["%.2f"%item for item in avgCase_N])
	print("N2:", ["%.2f"%item for item in avgCase_N2])

	plt.title("Time Complexity Chart")
	plt.xlabel("Average Case")
	plt.ylabel("Time (ms)")

	plt.legend()
	export_plot()
	plt.show()

	return avgCase_N, avgCase_logn, avgCase_N2
	
def export_plot():
	path = back_directory("Graphs")
	indexNum = 0
	
	#check if Exports folder directory exists, create Graphs folder if not.
	if not os.path.isdir(path):
		os.makedirs(path)

	#check last indexNum of created files under Graphs Folder.
	while os.path.exists(f"{path}plot_%s.png"%indexNum):
		indexNum += 1

	plt.savefig(f"{path}plot_%s.png"%indexNum, dpi=300)
	print("")
	print(f"Exported Figure: plot_%s.png"%indexNum)