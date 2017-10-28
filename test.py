
file_name= '/home/robert/testfile.txt'
f = open(file_name, 'w')
print("I am file {}".format(file_name),file=f)
print("Closing")
f.close()
print("Closing")
f.close()
print ("done")
