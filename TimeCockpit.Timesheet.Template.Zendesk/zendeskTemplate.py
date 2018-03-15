clr.AddReference("System")
clr.AddReference("Newtonsoft.Json")
from System.Net import *
from System.IO import *
from System.Text import *
from Newtonsoft.Json import *
from System.Collections.Generic import List
 
def getTimesheets(templateQueryContext):
    user = Context.SelectSingleWithParams({
        "Query": "From U In UserDetail Where U.UserDetailUuid = @UserDetailUuid Select U",
        "@UserDetailUuid": templateQueryContext.UserDetailUuid
    })
     
    # --- setup zendesk settings ---
    serverURL = "https://yourZendeskURL/api/v2/search.json?query=type:ticket+updated:" + templateQueryContext.BeginTime.ToString("yyyy-MM-dd") + "+assignee:'" + user.Firstname + " " + user.Lastname + "'"
    userName = "yourUserName"
    token = "yourZendeskToken"
    # --- setup zendesk settings ---
     
    credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes(userName + "/token:"+ token));
     
    modelEntity = ModelEntity({ "Name": "Result" })
    modelEntity.Properties.Add(TextProperty({ "Name": "Description" }))
    modelEntity.Properties.Add(TextProperty({ "Name": "ResultTitle" }))
    modelEntity.Properties.Add(TextProperty({ "Name": "ResultSortOrder" }))
     
    request = HttpWebRequest.Create(serverURL)
    request.Headers.Add("Authorization", "Basic " + credentials);
    request.ContentLength = 0
    request.Method = "GET"
    request.ContentType = "application/json"
    request.PreAuthenticate = True
     
    response = request.GetResponse()
    streamReader = StreamReader(response.GetResponseStream())
     
    result = List[EntityObject]()
     
    counter = 0
    jsonReader = JsonTextReader(streamReader)
    id = ""
    name = ""
    subject = ""
    status = ""
    returnLevel = 0
    objectInProgress = False
     
    jsonReader.Read()
    jsonReader.Read()
    jsonReader.Read()
     
    while jsonReader.Read():
        if jsonReader.TokenType == JsonToken.StartObject:
            if not objectInProgress:
                objectInProgress = True
                returnLevel = counter
                entity = modelEntity.CreateEntityObject()
                entity.Description = ""
                id = ""
                name = ""
                subject = ""
                status = ""
                 
            counter = counter + 1
        elif jsonReader.TokenType == JsonToken.EndObject:
            counter = counter - 1
            if counter == returnLevel:
                objectInProgress = False
                     
                entity.Description = "#" + id + ": " + subject + " (" + name + ", " + status + ")"
                entity.ResultTitle = entity.Description
                entity.ResultSortOrder = entity.Description
                result.Add(entity)
        elif jsonReader.TokenType == JsonToken.PropertyName:
            token = jsonReader.Value.ToString()
            if token == "id" and counter == 1:
                jsonReader.Read()
                if jsonReader.Value != None:
                    id = jsonReader.Value.ToString()
                     
            elif token == "name":
                jsonReader.Read()
                if jsonReader.Value != None and jsonReader.Value.ToString() != "time cockpit":
                    name = jsonReader.Value.ToString()
                     
            elif token == "subject":
                jsonReader.Read()
                if jsonReader.Value != None:
                    subject = jsonReader.Value.ToString()
         
            elif token == "status":
                jsonReader.Read()
                if jsonReader.Value != None:
                    status = jsonReader.Value.ToString()
                     
            else:
                jsonReader.Read()
                if jsonReader.TokenType == JsonToken.StartObject:
                    counter = counter + 1
                elif jsonReader.TokenType == JsonToken.StartObject:
                    counter = counter - 1
                     
    templateQueryContext.Templates = result