(function () {
	'use strict';

	define(function (require) {

		const [ angular, _ ] = [ require('angular'), require('lodash') ];

		return [ 'auth', class AuthenticationForm {

			constructor(module) {

				this.$$ctrl = module;
				this.id = null;
				this.password = null;
				this.$errors = {};
			}

			error(key) { return (this.$errors[key] || false); }
			submit() {

				this.$errors = {};
				this.id = this.id.trim();
				this.password = this.password.trim();

				if (!!(this.id && this.password)) {

					const id = this.id;
					const password = btoa(this.password);
					console.log(password);

					// Send the response by HTTP POST
					const $http = this.$$ctrl.$$inject.get('$http');
					$http.post(`/accounts/login/`, { 'id': id, 'password': password }, { 'headers': { 'X-CSRFToken': this.$$ctrl.$csrf } })
					.then(({ 'data': data }) => {

						this.$$ctrl.$token = `${data['user']['id']}:${data['token']}`;
						this.$$ctrl.$user = data['user'];
					});
				}
				else {

					if (!this.id) this.$errors['id'] = 'User ID cannot be empty';
					if (!this.password) this.$errors['password'] = 'Password cannot be empty';
				}
			}

		} ];
	});

})();
