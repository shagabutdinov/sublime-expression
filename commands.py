import sublime
import sublime_plugin

from Expression.expression import lookup, get_match_start_end

class GotoExpression(sublime_plugin.TextCommand):
  def run(self, edit, expression, options = {}, expand = False, delete = False,
    append = False, range = None, highligh = False):

    selections = []
    highlighs = []
    if delete:
      expand = True

    if not highligh:
      options['limit'] = 1
    elif isinstance(highligh, int):
      options['limit'] = highligh
    else:
      options['limit'] = 10

    size = len(self.view.sel())
    index = 0
    while index < size:
      sel = self.view.sel()[index]
      index += 1

      region, highligh_ranges = self._get_region(sel, expression, options,
        expand, append, range, highligh)

      highlighs += highligh_ranges

      if delete:
        self.view.replace(edit, region, '')
      else:
        selections.append(region)

    if not delete:
      self.view.sel().clear()
      self.view.sel().add_all(selections)

    if len(selections) > 0:
      self.view.show(selections[0].b)

    if highligh:
      self.view.erase_regions('expression')
      draw = sublime.DRAW_EMPTY | sublime.DRAW_OUTLINED
      self.view.add_regions('expression', highlighs, 'string', '', draw)

  def _get_region(self, sel, expression, options, expand, append, range,
    highligh):

    cursor = sel.b

    matches, start, end, shift = lookup(self.view, cursor, expression, options)
    if start == None or end == None:
      return sublime.Region(sel.a, sel.b), []

    if highligh == True:
      highligh = 10
    elif not isinstance(highligh, int):
      highligh = None

    highlighs = []
    if highligh != None:
      for index, match in enumerate(matches):
        if index == 0:
          continue
        if index > 10:
          break

        highligh_start, highligh_end = get_match_start_end(match, options)
        highligh = sublime.Region(highligh_start + shift, highligh_end + shift)
        highlighs.append(highligh)

    if options.get('backward', False):
      start, end = end, start

    if expand:
      result = sublime.Region(sel.a, start)
    elif append:
      result = sublime.Region(start, end)
    else:
      result = sublime.Region(start, start)

    return result, highlighs