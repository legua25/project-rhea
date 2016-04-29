(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		return class RheaSubject extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);
				this.$subject = false;
			}

			$init(rhea) {

				const user = rhea.$user.id;
				this.list(user).then(() => { this.view(user, this.$routeParams['id'] || false); });
			}
			list(user, size = 15, page = 1) {

				return this.$http.get(`/curricula/subjects/?size=${size}&page=${page}`, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${user}:${this.$token}`
					}
				})
				.then(({ data }) => {

					return {
						'entries': data['subjects'],
						'pagination': {
							'page': data['pagination']['current'],
							'next': data['pagination']['next'],
							'previous': data['pagination']['previous']
						}
					};
				});
			}
			view(user, code, size = 15, page = 1) {

				if (code !== false) {

					return this.$http.get(`/curricula/subjects/${code}/?size=${size}&page=${page}`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$token}`
						}
					})
					.then(({ data }) => {

						this.$subject = data['subject'];
					});
				}
			}

		};
	});

})();
