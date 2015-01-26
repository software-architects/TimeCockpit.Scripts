# -*- coding: utf-8 -*-

# =================================================================================================================
#	SIGNAL DATA EXPORT SCRIPT (see SampleExport.py for an example of how to use)
# -----------------------------------------------------------------------------------------------------------------
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
#	This script exports the activity log collected by time cockpit's signal tracker. The result is another
#	script that can be used to recreate the activity log in a different time cockpit account.
#	Note that this script has to have access to the decrypted activity log. Therefore, you can only export
#	signals of the current user. Because of privacy restrictions, it is NOT POSSIBLE to export the
#	activity log of a different user.
#
#	CAUTION: THE RESULTS MIGHT CONTAIN SENSITIVE DATA AS IT INCLUDES THE ENTIRE ACTIVITY LOG FOR
#		THE SELECTED TIME PERIOD. THEREFORE, YOU HAVE TO PROPERLY PROTECT THE RESULTS.
# =================================================================================================================

# Import some .NET classes
from System.Collections.Generic import Dictionary, List
from System import String
from System.Text import StringBuilder
from System.IO import StreamWriter
clr.AddReference("System.Core")

def exportSignalsToFile(dc,	dayToExport, deviceNameToExport, targetFilePath, subroutineName, \
	exportFileSystemSignals = False, exportWifiSignals = False):
	"""
	Exports signal data of activity log to a file.

	Keyword arguments:
	dc -- DataContext that should be used to read activity log (TimeCockpit.Data.DataContext)
	dayToExport -- Day that should be exported (DateTime; time-part has to be 0)
	deviceNameToExport -- Name of the device that should be exported
	targetFilePath -- Full path to the target file (UTF-8, overwrites file if it exists)
	subroutineName -- Name of the generated routine (should be unique for each export)
	exportFileSystemSignals -- Indicates whether file system signals should be exported (bool); default is False
	exportWifiSignals -- Indicates whether WIFI signals should be exported (bool); default is False
	"""
	targetStream = StreamWriter(targetFilePath)
	try:
		exportSignalsToStream(dc, dayToExport, deviceNameToExport, targetStream, subroutineName, \
			exportFileSystemSignals, exportWifiSignals)
	finally:
		targetStream.Close()

