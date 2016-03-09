(function () {
	'use strict';

	// Paginator class
	define([], function () {

		return class Paginator extends null {

			constructor(source, page = 1, size = 10) {

				if (typeof source !== 'function')
					throw new TypeError('"source" must be a function returning a promise');

				this.source = source;
				this.$data = [];
				this.$update(page, size);

				Object.defineProperties(this, {
					'count': { 'configurable': false, get() { return this.$total; } },
					'has_previous': { 'configurable': false, get() { return !!this.$prev; } },
					'has_next': { 'configurable': false, get() { return !!this.$next; } },
					'page': { 'configurable': false, get() { return this.$page } },
					'entries': {
						'configurable': false,
						get() {

							// The "entries" property is a view of the current entries using a generator
							return (function* (entries) { yield *entries; })(this.$data);
						}
					}
				});
			}

			$update(page, size) {

				return this.source(page, size).then(function (data) {

					// We are assuming that the response contains a "meta" component and a list of "entries"
					const meta = data.meta;
					const entries = data.entries;

					this.$page = meta.current;
					this.$total = meta.total;
					this.$prev = meta.prev;
					this.$next = meta.next;
					this.$size = meta.size;
					this.$data = entries;
				});
			}
			next() {

				// We can only request "next" if there are entries to go to
				return (this.$next !== false && !!this.$update(this.$next, this.$size));
			}
			previous() {

				// We can only request "previous" if there are entries to go to
				return (this.$prev !== false && !!this.$update(this.$prev, this.$size));
			}
			first() { return !!this.$update(1, this.$size); }
			last() { return !! this.$update(this.$total, this.$size); }
			resize(size) { return this.$update(1, size); }

		};
	});

})();
