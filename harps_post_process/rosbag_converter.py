#!/usr/bin/env python
"""
Converts ROS bags in a directory to .csv files for each topic.
Use 1: 'python3 rosbag_converter.py' to convert all ROSbags in current directory
or 2: 'python3 rosbag_converter.py <bagName>' to convert a single ROSbag in the current directory.
"""

__author__ = "Trevor Slack"
__version__ = "1.1"
__maintainer__ = "Trevor Slack"
__email__ = "trevor.slack@colorado.edu"
__status__ = "Production"


import rosbag, sys, csv, time, string, os


""" reads each ROSbag in baglist into .csv files for each topic """
def readBags(baglist):
	start_time = time.time()
	# read all bags
	count = 0
	while baglist:
		# get new bag
		bag = rosbag.Bag(baglist.pop(-1))
		bagData = bag.read_messages()
		bagName = bag.filename
		print("Reading ROSbag: {}".format(bagName))

		# directory to save bags in
		directory = bagName.rstrip(".bag")
		try:
			os.makedirs(directory)
		except:
			pass

		# topics in bag
		topics = []
		for topic, msg, t in bagData:
			if topic not in topics:
				# ignore image data
				if topic == '/Drone1/image_raw':
					continue
				topics.append(topic)

		# create .csv file for topics
		for topicName in topics:
			filename = directory + '/' + topicName.replace('/', '_slash_') + '.csv'
			# open in csv format
			with open(filename,"w+") as csvfile:
				filewriter = csv.writer(csvfile,delimiter=',')
				firstIteration = True
				# every occurance of topicName
				for subtopic, msg, t in bag.read_messages(topicName):
					# data is in format 'DataName: value\n...'
					msgString = str(msg)
					msgList = msgString.split('\n')
					#print(msgList)
					listofData = []
					for namePair in msgList:
						# split into 'DataName', 'value'
						splitPair = namePair.split(':')
						if len(splitPair) == 1:
							splitPair = ['',splitPair[0]]
						#print(namePair)
						#print(splitPair)
						# remove extra space
						for i in range(len(splitPair)):
							splitPair[i] = splitPair[i].strip()
							splitPair[i] = splitPair[i].replace("- ","")
							#print(splitPair[i])
						listofData.append(splitPair)
					#print(listofData)
					# write message to csv
					# header
					if firstIteration:
						headers = ["rosbagTimestamp"]
						for pair in listofData:
							headers.append(pair[0])
						#print(headers)
						filewriter.writerow(headers)
						firstIteration = False
					# write values
					values = [str(t)] # timestamp
					for pair in listofData:
						if len(pair) > 1:
							values.append(pair[1])
					#print(values)
					filewriter.writerow(values)
		bag.close()
		count+=1
	total_time = round(time.time() - start_time,1)
	print("Finished reading all {} ROSbag files in {} seconds.".format(count,total_time))



if __name__ == "__main__":
	# verify arguments
	baglist = []
	num_argvs = len(sys.argv)
	if num_argvs > 2:
		print("Invalid number of arguments: {}".format(num_argvs))
		print("Use 2: 'rosbag_converter.py' 'ROSbag Name', for a single ROSbag\n Or 1: 'rosbag_converter.py', for all ROSbags in current directory.")
		sys.exit(1)
	elif num_argvs == 2:
		baglist.append(sys.argv[1])
	else:
		count = 0
		for bag in os.listdir("."):
			if bag[-4:] == ".bag":
				baglist.append(bag)
				count+=1
		print("Reading {} ROSbags in {}".format(count,os.getcwd()))
	# read the ROSbag(s)
	readBags(baglist)