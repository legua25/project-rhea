(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const Controller = require('rhea/controller');

		return class RheaManagement extends Controller {

			constructor ($scope, $injector) {

				super($scope, $injector);

				const token = this.$token;
				if (token) this.$$token = token.split(':', 2)[1];

				this.$pane = false;
				this.$panes = [
					{ 'title': 'program' },
					{ 'title': 'student' },
					{ 'title': 'instructor' },
					Object.defineProperty({ 'title': 'schedule', 'data': false }, 'tab', (function () {

						let $tab = 0;
						const $data = {};

						return {
							'configurable': false,
							get() { return $tab; },
							set(tab) {

								if (this.data !== false) {

									$data[$tab] = this.data;
									this.data = false;
								}

								$tab = tab;
								if ($data[tab] !== undefined) this.data = $data[tab];
							}
						};
					})())
				];
				this.$times = [

					'07:00 - 08:30',
					'08:30 - 10:00',
					'10:00 - 11:30',
					'11:30 - 13:00',
					'13:00 - 14:30',
					'14:30 - 16:00',
					'16:00 - 17:30',
					'17:30 - 19:00',
					'19:00 - 20:30',
					'20:30 - 22:00'

				];
			}

			$init(rhea) { rhea.$extras.title = 'Management'; }
			select(pane) {

				if (pane !== this.$pane)
					this.$pane = (this.$panes.find(e => { return e.title === pane; }) || false);
				else
					this.$pane = false;
			}
			export_file(data, name) {

				// Serialize the data, then create a download link
				const url = URL.createObjectURL(new Blob([ JSON.stringify(data) ], { 'type': 'octet/stream' }));
				const link = $(`<a href="${url}" download="${name}.json"></a>`);
				link.css({ 'display': 'none' });

				// Execute the click, then clean up
				$('body').append(link);
				link.get(0).click();
				link.detach();
				URL.revokeObjectURL(url);
			}

			run_subjects(user) {

				this.$http.post(`/schedule/subjects/`, undefined, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${user}:${this.$$token}`
					}
				})
				.then(({ data }) => {

					const coverage = (data['stats']['coverage'] * 100);
					const start = new Date(data['stats']['start'] * 1000);
					const elapsed_sec = (data['stats']['elapsed'] / 1000000);
					const elapsed_hour = +(Math.round((elapsed_sec / 3600) + 'e+2') + 'e-2');

					this.$pane.export = () => {
						this.export_file({ 'subjects': data['subjects'].map(({ id }) => { return id; }) }, 'step-1-subjects');
					};
					this.$pane.data = {
						'coverage': +(Math.round(coverage + 'e+2') + 'e-2'),
						'start': start.toLocaleDateString('en-US', {
							'minute': '2-digit',
							'hour': '2-digit',
							'day': 'numeric',
							'month': 'short',
							'year': 'numeric'
						}),
						'elapsed': {
							'seconds': elapsed_sec,
							'hours': (elapsed_hour > 1.0) ? `about ${elapsed_hour} hour(s)` : 'less than an hour'
						},
						'subjects': data['subjects']
					};
				});
			}
			run_courses(user) {

				const input = $('input[type="file"]#courses-list');
				if (input.val()) {

					const reader = new FileReader();
					reader.onload = () => {

						const data = reader.result;
						this.$http.post(`/schedule/courses/`, JSON.parse(data), {
								'headers': {
									'X-CSRFToken': this.$csrf,
									'HTTP-Authentication': `Basic ${user}:${this.$$token}`
								}
							})
							.then(({ data }) => {

								const start = new Date(data['stats']['start'] * 1000);
								const elapsed_sec = (data['stats']['elapsed'] / 1000000);
								const elapsed_hour = +(Math.round((elapsed_sec / 3600) + 'e+2') + 'e-2');

								this.$pane.data = {
									'start': start.toLocaleDateString('en-US', {
										'minute': '2-digit',
										'hour': '2-digit',
										'day': 'numeric',
										'month': 'short',
										'year': 'numeric'
									}),
									'elapsed': {
										'seconds': elapsed_sec,
										'hours': (elapsed_hour > 1.0) ? `about ${elapsed_hour} hour(s)` : 'less than an hour'
									},
									'courses': data['courses']
								};
								this.$pane.serialize = (slots) => {

									let days = [ '·', '·', '·', '·', '·' ];
									let hours = '';

									for (let { day, time } of slots) {

										switch (day) {
											case 0: days[0] = 'M'; break;
											case 1: days[1] = 'T'; break;
											case 2: days[2] = 'W'; break;
											case 3: days[3] = 'X'; break;
											case 4: days[4] = 'F'; break;
										}
										hours = this.$times[time];
									}

									return [ days.join(' '), hours ];
								};
								this.$pane.export = () => {

									this.export_file({ 'courses': data['courses'].map(e => {
										return { 'instructor': e.instructor.id, 'subject': e.subject.code, 'slots': e.slots };
									}) }, 'step-2-courses');
								};
							});
					};

					reader.readAsText(input.get(0).files[0]);
				}
			}
			run_update(user) {

				let request = null;
				if (this.$pane.data.token === undefined) {

					request = this.$http.get(`/schedule/update/`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					});
				}
				else {

					request = this.$http.get(`/schedule/update/${this.$pane.data.token}/`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					});
				}

				request.then(({ data }) => {

					const coverage = (data['execution']['stats']['coverage'] * 100);
					const start = new Date(data['execution']['stats']['start'] * 1000);
					const elapsed_sec = (data['execution']['stats']['elapsed'] / 1000000);
					const elapsed_hour = +(Math.round((elapsed_sec / 3600) + 'e+2') + 'e-2');

					this.$pane.data = {
						'token': data['token'],
						'coverage': +(Math.round(coverage + 'e+2') + 'e-2'),
						'start': start.toLocaleDateString('en-US', {
							'minute': '2-digit',
							'hour': '2-digit',
							'day': 'numeric',
							'month': 'short',
							'year': 'numeric'
						}),
						'elapsed': {
							'seconds': elapsed_sec,
							'hours': (elapsed_hour > 1.0) ? `about ${elapsed_hour} hour(s)` : 'less than an hour'
						},
						'instructors': data['execution']['pending'].map(e => { return (e['instructor'] !== undefined ? e['instructor'] : e); })
					};
					this.$pane.export = () => {
						this.export_file({ 'pending': data['execution']['pending'], 'token': data['token'] }, 'step-0-update');
					};
				});
			}
			run_selection(user) {

				let request = null;
				if (this.$pane.data.token === undefined) {

					request = this.$http.get(`/schedule/selection/`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					});
				}
				else {

					request = this.$http.get(`/schedule/selection/${this.$pane.data.token}/`, {
						'headers': {
							'X-CSRFToken': this.$csrf,
							'HTTP-Authentication': `Basic ${user}:${this.$$token}`
						}
					});
				}

				request.then(({ data }) => {

					const coverage = (data['execution']['stats']['coverage'] * 100);
					const start = new Date(data['execution']['stats']['start'] * 1000);
					const elapsed_sec = (data['execution']['stats']['elapsed'] / 1000000);
					const elapsed_hour = +(Math.round((elapsed_sec / 3600) + 'e+2') + 'e-2');

					this.$pane.data = {
						'token': data['token'],
						'coverage': +(Math.round(coverage + 'e+2') + 'e-2'),
						'start': start.toLocaleDateString('en-US', {
							'minute': '2-digit',
							'hour': '2-digit',
							'day': 'numeric',
							'month': 'short',
							'year': 'numeric'
						}),
						'elapsed': {
							'seconds': elapsed_sec,
							'hours': (elapsed_hour > 1.0) ? `about ${elapsed_hour} hour(s)` : 'less than an hour'
						},
						'students': data['execution']['pending'].map(e => { return (e['student'] !== undefined ? e['student'] : e); })
					};
					this.$pane.export = () => {
						this.export_file({ 'pending': data['execution']['pending'], 'token': data['token'] }, 'step-3-selection');
					};
				});
			}
			run_gathering(user) {

				this.$http.post(`/schedule/gathering/`, undefined, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${user}:${this.$$token}`
					}
				})
				.then(({ data }) => {

					const total = data['stats']['total'];
					const coverage = (data['stats']['coverage'] * 100);
					const start = new Date(data['stats']['start'] * 1000);
					const elapsed_sec = (data['stats']['elapsed'] / 1000000);
					const elapsed_hour = +(Math.round((elapsed_sec / 3600) + 'e+2') + 'e-2');

					this.$pane.export = () => { this.export_file({ 'courses': data['courses'] }, 'step-4-gathering'); };
					this.$pane.serialize = (slots) => {

						let days = [ '·', '·', '·', '·', '·' ];
						let hours = '';

						for (let { day, time } of slots) {

							switch (day) {
								case 0: days[0] = 'M'; break;
								case 1: days[1] = 'T'; break;
								case 2: days[2] = 'W'; break;
								case 3: days[3] = 'X'; break;
								case 4: days[4] = 'F'; break;
							}
							hours = this.$times[time];
						}

						return [ days.join(' '), hours ];
					};
					this.$pane.data = {
						'total': total,
						'coverage': +(Math.round(coverage + 'e+2') + 'e-2'),
						'start': start.toLocaleDateString('en-US', {
							'minute': '2-digit',
							'hour': '2-digit',
							'day': 'numeric',
							'month': 'short',
							'year': 'numeric'
						}),
						'elapsed': {
							'seconds': elapsed_sec,
							'hours': (elapsed_hour > 1.0) ? `about ${elapsed_hour} hour(s)` : 'less than an hour'
						},
						'courses': data['courses']
					};
				});
			}

		};
	});

})();
