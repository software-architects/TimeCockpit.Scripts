# -*- coding: utf-8 -*-

# =================================================================================================================
#	SIGNAL DATA EXPORT SCRIPT
# -----------------------------------------------------------------------------------------------------------------
#	The MIT License (MIT)
#	Copyright (c) 2015 software architects gmbh
#	
#	Permission is hereby granted, free of charge, to any person obtaining a copy
#	of this software and associated documentation files (the "Software"), to deal
#	in the Software without restriction, including without limitation the rights
#	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#	copies of the Software, and to permit persons to whom the Software is
#	furnished to do so, subject to the following conditions:
#	
#	The above copyright notice and this permission notice shall be included in
#	all copies or substantial portions of the Software.
#	
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#	THE SOFTWARE.
# -----------------------------------------------------------------------------------------------------------------
#	This script demonstrates how to use the export methods for activity logs (see ExportSignalsToScript.py
#	for details).
#
#	CAUTION: THE RESULTING FILES MIGHT CONTAIN SENSITIVE DATA AS IT INCLUDES THE ENTIRE ACTIVITY LOG FOR
#		THE SELECTED TIME PERIOD. THEREFORE, YOU HAVE TO PROPERLY PROTECT THE RESULTING FILE.
# =================================================================================================================
from System.IO import StringWriter

dc = Context

# Path where scripts are stored. You have to change that value according to your directory structure
basePath = r"C:\Code\Github_TimeCockpit.Scripts\ExportImportSignals"

# Execute ExportSignalsToScript.py so that we get the necessary export functions
# exportSignalsToFile and exportSignalsToStream
execfile(basePath + r"\ExportSignalsToScript.py")

# Export signals of a specific date to a file
exportSignalsToFile(Context, DateTime(2015, 1, 26)	# Date to export
	, "SIERRA3"										# Name of the device to export \
	, basePath + "\\TypicalOfficeDayLog.g.py"		# Name of target file \
	, "GenerateTypicalOfficeDayLog"					# Name of the generated method \
	, False, False)									# No need to generate file and WIFI signals

# Export multiple days (January 20th to 23th) in a loop
for day in range(20, 23 + 1):
	exportSignalsToFile(Context, DateTime(2015, 1, day), "SIERRA3"
		, basePath + "\\Signals{0}.g.py".format(day)	# Name of target file \
		, "GenerateSignals{0}".format(day)				# Name of the generated method \
		, False, False)									# No need to generate file and WIFI signals

# Export signals to a string
writer = StringWriter()
exportSignalsToStream(Context, DateTime(2015, 1, 25)	# Date to export
	, "SIERRA3"											# Name of the device to export \
	, writer											# Target stream (backed by StringBuilder) \
	, "GenerateTypicalDevelopmentDayLog"				# Name of the generated method \
	, False, False)										# No need to generate file and WIFI signals
# Print source of generated method
print writer.ToString().Substring(50) + " ..."

print "Done!"
