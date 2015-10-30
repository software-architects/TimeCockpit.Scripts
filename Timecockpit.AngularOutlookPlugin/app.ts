/// <reference path="typings/tsd.d.ts" />

'use strict';

/** Project data structures */
interface IProject {
	APP_ProjectUuid: string;
	APP_Code: string;
}
interface IOdataResult<T> {
	value: T[];
}

/** Controller for project list */
class ProjectListController {
	private token: string;

	constructor(private $http: ng.IHttpService, private $location: ng.ILocationService) {
		// Check if there is already a token in local storage
		this.token = localStorage.getItem("ProjectPickerToken");
		if (!this.token) {
			// No token -> redirect to login page
			$location.url('/getToken');
		} else {
			this.refreshProjectListAsync();
		}
	}

	// Variables used for data binding	
	public projects: IProject[];
	public isLoading: boolean = false;
	
	/** Refreshes the project list */
	private refreshProjectListAsync() {
		// Indicate that loading operation is running.
		// Controls loading indicator
		this.isLoading = true;
		
		// Get project list using OData
		this.$http.get<IOdataResult<IProject>>(
			"https://apipreview.timecockpit.com/odata/APP_Project?$select=APP_ProjectUuid,APP_Code&$top=20&$orderby=APP_Code",
			{ headers: { "Authorization": "Bearer " + this.token } })
			.then(
				// Success -> save project list
				projects => this.projects = projects.data.value,
				// Error -> if unauthorized, redirect to login page
				err => { if (err.status === 401) { this.$location.url("/getToken"); } })
			// Reset loading indicator
			.finally(() => this.isLoading = false)
	}
	
	/** Transfers project code to current appointment's subject field */
	public pickAppointment(projectCode: string) {
		var currentAppointment = <Office.Types.AppointmentCompose>Office.context.mailbox.item;
		currentAppointment.subject.setAsync("Working on project '" + projectCode + "'");
	}
}

/** Controller for login form */
class GetTokenController {
	constructor(private $http: ng.IHttpService, private $location: ng.ILocationService) {
	}
	
	// Variables used for data binding	
	public userName: string;
	public password: string;
	public loginError: boolean;
	
	/** Gets the token using basic auth */
	public getToken() {
		if (this.userName && this.password) {
			// Convert user:password to base64
			var base64UserPassword = window.btoa(this.userName + ':' + this.password);
			
			// Get the bearer token using user + password
			this.$http.get<string>(
				"https://apipreview.timecockpit.com/token", 
				{ headers: { "Authorization": "Basic " + base64UserPassword } })
				.then(
					// Success -> save token in local storage
					token => this.saveToken(token.data), 
					// Error -> activate error message
					_ => this.loginError = true);
		}
	}
	
	/** Saves token in local storage and redirects to project list */
	private saveToken(token: string) {
		localStorage.setItem("ProjectPickerToken", token);
		this.$location.url("/projectList");
	}
}

// Setup angular application
angular.module('ProjectPicker', [ 'ngRoute' ])
	.controller('projectListController', ProjectListController)
	.controller('getTokenController', GetTokenController)
	.config(($routeProvider : angular.route.IRouteProvider) => {
		$routeProvider
			.when('/projectList', { 
				template: `
				<h1>Project List</h1>
				<p class="text-info" ng-show="vm.isLoading">
					Loading projects from time cockpit ...
				</p>
				<table class="table table-hover">
					<tr ng-repeat="p in vm.projects"
					    ng-click="vm.pickAppointment(p.APP_Code)">
						<td>{{ p.APP_Code }}</td>
					</tr>
				</table>
				`,
				controller: 'projectListController',
				controllerAs: 'vm'
			})
			.when('/getToken', { 
				template: `
				<h1>Login</h1>
				<form>
					<div class="form-group">
						<label for="userName">User:</label>
						<input type="email" class="form-control" id="userName" 
						       placeholder="Time cockpit user name ..."
							   ng-model="vm.userName">
					</div>
					<div class="form-group">
						<label for="password">Password:</label>
						<input type="password" class="form-control" id="password" 
						       placeholder="Time cockpit password ..."
							   ng-model="vm.password">
					</div>
					<p class="text-warning" ng-show="vm.loginError">
						There was an error logging in. Correct password?
					</p>
					<button class="btn btn-default" ng-click="vm.getToken()"
						    ng-disabled="!vm.userName || !vm.password">Login</button>
				</form>
				`,
				controller: 'getTokenController',
				controllerAs: 'vm'
			})
			.otherwise({ redirectTo: '/projectList' });
	});

	// Add office initializer
	Office.initialize = () => {
		angular.bootstrap(jQuery('#container'), ['ProjectPicker']);
	};
