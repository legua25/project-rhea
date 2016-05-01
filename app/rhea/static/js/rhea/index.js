(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		const max = 4, min = 1;
		const app = angular.module('rhea', [ 'ngAria', 'ngCookies', 'ngRoute' ]);

		app.controller('Rhea', class Rhea extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);
				require('rhea/forms/index')(this);

				this.$extras = {
					'background': (Math.floor(Math.random() * (max - min)) + min),
					'title': 'Untitled'
				};
				this.$user = false;

				this.validate();
			}

			// Authentication calls
			validate() {

				// Check if we have a user or not
				if (this.$token !== undefined) {

					let [ id, token ] = this.$token.split(':', 2);
					this.$http.get(`/accounts/${id}/${token}/`, { 'headers': { 'X-CSRFToken': this.$csrf } }).then(({ data }) => {

						if (data['token'] !== false) {

							this.$user = data['user'];
							this.$extras['title'] = 'Home';
						}
						else
							this.$extras['title'] = 'Log in';
					});
				}
				else {

					this.$location.url('/login/');
					this.$extras['title'] = 'Log in';
				}
			}
			login(id, password) {

				// Send the service call to log in the user with credentials
				this.$http.post(`/accounts/login/`, { 'id': id, 'password': password }, { 'headers': { 'X-CSRFToken': this.$csrf } }).then(({ data }) => {

					this.$location.url('/');
					this.$token = `${data['user']['id']}:${data['token']}`;
					this.$user = data['user'];
					this.$extras['title'] = 'Home';
				});
			}
			logout() {

				// Request the system to discard the user session
				this.$http.get(`/accounts/logout/`, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${this.$user.id}:${this.$token}`
					}
				}).then(() => {

					this.$token = undefined;
					this.$user = false;
					this.$extras['title'] = 'Log in';
				});
			}

		});
		app.directive('paginator', require('rhea/directives/pagination'));
		app.config([ '$routeProvider', ($router) => {

			$router.when('/', { 'templateUrl': '/view/parts.profile/', 'controller': require('rhea/controller/profile'), 'controllerAs': 'profile' })
				   .when('/program/:id?/?', { 'templateUrl': '/view/parts.program/', 'controller': require('rhea/controller/program'), 'controllerAs': 'list' })
				   .when('/subject/:id?/?', { 'templateUrl': '/view/parts.subject/', 'controller': require('rhea/controller/subject'), 'controllerAs': 'list' })
				   .when('/user/:id?/?', { 'templateUrl': '/view/parts.user/', 'controller': require('rhea/controller/user'), 'controllerAs': 'list' })
				   .when('/manage/', { 'templateUrl': '/view/parts.management/', 'controller': require('rhea/controller/management'), 'controllerAs': 'manage' })
				   .when('/login/', {}).when('/logout/', {})
				   .otherwise('/');
		} ]);

		return app;
	});

})();
