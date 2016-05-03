(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const $ = require('jquery');
		const _ = require('lodash');
		const Controller = require('rhea/controller');
		require('bootstrap');

		return class RheaInstructor extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);

				const token = this.$token;
				if (token) this.$$token = token.split(':', 2)[1];

				this.$auth = false;
				this.$user = false;
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

				this.$list = [];
				this.$subjects = [];
				this.$table = this.$times.map(() => { return [ 0, 0, 0, 0, 0 ]; });
				this.$level = 1.0;
			}

			$init(rhea) {

				rhea.$extras.title = 'Update Subjects';

				const user = rhea.$user.id;
				this.$http.get(`/users/${rhea.$user.id}/`, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${rhea.$user.id}:${this.$$token}`
					}
				})
				.then(({ data }) => {

					this.$user = data['user'];
					this.$auth = this.$routeParams['token'];

					if (!!(this.$auth) === false || data['type'] !== 'instructor')
						this.$location.url('/');
				});
			}
			list(user, search) {

				if (!!search) {

					return this.$http.get(`/curricula/subjects/?query=${search}&size=5`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					})
					.then(({ data }) => {
						this.$list = data['subjects'];
					});
				}
				else
					this.$list = [];
			}
			toggle_cell(row, col) {

				if (this.$table[row][col] !== this.$level)
					this.$table[row][col] = this.$level;
				else
					this.$table[row][col] = 0.0;
			}
			toggle_row(row) {

				if (!this.$table[row].every(e => e === this.$level))
					this.$table[row].fill(this.$level);
				else
					this.$table[row].fill(0.0);
			}
			toggle_column(col) {

				let base = 0.0;
				for (let i = 0; i < this.$times.length; i++) {

					if (this.$table[i][col] !== this.$level) {

						base = this.$level;
						break;
					}
				}

				for (let i = 0; i < this.$times.length; i++)
					this.$table[i][col] = base;
			}
			availability(day, time) {

				const level = (this.$table[time][day] || 0.0);
				switch (level) {
					case 0.00: return 0;
					case 0.25: return 1;
					case 0.50: return 2;
					case 1.00: return 3;
				}
			}
			submit(user) {

				const data = {
					'subjects': this.$subjects.map(({ code }) => { return code; }),
					'schedule': this.$table.reduce(($carry, $days, $time) => {

						const data = [];
						for (let i = 0; i < $days.length; i++) {

							const level = $days[i];
							if (level > 0.0) data.push({ 'day': i, 'time': $time, 'level': level });
						}

						return $carry.concat(data);
					}, [])
				};

				return this.$http.post(`/schedule/update/${this.$auth}/`, data, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${user}:${this.$$token}`
					}
				})
				.then(() => {

					const modal = $('#confirm');

					modal.modal({ 'backdrop': 'static', 'show': true });
					modal.on('hidden.bs.modal', () => { this.$scope.$apply(() => { this.$location.url('/'); }); });

					setTimeout(() => { modal.modal('hide'); }, 1500);
				});
			}

		};
	});

})();
