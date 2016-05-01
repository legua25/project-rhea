(function () {
	'use strict';

	define(function (require) {

		const angular = require('angular');
		const _ = require('lodash');
		const Controller = require('rhea/controller');

		return class RheaProfile extends Controller {

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

				rhea.$extras.title = 'Your Profile';

				this.$http.get(`/users/${rhea.$user.id}/`, {
					'headers': {
						'X-CSRFToken': this.$csrf,
						'HTTP-Authentication': `Basic ${rhea.$user.id}:${this.$$token}`
					}
				})
				.then(({ data }) => {

					this.$type = data['type'];
					this.$user = data['user'];
				});
			}
			expiry() {

				if (this.$user !== false) {

					const date = new Date(this.$user.availability.expires);
					return date.toLocaleDateString('en-us', {
						'day': 'numeric',
						'month': 'long',
						'year': 'numeric'
					});
				}

				return 'N/A';
			}
			availability(day, time) {

				const result = _.find(this.$user.availability.entries, { day, time });
				const level = (result !== undefined) ? result.level : 0.0;

				switch (level) {
					case 0.0: return 0;
					case 0.25: return 1;
					case 0.5: return 2;
					case 1.0: return 3;
				}
			}

		};
	});

})();