def exportSignalsToStream(dc, dayToExport, deviceNameToExport, targetStream, subroutineName, \
	exportFileSystemSignals, exportWifiSignals):
	"""
	Exports signal data of activity log to a stream.

	Keyword arguments:
	dc -- DataContext that should be used to read activity log (TimeCockpit.Data.DataContext)
	dayToExport -- Day that should be exported (DateTime; time-part has to be 0)
	deviceNameToExport -- Name of the device that should be exported
	targetStream -- Target Stream (System.IO.StreamWriter)
	subroutineName -- Name of the generated routine (should be unique for each export)
	exportFileSystemSignals -- Indicates whether file system signals should be exported (bool); default is False
	exportWifiSignals -- Indicates whether WIFI signals should be exported (bool); default is False
	"""

	# Internal helper function for extracting type name
	def extractTypeName(x):
		helper = str(x)
		helper = helper.Substring(0, helper.IndexOf(' '))
		helper = helper.Substring(helper.LastIndexOf('.') + 1)
		return helper

	# Specify all signal types that should be exported
	signalTypes = [ "APP_CleansedChangeSetSignal", "APP_CleansedComputerActiveSignal", "APP_CleansedEmailSentSignal",
		"APP_CleansedIpConnectSignal", "APP_CleansedPhoneCallSignal", "APP_CleansedShortMessageSignal", 
		"APP_CleansedUserActiveSignal", "APP_CleansedUserNoteSignal", "APP_CleansedWindowActiveSignal", 
		"APP_CleansedWorkItemChangeSignal" ]
	if exportFileSystemSignals:
		# Only export file system signals if explicitly asked for
		signalTypes.append("APP_CleansedFileSystemSignal")
	if exportWifiSignals:
		# Only export WIFI signals if explicitly asked for
		signalTypes.append("APP_CleansedWifiAvailableSignal")

	try:
		chunks = dc.SelectWithParams({
			"Query": "From C In SYS_Chunk.Include('SYS_Entity').Include('SYS_Device') " \
				"Where ((:Year(C.BeginTime) = @FilterYear And :Month(C.BeginTime) = @FilterMonth And :Day(C.BeginTime) = @FilterDay) " \
				"	Or (:Year(C.EndTime) = @FilterYear And :Month(C.EndTime) = @FilterMonth And :Day(C.EndTime) = @FilterDay)) " \
				"	And C.Device.DeviceName = @DeviceName Select C",
			"@FilterYear": dayToExport.Year, "@FilterMonth": dayToExport.Month, "@FilterDay": dayToExport.Day,
			"@DeviceName": deviceNameToExport })
		if (len(chunks) == 0):
			raise Exception("No chunks found. Please review export filter criteria.")
		
		# Write documentation header
		targetStream.WriteLine("# -*- coding: utf-8 -*-")
		targetStream.WriteLine("# This is an auto-generated script")
		targetStream.WriteLine("#\tGeneration date: {0}", DateTime.Today)
		targetStream.WriteLine("#\tSource device name: {0}", deviceNameToExport)
		targetStream.WriteLine("#\tSource day: {0}", dayToExport)
		targetStream.WriteLine()

		# Write necessary imports		
		targetStream.WriteLine("from System.Collections.Generic import List")
		targetStream.WriteLine()
		
		# Generate method that regenerates activity log
		targetStream.WriteLine("def {0}(dc, targetDay):", subroutineName)
		targetStream.WriteLine("\tentities = dc.Select(\"From E In SYS_Entity Select E\")")
		targetStream.WriteLine("\tdevice = dc.SelectSingle(\"From D In SYS_Device Select D\")")
		targetStream.WriteLine("\tif device is None:")
		targetStream.WriteLine("\t\traise Exception(\"No device found\")")
		targetStream.WriteLine("\ttimeCorrection = targetDay - DateTime({0}, {1}, {2})", dayToExport.Year, dayToExport.Month, dayToExport.Day)
		
		targetStream.WriteLine("\tdc.DbClient.BeginTransaction()")
		targetStream.WriteLine("\ttry:")
		for chunk in chunks:
			if (chunk.Entity.EntityName in signalTypes):
				targetStream.WriteLine("\t\tchunk = dc.CreateChunk({{ \"BeginTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.BeginTime.Year, chunk.BeginTime.Month, chunk.BeginTime.Day, chunk.BeginTime.Hour, chunk.BeginTime.Minute, chunk.BeginTime.Second)
				targetStream.WriteLine("\t\t\t\"EndTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.EndTime.Year, chunk.EndTime.Month, chunk.EndTime.Day, chunk.EndTime.Hour, chunk.EndTime.Minute, chunk.EndTime.Second)
				targetStream.WriteLine("\t\t\t\"LogicalBeginTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.LogicalBeginTime.Year, chunk.LogicalBeginTime.Month, chunk.LogicalBeginTime.Day, chunk.LogicalBeginTime.Hour, chunk.LogicalBeginTime.Minute, chunk.LogicalBeginTime.Second)
				targetStream.WriteLine("\t\t\t\"LogicalEndTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.LogicalEndTime.Year, chunk.LogicalEndTime.Month, chunk.LogicalEndTime.Day, chunk.LogicalEndTime.Hour, chunk.LogicalEndTime.Minute, chunk.LogicalEndTime.Second)
				targetStream.WriteLine("\t\t\t\"Entity\": [e for e in entities if e.EntityName == \"{0}\"][0],", chunk.Entity.EntityName)
				targetStream.WriteLine("\t\t\t\"Device\": device })")
				
				targetStream.WriteLine("\t\tchunkContentList = List[EntityObject]()")
				for signal in chunk.Content:
					signalContent = StringBuilder()
					for prop in signal.Entity.Properties:
						typeName = extractTypeName(prop)
						if (typeName <> "CalculatedProperty"):
							if (signalContent.Length > 0):
								signalContent.Append(", ")
							signalContent.AppendFormat("\"{0}\": ", prop.Name)
							if (typeName == "TextProperty"):
								signalContent.Append('"')
								t = eval("signal.{0}".format(prop.Name)).Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\t").Replace("\r", "\\r")
								signalContent.Append(t)
								signalContent.Append('"')
							elif (typeName == "DateTimeProperty"):
								signalContent.Append('DateTime(')
								d = eval("signal.{0}".format(prop.Name))
								signalContent.AppendFormat("{0}, {1}, {2}, {3}, {4}, {5}", d.Year, d.Month, d.Day, d.Hour, d.Minute, d.Second)
								signalContent.Append(')')
								if (prop.Name == "APP_BeginTime" or prop.Name == "APP_EndTime" or prop.Name == "APP_EventTime"):
									signalContent.Append(" + timeCorrection")
							elif (typeName == "BooleanProperty"):
								b = eval("signal.{0}".format(prop.Name))
								signalContent.Append("True" if b else "False")
							elif (typeName == "GuidProperty"):
								signalContent.Append('Guid("')
								signalContent.Append(eval("signal.{0}".format(prop.Name)))
								signalContent.Append('")')
							elif (typeName == "NumericProperty"):
								n = eval("signal.{0}".format(prop.Name))
								signalContent.Append(n)
							else:
								raise Exception("MISSING TYPE {0}".format(typeName))
					targetStream.WriteLine("\t\tchunkContentList.Add(dc.Create{0}({{ {1} }}))", chunk.Entity.EntityName, signalContent.ToString())
				targetStream.WriteLine("\t\tchunk.Content = chunkContentList")
				targetStream.WriteLine("\t\tdc.SaveObject(chunk)")
		targetStream.WriteLine("\texcept:")
		targetStream.WriteLine("\t\tif (dc.DbClient.TransactionCount > 0):")
		targetStream.WriteLine("\t\t\tdc.DbClient.RollbackTransaction()")
		targetStream.WriteLine("\t\traise")
		targetStream.WriteLine("\tfinally:")
		targetStream.WriteLine("\t\tif (dc.DbClient.TransactionCount > 0):")
		targetStream.WriteLine("\t\t\tdc.DbClient.CommitTransaction()")
		
	finally:
		targetStream.Close()
