(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		return class RheaUser extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);

				const token = this.$token;
				if (token) this.$$token = token.split(':', 2)[1];

				this.$user = false;
				this.$type = 'user';
			}

			$init(rhea) {

				rhea.$extras.title = 'Users';

				const user = rhea.$user.id;
				this.students(user).then(() => {

					this.instructors(user);
					this.view(user, this.$routeParams['id'] || false);
				});
			}
			students(user, size = 10, page = 1) {
				return this.list(`/users/?size=${size}&page=${page}&type=student`, user);
			}
			instructors(user, size = 10, page = 1) {
				return this.list(`/users/?size=${size}&page=${page}&type=instructor`, user);
			}
			list(url, user) {

				return this.$http.get(url, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${user}:${this.$$token}`
					}
				})
				.then(({ data }) => {

					return {
						'entries': data['users'],
						'pagination': {
							'page': data['pagination']['current'],
							'next': data['pagination']['next'],
							'previous': data['pagination']['previous']
						}
					};
				});
			}
			view(user, id) {

				if (id !== false) {

					this.$http.get(`/users/${id}/`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					})
					.then(({ data }) => {

						this.$user = data['user'];
						this.$type = data['type'];
					});
				}
			}

		};
	});

})();
