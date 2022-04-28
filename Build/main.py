import time
import numpy as np
import utility

def mergeSort(arr):
	#sourced from https://www.geeksforgeeks.org/merge-sort/
	if len(arr) > 1:
		mid = len(arr)//2
		L = arr[:mid]
		R = arr[mid:]

		mergeSort(L)
		mergeSort(R)
		i = j = k = 0
  
		while i < len(L) and j < len(R):
			if L[i] < R[j]:
				arr[k] = L[i]
				i += 1
			else:
				arr[k] = R[j]
				j += 1
			k += 1
  
		while i < len(L):
			arr[k] = L[i]
			i += 1
			k += 1
  
		while j < len(R):
			arr[k] = R[j]
			j += 1
			k += 1
	
	return arr

def generateList(arrayType, arraySize):
	MAX_RANGE = 10000
	if(arrayType == 1):
		input_array = np.ones((1, int(arraySize)))
	elif(arrayType == 2):
		input_array = np.random.randint(MAX_RANGE, size=int(arraySize))

	input_array = input_array.tolist()
	return input_array

def avgCase_compute(list, repeats):
	avgCase_ComputeTime = []
	total_time = 0

	print('''Average Case Compute Time:
T(N) for N = 10, 100, 1000, 10000
with five different runs for each value.
-------------------------------------''')

	for i in list:
		for run_count in range(repeats):
			tempList = generateList(2, i)
			start = time.time()
			tempList = mergeSort(tempList)
			end = time.time()

			temp_time = end - start
			total_time += temp_time

		avgCase_ComputeTime.append(total_time*1000)
		total_time = 0
	return avgCase_ComputeTime

if __name__ == '__main__':

	arrayType, arraySize = utility.userInput_prompt()
	
	presort = generateList(arrayType, arraySize)
	print("Pre-Sorted: ")
	print(presort)

	start = time.time()
	postsort = mergeSort(presort[:])
	end = time.time()
	total_time1 = end - start
	
	print("Post-Sorted: ")
	print(postsort)
	
	print(" Time Complexity: O(nlogn)")	
	print(f"Computation Time: {'{0:.2f}'.format(total_time1*1000)}ms\n")

	avgCase_List = [10, 100, 1000, 10000]
	avgCase_ComputeTime = avgCase_compute(avgCase_List, 5)
	for index, comp_time in enumerate(avgCase_ComputeTime):
		print(f"{avgCase_List[index]} * 5 Runs Compute Time: {'{0:.2f}'.format(comp_time)}ms")

	avgCase_N, avgCase_logn, avgCase_N2 = utility.plotFunc(avgCase_List, avgCase_ComputeTime)
	utility.export_report(presort, postsort, total_time1, avgCase_List, avgCase_ComputeTime)
