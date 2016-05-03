# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from dateutil.relativedelta import relativedelta as timedelta
from django.utils.timezone import now
from collections import defaultdict
from _days import DayOfWeek
import random, copy


__all__ = [ 'ScheduleBuilder' ]

cdef int _evaluate(schedule, scores, total):

	inserted, conflicts = scores

	# Setting all subjects is worth 100 points given no conflicts occurred
	points = ((len(inserted) / total) * 100.0) - len(conflicts)

	# Check if the composition criteria are met
	for day, entries in schedule.iteritems():

		# The "three consecutive courses" rule only applies if more than three courses happen per day
		if len(day) > 3:

			consecutive = 0
			for time, subject in entries:

				# Transgressing the rule takes 25 points per day this occurs
				if (time - 1) in entries:

					consecutive += 1
					if consecutive >= 3: points -= 25
				else: consecutive = 0

	return points

cdef class ScheduleBuilder:

	cdef public object instructor
	cdef dict _entries
	cdef list _courses
	cdef public dict entries

	def __init__(self, instructor, available):

		self.instructor = instructor

		schedule = instructor.availability.entries.all().filter(active = True)
		subjects = instructor.specialties.all().filter(active = True, confidence__gt = 0.0, subject_id__in = available)[:4]
		days = len(DayOfWeek.__members__)

		if subjects.exists():

			self._entries = { subject: { day: defaultdict(lambda: 0.0) for day in range(days) } for subject in subjects.values_list('subject_id', flat = True) }
			self._courses = []

			# Initialize the probability matrix with what we know
			for (subject, confidence) in subjects.values_list('subject_id', 'confidence'):
				for (level, day, time) in schedule.values_list('level', 'day', 'time'):
					self._entries[subject][day][time] = (level * confidence)

			# Generate a schedule for this instructor
			subjects_list = [ subject for subject in subjects.values_list('subject_id', flat = True) ]
			slots_list = [ entry for entry in schedule.values_list('day', 'time') ]

			self.entries = self._refine(subjects_list, slots_list)
		else: self.entries = {}

	def save(self, schedule_type, course_type):

		# Disable the previous schedule (if any)
		if self.instructor.schedule:

			self.instructor.schedule.entries.all().update(active = False)
			self.instructor.schedule.active = False
			self.instructor.schedule.save()

		# Create the courses
		schedule = schedule_type.objects.create(expiry = now() + timedelta(months = 6))
		for ((day, time), id) in self.entries.iteritems():

			schedule.entries.add(course_type.objects.create(
				day = day,
				time = time,
				subject_id = id,
				instructor = self.instructor
			))

		# Change the instructor's schedule
		schedule.save()
		self.instructor.schedule = schedule
		self.instructor.save()

	cdef dict _refine(self, list subjects, list slots):

		# Build a randomized solution - count how many did we fit without collisions
		tabu_list = defaultdict(lambda: 0)
		entries, performance = self._create_solution(subjects, slots, tabu_list)
		score = _evaluate(entries, performance, total = len(subjects))

		while score < 100.0:

			candidates = []
			inserted, conflicts = performance

			# For each conflict, attempt to permute it with another subject
			for conflict in conflicts:
				for subject in inserted:

					# Create a copy of the entries so changes are not automatically propagated
					_entries = copy.deepcopy(entries)
					_tabus = copy.deepcopy(tabu_list)

					candidates.append((self._permute_solution(_entries, subject, conflict, slots, _tabus, count = len(subjects)), _tabus))

			# Get the best out of all candidates
			best, best_score, last_tabus = None, score, None
			for ((candidate, (added, failures)), tabus) in candidates:

				actual = ((inserted - failures) | added), ((conflicts - added) | failures)
				_score = _evaluate(candidate, actual, total = len(subjects))

				if _score > best_score:

					best = candidate
					best_score = _score
					last_tabus = tabus

			# Update the outermost state with the best element
			if best is not None:

				entries = best
				score = best_score
				tabu_list = last_tabus

		return entries
	cdef tuple _create_solution(self, subjects, slots, tabu_list):

		entries = {}
		conflicts, inserted = set(), set()

		# Fit all subjects into the allocated spaces - if unable, add it to the conflicts set
		for subject in subjects:
			self._insert_subject(subject, entries, slots, inserted, conflicts, tabu_list, count = len(subjects))

		return entries, (inserted, conflicts)
	cdef tuple _permute_solution(self, entries, subject, conflict, slots, tabu_list, count):

		# Remove previous entries of the subject form the entries list
		for (day, time) in entries.keys():
			if entries[day, time] == subject:

				# Mark the item as tabu to prevent its usage
				value = entries[day, time]
				tabu_list[value, day, time] = count

				del entries[day, time]

		# Attempt to insert both elements in the reverse order
		inserted, conflicts = set(), set()
		self._insert_subject(conflict, entries, slots, inserted, conflicts, tabu_list, count)
		self._insert_subject(subject, entries, slots, inserted, conflicts, tabu_list, count)

		return entries, (inserted, conflicts)
	cdef object _insert_subject(self, subject, entries, slots, inserted, conflicts, tabu_list, count):

		# Calculate a random seed - this will be used to check if a slot is candidate for insertion
		seed = random.uniform(0.0, 1.0)
		for (day, time) in slots:

			# We set these by means of a random seed and its non-existence in the tabu list
			key = (subject, day, time)
			if key not in tabu_list and self[key] >= seed:

				if (day, time) not in entries:

					# Update the tabu list so it excludes the current item
					tabu_list[key] = count
					inserted.add(subject)

					# Mo-Th / Tu-Fr are days which tend to go in pairs
					if 0 <= day <= 1:

						entries[day, time] = subject
						entries[day + 3, time] = subject
					elif 3 <= day <= 4:

						entries[day - 3, time] = subject
						entries[day, time] = subject

					# We tends to stack, yet we're not stacking as of this version
					else: entries[day, time] = subject

					break
			# If the item was not inserted there was a conflict, so we add it to the conflicts set
		else:
			conflicts.add(subject)

		# Decrement all entries from the tabu list
		for key in tabu_list.iterkeys(): tabu_list[key] = min(tabu_list[key] - 1, 0)

	def __getitem__(self, tuple key):

		cdef int subject, day, time
		subject, day, time = key

		return self._entries[subject][day][time]
