(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const _ = require('lodash');
		const Controller = require('rhea/controller');

		return class RheaUser extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);

				const token = this.$token;
				if (token) this.$$token = token.split(':', 2)[1];

				this.$user = false;
				this.$type = 'user';
				this.$times = [

					'07:00 08:30',
					'08:30 10:00',
					'10:00 11:30',
					'11:30 13:00',
					'13:00 14:30',
					'14:30 16:00',
					'16:00 17:30',
					'17:30 19:00',
					'19:00 20:30',
					'20:30 22:00'

				];
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
			course(day, time) {

				if ((!!this.$user.schedule) !== false) {

					const result = _.find(this.$user.schedule.entries, { 'slots': [ { day, time } ] });
					if (result !== undefined) {

						return `<p class="course-entry">
							<a href="#/subject/${result.code}/"><span class="badge">${result.code.toUpperCase()}</span></a>
						</p>`;
					}
				}

				return `&nbsp;`;
			}

		};
	});

})();
