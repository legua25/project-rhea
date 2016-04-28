(function () {
	'use strict';

	define(function (require) {

		const [ angular, _ ] = [ require('angular'), require('lodash') ];

		const max = 4, min = 1;
		const app = angular.module('rhea', [ 'ngAria', 'ngCookies' ]);
		const register_forms = require('rhea/forms/index');

		app.controller('Rhea', class Rhea {

			constructor ($scope, $cookies, $http, $injector) {

				this.$$inject = $injector;
				register_forms(this);

				Object.defineProperties(this, {
					'$csrf': { 'configurable': false, get() { return $cookies.get('csrftoken'); } },
					'$token': {
						'configurable': false,
						get() { return $cookies.get('rheatoken'); },
						set(token) {

							// Expires in a day
							const expires = new Date(Date.now());
							expires.setDate(expires.getDate() + 1);

							$cookies.put('rheatoken', token, { 'expires': expires });
						}
					}
				});

				this.$extras = {
					'background': Math.floor(Math.random() * (max - min)) + min
				};
				this.$title = 'Untitled';

				// Check if we have a user or not
				if (this.$token !== undefined) {

					let [ id, token ] = this.$token.split(':', 2);
					$http.get(`/accounts/${id}/${token}/`, { 'headers': { 'X-CSRFToken': this.$csrf } }).then(({ 'data': data }) => {
						this.$user = data['user'];
					});
				}
				else {

					this.$user = false;
					this.$title = 'Log in'
				}
			}

		});

		return app;
	});

})();
