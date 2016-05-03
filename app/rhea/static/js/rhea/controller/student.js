(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const $ = require('jquery');
		const Controller = require('rhea/controller');
		require('bootstrap');

		return class RheaStudent extends Controller {

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

				this.$table = this.$times.map(() => { return [ 0, 0, 0, 0, 0 ]; });
				this.$subjects = [];
				this.$subject = false;

				this.$scope.available = (instructor) => !this.occupied_by(instructor);
			}

			$init(rhea) {

				rhea.$extras.title = 'Select Courses';

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

					if (!!(this.$auth) === false || data['type'] !== 'student')
						this.$location.url('/');

					this.$http.get(`/schedule/selection/${this.$auth}/query/`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${rhea.$user.id}:${this.$$token}`
						}
					})
					.then(({ data }) => { this.$subjects = data['subjects']; });
				});
			}
			slots(instructor) {

				let days = [ '·', '·', '·', '·', '·' ];
				let hours = '';

				for (let { day, time } of instructor.slots) {

					switch (day) {
						case 0: days[0] = 'M'; break;
						case 1: days[1] = 'T'; break;
						case 2: days[2] = 'W'; break;
						case 3: days[3] = 'X'; break;
						case 4: days[4] = 'F'; break;
					}
					hours = this.$times[time];
				}

				return [ days.join(' '), hours.replace(' ', ' - ') ];
			};
			toggle(subject) {

				if (this.$subject !== false && this.$subject === subject)
					this.$subject = false;
				else
					this.$subject = subject;
			}
			occupied_by(instructor) {

				const slots = instructor.slots;
				for (let { day, time } of slots) {

					if (this.$table[time][day] !== 0)
						return true;
 				}

				return false;
			}
			add(instructor) {

				if (!this.occupied_by(instructor)) {

					const slots = instructor.slots;
					for (let { day, time } of slots) {

						this.$table[time][day] = {
							'subject': this.$subject,
							'instructor': instructor
						};
					}

					this.$subject = false;
				}
			}
			remove(day, time) {

				if (this.$table[time][day] !== 0) {

					const entry = this.$table[time][day];
					const slots = entry.instructor.slots;

					for (let { 'day': $day, 'time': $time } of slots)
						this.$table[$time][$day] = 0;
				}
			}
			course(day, time) {

				if (this.$table[time][day] !== 0) {

					const result = this.$table[time][day];
					if (result !== undefined) {

						return `<p class="course-entry" title="${result.instructor.name}">
							<span class="badge"><strong>${result.subject.code.toUpperCase()}</strong></span>
						</p>`;
					}
				}

				return `&nbsp;`;
			}
			submit(user) {

				const courses = this.$table.reduce(($carry, row, time) => {

					const data = [];
					for (let i = 0; i < row.length; i++) {

						const item = row[i];
						if (item !== 0) {

							data.push({
								'code': item.subject.code,
								'instructor': item.instructor.id,
								'day': i,
								'time': time
							});
						}
					}

					return $carry.concat(data);
				}, []);

				return this.$http.post(`/schedule/selection/${this.$auth}/`, { courses }, {
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
