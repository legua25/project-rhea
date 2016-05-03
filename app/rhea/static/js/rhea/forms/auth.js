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

				if (!!(this.id && this.password))
					this.$$ctrl.login(this.id, btoa(this.password));
				else {

					if (!this.id) this.$errors['id'] = 'User ID cannot be empty';
					if (!this.password) this.$errors['password'] = 'Password cannot be empty';
				}
			}

		} ];
	});

})();
