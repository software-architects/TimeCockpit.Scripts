# Signal Data Export Sample

# Introduction

When [time cockpit](http://www.timecockpit.com) stores a user's activity log,
it encrypts the data with the user's signal data password. Therefore, nobody
else can read her activity log.

In some situations it might be useful to export a user's activity log
and import it in a different user account or even a different time cockpit
subscription. Such situations could be:

* Trainings
* Product demos
* Standardized test scenarios

The script in this sample can be used to auto-generate a script that you
can use to recreate the activity log of a given day/device in any 
account you like.

# How to Use the Script

## Exporting the Activity Log

The core export logic can be found in [ExportSignalsToScript.py](ExportSignalsToScript.py).
Typically, you do not need to change this script.

[SampleExport.py](SampleExport.py) shows how to use the export script to
export activity logs for specified dates and devices. Note that the
export script can generate a target file (*exportSignalsToFile* method)
or write the result into a stream (*exportSignalsToStream* method).
[SampleExport.py](SampleExport.py) contains examples for how to call
both methods.

The workflow for **exporting** looks like this:

* Find out the dates and devices you want to export using time cockpit's
  graphical calendar.

* Create a new, empty directory on your disk and save [ExportSignalsToScript.py](ExportSignalsToScript.py)
  and [SampleExport.py](SampleExport.py) there.

* Change your local copy of *SampleExport.py* so that it exports the
  dates and devices that you want to export.

* Start time cockpit with the user whose activity log you want to export.
  Note that you **will need the user's password and her signal data password**.
  It is **not possible** to export a different user's activity log even if you
  are a time cockpit administrator.

* Switch to time cockpit's *Customization* module. If you do not see this 
  module in time cockpit, the user is no time cockpit administrator. 
  Exporting the activity log **requires the scripting feature** of time cockpit.
  Only time cockpit administrators have access to it. So you need to at 
  least temporarily **give the user** whose activity log should be exported
  **administrative privileges**.

* Open and execute your local, adapted copy of *SampleExport.py*.

## Importing the Activity Log

Once you exported the activity log, you can use the resulting script files
to regenerate it in any other account or subscription.

The workflow fpr **importing** looks like this:

* Start time cockpit with the user into who you want to import the
  activity log. Note that you **will need the user's password and her 
  signal data password**. It is **not possible** to import into a 
  different user's activity log even if you are a time cockpit administrator.

* Switch to time cockpit's *Customization* module. If you do not see this 
  module in time cockpit, the user is no time cockpit administrator. 
  Importing the activity log **requires the scripting feature** of time cockpit.
  Only time cockpit administrators have access to it. So you need to at 
  least temporarily **give the user** whose activity log should be imported
  **administrative privileges**.

* Open the generated script in time cockpit (choose *Open / Open Python 
  Script* in the Ribbon).

* Uncomment and adapt the last two lines in the generated script as needed.

* Execute the script.

If you switch back to the calendar and reload all data, you should see
the imported activity log.

## Important Tips

If you need to run the import multiple times, you can delete the activity log
using time cockpits *Delete signals* wizard. You find it in the
calendar's Ribbon.
