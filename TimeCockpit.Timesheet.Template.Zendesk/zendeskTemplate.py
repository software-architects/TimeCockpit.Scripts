def getTimesheetsFromZendesk(templateQueryContext):
	# --- setup zendesk settings ---
	serverURL = "https://yourZendeskHost"
	userName = "yourUserName"
	token = "yourZendeskToken"
	# --- setup zendesk settings ---

	clr.AddReference("System.Web")
	clr.AddReference("System.Net.Http")
	clr.AddReference("Newtonsoft.Json")
	from System.Text import Encoding
	from Newtonsoft.Json.Linq import JObject
	from System.Collections.Generic import List
	from System.Web import HttpUtility
	from System.Net.Http import HttpClient
	from System.Net.Http.Headers import AuthenticationHeaderValue

	user = Context.SelectSingleWithParams({
		"Query": "From U In UserDetail Where U.UserDetailUuid = @UserDetailUuid Select U",
		"@UserDetailUuid": templateQueryContext.UserDetailUuid
	})

	query = HttpUtility.UrlEncode("type:ticket updated:" + templateQueryContext.BeginTime.ToString("yyyy-MM-dd") + " assignee:" + user.Username) 
	queryURL = serverURL + "/api/v2/search.json?query=" + query

	credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes(userName + "/token:"+ token));

	modelEntity = ModelEntity({ "Name": "Result" })
	modelEntity.Properties.Add(TextProperty({ "Name": "Description" }))
	modelEntity.Properties.Add(TextProperty({ "Name": "ResultTitle" }))
	modelEntity.Properties.Add(TextProperty({ "Name": "ResultSortOrder" }))

	result = List[EntityObject]()

	with HttpClient() as client:
		client.DefaultRequestHeaders.Authorization = AuthenticationHeaderValue("Basic", credentials)
		response = client.GetAsync(queryURL).Result
		response.EnsureSuccessStatusCode()

		text = response.Content.ReadAsStringAsync().Result
		json = JObject.Parse(text)

		for item in json.results:
			id = str(item.id)
			name = str(item.via.source["from"].name)
			subject = str(item.subject)
			status = str(item.status)

			entity = modelEntity.CreateEntityObject()
			entity.Description = "#" + id + ": " + subject + " (" + name + ", " + status + ")"
			entity.ResultTitle = entity.Description
			entity.ResultSortOrder = entity.Description
			result.Add(entity)

	templateQueryContext.Templates = result
