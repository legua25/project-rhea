(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		return class RheaProgram extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);

				const token = this.$token;
				if (token) this.$$token = token.split(':', 2)[1];

				this.$program = false;
			}

			$init(rhea) {

				rhea.$extras.title = 'Programs';

				const user = rhea.$user.id;
				this.list(user).then(() => { this.view(user, this.$routeParams['id'] || false); });
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
			view(user, acronym, size = 15, page = 1) {

				if (acronym !== false) {

					return this.$http.get(`/curricula/programs/${acronym}/?size=${size}&page=${page}`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					})
					.then(({ data }) => {

						this.$program = data['program'];
						return {
							'entries': this.$program.subjects,
							'pagination': {
								'page': data['pagination']['current'],
								'next': data['pagination']['next'],
								'previous': data['pagination']['previous']
							}
						};
					});
				}
			}

		};
	});

})();
