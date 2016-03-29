# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.template import Library, Node

register = Library()

class AngularNode(Node):
	""" Adapted from <"https://djangosnippets.org/snippets/2787/"> """

	def __init__(self, contents):
		self._contents = contents

	def render(self, context):
		return '{{ %s }}' % ' '.join(self._contents[1:])

@register.tag(name = 'angular')
def angular_tag(parser, token):

	contents = token.split_contents()
	return AngularNode(contents)
