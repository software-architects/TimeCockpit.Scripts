# -*- coding: utf-8 -*-
# =================================================================================================================
#	SIGNAL DATA EXPORTER
#	This script can be used to generate a Python script that re-creates the signals of the specified day.
# =================================================================================================================

from System.Collections.Generic import Dictionary, List
from System import String
from System.Text import StringBuilder
from System.IO import StreamWriter
from System import Random
clr.AddReference("System.Core")

def extractTypeName(x):
	helper = str(x)
	helper = helper.Substring(0, helper.IndexOf(' '))
	helper = helper.Substring(helper.LastIndexOf('.') + 1)
	return helper
	
def exportSignals(dc, dayToExport, deviceNameToExport, targetFilePath, scenarioName, subroutineName, exportFileSystemSignals, exportWifiSignals):
	# Specify all signal types that should be exported
	signalTypes = [ "APP_CleansedChangeSetSignal", "APP_CleansedComputerActiveSignal", "APP_CleansedEmailSentSignal",
		"APP_CleansedIpConnectSignal", "APP_CleansedPhoneCallSignal",
		"APP_CleansedShortMessageSignal", "APP_CleansedUserActiveSignal", "APP_CleansedUserNoteSignal",
		"APP_CleansedWindowActiveSignal", "APP_CleansedWorkItemChangeSignal" ]
	if exportFileSystemSignals:
		# Only export file system signals if explicitly asked for
		signalTypes.append("APP_CleansedFileSystemSignal")
	if exportWifiSignals:
		# Only export WIFI signals if explicitly asked for
		signalTypes.append("APP_CleansedWifiAvailableSignal")

	writer = StreamWriter(targetFilePath)
	rand = Random()
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
		
		writer.WriteLine("# -*- coding: utf-8 -*-")
		writer.WriteLine("# This is an auto-generated script")
		writer.WriteLine("#\tScenario name: {0}", scenarioName)
		writer.WriteLine("#\tGeneration date: {0}", DateTime.Today)
		writer.WriteLine("#\tSource device name: {0}", deviceNameToExport)
		writer.WriteLine("#\tSource day: {0}", dayToExport)
		writer.WriteLine()
		
		writer.WriteLine("from System.Collections.Generic import List")
		writer.WriteLine("persist = False\t\t# Change to True to write changes to DB")
		writer.WriteLine()
		writer.WriteLine("def {0}(dc, targetDay):", subroutineName)
			
		writer.WriteLine("\tentities = dc.Select(\"From E In SYS_Entity Select E\")")
		writer.WriteLine("\tdevice = dc.SelectSingle(\"From D In SYS_Device Select D\")")
		writer.WriteLine("\tif device is None:")
		writer.WriteLine("\t\traise Exception(\"No device found\")")
		writer.WriteLine("\ttimeCorrection = targetDay - DateTime({0}, {1}, {2})", dayToExport.Year, dayToExport.Month, dayToExport.Day)
		
		writer.WriteLine("\tdc.DbClient.BeginTransaction()")
		writer.WriteLine("\ttry:")
		for chunk in chunks:
			if (chunk.Entity.EntityName in signalTypes):
				writer.WriteLine("\t\tchunk = dc.CreateChunk({{ \"BeginTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.BeginTime.Year, chunk.BeginTime.Month, chunk.BeginTime.Day, chunk.BeginTime.Hour, chunk.BeginTime.Minute, chunk.BeginTime.Second)
				writer.WriteLine("\t\t\t\"EndTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.EndTime.Year, chunk.EndTime.Month, chunk.EndTime.Day, chunk.EndTime.Hour, chunk.EndTime.Minute, chunk.EndTime.Second)
				writer.WriteLine("\t\t\t\"LogicalBeginTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.LogicalBeginTime.Year, chunk.LogicalBeginTime.Month, chunk.LogicalBeginTime.Day, chunk.LogicalBeginTime.Hour, chunk.LogicalBeginTime.Minute, chunk.LogicalBeginTime.Second)
				writer.WriteLine("\t\t\t\"LogicalEndTime\": DateTime({0}, {1}, {2}, {3}, {4}, {5}) + timeCorrection,", chunk.LogicalEndTime.Year, chunk.LogicalEndTime.Month, chunk.LogicalEndTime.Day, chunk.LogicalEndTime.Hour, chunk.LogicalEndTime.Minute, chunk.LogicalEndTime.Second)
				writer.WriteLine("\t\t\t\"Entity\": [e for e in entities if e.EntityName == \"{0}\"][0],", chunk.Entity.EntityName)
				writer.WriteLine("\t\t\t\"Device\": device })")
				
				writer.WriteLine("\t\tchunkContentList = List[EntityObject]()")
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
					writer.WriteLine("\t\tchunkContentList.Add(dc.Create{0}({{ {1} }}))", chunk.Entity.EntityName, signalContent.ToString())
				writer.WriteLine("\t\tchunk.Content = chunkContentList")
				writer.WriteLine("\t\tdc.SaveObject(chunk)")
		writer.WriteLine("\texcept:")
		writer.WriteLine("\t\tif (dc.DbClient.TransactionCount > 0):")
		writer.WriteLine("\t\t\tdc.DbClient.RollbackTransaction()")
		writer.WriteLine("\t\traise")
		writer.WriteLine("\tfinally:")
		writer.WriteLine("\t\tif (dc.DbClient.TransactionCount > 0):")
		writer.WriteLine("\t\t\tif(persist):")
		writer.WriteLine("\t\t\t\tdc.DbClient.CommitTransaction()")
		writer.WriteLine("\t\t\telse:")
		writer.WriteLine("\t\t\t\tdc.DbClient.RollbackTransaction()")
		
	finally:
		writer.Close()
