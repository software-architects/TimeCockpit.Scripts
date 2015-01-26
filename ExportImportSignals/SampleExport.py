# -*- coding: utf-8 -*-

# Script for generating demo data
dc = Context

basePath = r"C:\Code\Github_TimeCockpit.Scripts\ExportImportSignals"
execfile(basePath + r"\ExportSignalsToScript.py")

exportSignals(Context, DateTime(2015, 1, 26), "SIERRA3", basePath + "\\SampleScenario.py", "SampleScenario", "SampleScenario", True, True)
print "Done!"
