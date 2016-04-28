(function () {
	'use strict';

	define([

		'rhea/forms/auth'

	], function (... forms) {

		return function register_forms(module) {

			module.$forms = {};
			Array.prototype.map.call(forms, ([ name, form ]) => {
				module.$forms[name] = new form(module);
			});
		};
	});

})();
