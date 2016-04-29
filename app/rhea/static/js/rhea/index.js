(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		const max = 4, min = 1;
		const app = angular.module('rhea', [ 'ngAria', 'ngCookies' ]);

		app.controller('Rhea', class Rhea extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);
				require('rhea/forms/index')(this);

				// Properties
				const $cookies = this.$cookies;
				Object.defineProperties(this, {
					'$csrf': { 'configurable': false, get() { return $cookies.get('csrftoken'); } },
					'$token': {
						'configurable': false,
						get() { return $cookies.get('rheatoken'); },
						set(token) {

							if (token === undefined) $cookies.remove('rheatoken');
							else {

								// Expires in a day
								const expires = new Date(Date.now());
								expires.setDate(expires.getDate() + 1);

								$cookies.put('rheatoken', token, { 'expires': expires });
							}
						}
					}
				});

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
					this.$http.get(`/accounts/${id}/${token}/`, { 'headers': { 'X-CSRFToken': this.$csrf } }).then(({ 'data': data }) => {

						if (data['token'] !== false) {

							this.$user = data['user'];
							this.$extras['title'] = 'Home';
						}
						else
							this.$extras['title'] = 'Log in';
					});
				}
				else
					this.$extras['title'] = 'Log in';
			}
			login(id, password) {

				// Send the service call to log in the user with credentials
				this.$http.post(`/accounts/login/`, { 'id': id, 'password': password }, { 'headers': { 'X-CSRFToken': this.$csrf } }).then(({ 'data': data }) => {

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

		return app;
	});

})();
