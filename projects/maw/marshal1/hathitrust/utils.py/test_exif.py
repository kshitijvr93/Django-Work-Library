# 20180620
# first, do $ pip install eifread
# see the pip docs
# and project release pages
import exifread
f = open('c:\\rvp\\tmpf.jp2', 'rb')
tags = exifread.process_file(f)

print ("Got tags='{}'".format(tags))
print ("Done")
