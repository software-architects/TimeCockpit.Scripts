from System import Environment

# Configuration
timeCockpitLocation = Environment.ExpandEnvironmentVariables(r"%ProgramW6432%\software architects\time cockpit\time cockpit 2010")
logFileName = r"python.log"

# Configuration file handling
import clr
clr.AddReference("System.Configuration")
from System.Configuration.Internal import IInternalConfigSystem
class ConfigurationProxy(IInternalConfigSystem):
    def __init__(self, fileName):
        from System import String
        from System.Collections.Generic import Dictionary
        from System.Configuration import IConfigurationSectionHandler, ConfigurationErrorsException
        self.__customSections = Dictionary[String, IConfigurationSectionHandler]()
        loaded = self.Load(fileName)
        if not loaded:
            raise ConfigurationErrorsException(String.Format("File: {0} could not be found or was not a valid cofiguration file.", fileName))

    def Load(self, fileName):
        from System.Configuration import ExeConfigurationFileMap, ConfigurationManager, ConfigurationUserLevel
        exeMap = ExeConfigurationFileMap()
        exeMap.ExeConfigFilename = fileName
        self.__config = ConfigurationManager.OpenMappedExeConfiguration(exeMap, ConfigurationUserLevel.None)
        return self.__config.HasFile
    
    def GetSection(self, configKey):
        if configKey == "appSettings":
            return self.__BuildAppSettings()
        return self.__config.GetSection(configKey)
    
    def __BuildAppSettings(self):
        from System.Collections.Specialized import NameValueCollection
        coll = NameValueCollection()
        for key in self.__config.AppSettings.Settings.AllKeys:
            coll.Add(key, self.__config.AppSettings.Settings[key].Value)
        return coll

    def RefreshConfig(self, sectionName):
        self.Load(self.__config.FilePath)
        
    def SupportsUserConfig(self):
        return False
    
    def InjectToConfigurationManager(self):
        from System.Reflection import BindingFlags
        from System.Configuration import ConfigurationManager
        configSystem = clr.GetClrType(ConfigurationManager).GetField("s_configSystem", BindingFlags.Static | BindingFlags.NonPublic)
        configSystem.SetValue(None, self)
    
from System.IO import Path
proxy = ConfigurationProxy(Path.Combine(timeCockpitLocation, "TimeCockpit.ExecuteScript.exe.config"))
proxy.InjectToConfigurationManager()

# References
clr.AddReferenceToFileAndPath(Path.Combine(timeCockpitLocation, "TimeCockpit.Data.dll"))
clr.AddReference("TimeCockpit.Common")
clr.AddReference("TimeCockpit.UI.Common")
clr.AddReference("System.Core")
import System
from TimeCockpit.Common import Logger, LogLevel
from TimeCockpit.UI.Common import TimeCockpitApplication, DataContextConnections, ConnectionType
clr.ImportExtensions(System.Linq)

# time cockpit DataContext
TimeCockpitApplication.Current.InitializeSettings()
Logger.Initialize(logFileName, TimeCockpitApplication.Current.ApplicationSettings.MinimumLogLevel)
TimeCockpitApplication.Current.InitializeDataContext(False, True)
connection = DataContextConnections.Current.Single(lambda dcc: dcc.ConnectionType == ConnectionType.ApplicationServer)
connection.InitializeOrThrow(False)
Context = connection.DataContext