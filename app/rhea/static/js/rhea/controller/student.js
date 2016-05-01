(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		return class RheaStudent extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);

				const token = this.$token;
				if (token) this.$$token = token.split(':', 2)[1];

			}

			$init(rhea) {

				rhea.$extras.title = 'Update Subjects';

				const user = rhea.$user.id;
			}
			list(user, size = 15, page = 1) {

				return this.$http.get(`/curricula/programs/?size=${size}&page=${page}`, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${user}:${this.$$token}`
					}
				})
				.then(({ data }) => {

					return {
						'entries': data['programs'],
						'pagination': {
							'page': data['pagination']['current'],
							'next': data['pagination']['next'],
							'previous': data['pagination']['previous']
						}
					};
				});
			}

		};
	});

})();
