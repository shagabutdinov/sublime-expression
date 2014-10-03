import sublime
import sublime_plugin
import re

OPTIONS = {
  'end': 'end',
  'start': None,
  'tokens': True,
  'nesting': True,
  'string': True,
  'comment': True,
  'backward': False,
  'search': 'minimal'
}

STOPS = {
  ']': '[',
  ')': '(',
  '}': '{',
}

def get_nesting(view, cursor, search_range = None, options = {},
  expression = r'[({\[]'):

  start_shift, begin_options = 0, options.copy()
  begin_options.update({'backward': True, 'nesting': 'end'})

  if search_range != None:
    begin_shift = search_range
    if isinstance(begin_shift, list):
      begin_shift = begin_shift[0]

    start_shift = max(0, cursor - begin_shift)
    begin_options['range'] = [start_shift, cursor]

  begin = find_match(view, cursor, expression, begin_options)
  if begin == None:
    return None

  end_shift, end_options = 0, options.copy()
  if search_range != None:
    forward_shift = search_range
    if isinstance(forward_shift, list):
      forward_shift = forward_shift[1]

    end_options['range'] = [cursor, min(view.size(), cursor + forward_shift)]
    end_shift = cursor

  expr = None
  for key, value in STOPS.items():
    if value == begin.group(0):
      expr = re.escape(key)
      break

  if expr == None:
    raise Exception('Unknown symbol "' + begin.group(0) + '"')

  end = find_match(view, cursor, expr, end_options)
  if end == None:
    return None

  return begin.end(0) + start_shift, end.start(0) + end_shift

def lookup(view, cursor, expression, options = {}):
  shift = 0
  if 'range' in options and options['range'] != None:
    if isinstance(options['range'], int):
      count = options['range']
      options['range'] = [max(cursor - count, 0), min(cursor + count,
        view.size())]
    else:
      range = options['range']
      options['range'] = [max(cursor - range[0], 0), min(cursor + range[1],
        view.size())]
    shift = options['range'][0]

  matches, start, end = find(view, cursor, expression, options)

  if options.get('backward', False):
    start, end = end, start

  if start != None:
    start += shift

  if end != None:
    end += shift

  return matches, start, end, shift

def find(view, cursor, expression, options = {}):
  if isinstance(expression, dict):
    options = dict(list(expression.items()) + list(options.items()))
    expression = options.pop('expression')

  options = _get_options(options)
  if isinstance(expression, list):
    return _find_list(view, cursor, expression, options)

  matches = find_matches(view, cursor, expression, options)
  if len(matches) == 0:
    return [], None, None

  match = matches[0]

  start, end = get_match_start_end(match, options)
  return matches, start, end

def get_match_start_end(match, options):
  options = _get_options(options)
  start, end = match.start(0), match.end(0)

  start_groups = options.get('start', None)
  end_groups = options.get('end', 'end')

  start = _get_groups_position(match, start_groups)
  end = _get_groups_position(match, end_groups)

  return start, end

def _get_options(options):
  options = options.copy()

  if options.get('tokens', None) == False:
    if not 'string' in options:
      options['string'] = False
    if not 'nesting' in options:
      options['nesting'] = False
    if not 'comment' in options:
      options['comment'] = False

  options = dict(list(OPTIONS.items()) + list(options.items()))
  return options

def _find_list(view, cursor, expressions, options):
  result_matches, starts, ends = [], [], []
  for expression in expressions:
    new_options = {}
    if isinstance(expression, dict):
      new_options = dict(list(expression.items()))
      expression = new_options.pop('expression')

    new_options = dict(list(options.items()) + list(new_options.items()))
    matches, start, end = find(view, cursor, expression, new_options)

    if start != None and end != None:
      starts.append(start)
      ends.append(end)
      result_matches += matches

  result = _find_list_select_result(starts, options)
  if result == None:
    return matches, None, None

  return matches, result, ends[starts.index(result)]

def _find_list_select_result(results, options):
  search = options.get('search', 'minimal')
  if len(results) == 0:
    result = None
  elif search == 'first':
    result = results[0]
  elif search == 'minimal':
    result = min(results)
  elif search == 'maximal':
    result = max(results)
  else:
    raise Exception('Wrong value "' + search + '" for "search" ' +
      'option')

  return result

def find_match(view, cursor, expression, options = {}):
  options = options.copy()
  options['limit'] = 1
  matches = find_matches(view, cursor, expression, options)
  if len(matches) == 0:
    return None

  return matches[0]

def find_matches(view, cursor, expression, options = {}):
  backward = options.get('backward', False)

  if 'range' in options and options['range'] != None:
    text_range = options['range']
    text = view.substr(sublime.Region(text_range[0], text_range[1]))
    shift = text_range[0]
  else:
    text = view.substr(sublime.Region(0, view.size()))
    shift = 0

  ignored_nesting = []
  if options.get('nesting', False) is not True:
    ignored_nesting += _get_nesting_ranges(view, text, shift)
  else:
    options.pop('nesting')

  if options.get('in_current_nesting', False):
    ignored_nesting += _get_inversed_nesting_ranges_for_cursor(view, cursor,
      text, shift)

  matches = list(re.finditer(expression, text))
  if backward:
    matches = reversed(matches)

  result = []

  limit = options.get('limit', None)

  for match in matches:
    if _is_point_out_of_cursor(match, cursor, backward, shift, options):
      continue

    if _is_point_ignored(ignored_nesting, match, cursor, shift, options):
      continue

    if _is_point_invalid(view, match, shift, options):
      continue

    result.append(match)
    if limit != None and len(result) >= limit:
      return result

  return result

def _is_point_out_of_cursor(match, cursor, backward, shift, options):
  cursor_groups = options.get('cursor', None)
  point = _get_groups_position(match, cursor_groups)

  if point == None:
    return False

  point += shift

  if backward and point >= cursor:
    return True

  if not backward and point < cursor:
    return True

  return False

def _is_point_ignored(ranges, match, cursor, shift, options):
  if ranges == None:
    return False

  nesting_groups = options.get('nesting', False)
  point = _get_groups_position(match, nesting_groups)
  if point == None:
    return False

  point += shift

  for range in ranges:
    if range[0] < cursor and cursor < range[1]:
      continue

    if range[0] < point and point < range[1]:
      return True

  return False

def _get_nesting_ranges(view, text, shift):
  stops_opens = STOPS.values()
  stops_closes = STOPS.keys()

  stack = []
  ranges = []
  result = []

  for match in re.finditer(r'[\(\)\{\}\[\]]', text):
    char = match.group(0)
    point = match.start(0)

    if _is_point_invalid(view, match, shift):
      continue

    if char in stops_opens:
      stack.append(char)
      ranges.append(point)
    elif char in stops_closes:
      while True:
        if len(stack) == 0:
          break

        start = ranges.pop()
        start_char = stack.pop()
        if start_char == STOPS[char]:
          end = point + 1
          result.append([start + shift, end + shift])
          break
    else:
      raise Exception('Unknown char "' + char + '"')

  return result

def _get_inversed_nesting_ranges_for_cursor(view, cursor, text, shift):
  nesting_ranges = _get_nesting_ranges(view, text, shift)
  result = []
  min_range_length = None
  for range in nesting_ranges:
    if range[0] < cursor and cursor < range[1]:
      range_length = range[1] - range[0]
      if min_range_length == None or min_range_length > range_length:
        min_range_length = range_length
        result = [[0, range[0]], [range[1], view.size()]]

  return result

def _is_point_invalid(view, match, shift, options = {}):
  if _is_point_invalid_by_key(view, match, shift, options, 'string', 'symbol'):
    return True

  if _is_point_invalid_by_key(view, match, shift, options, 'comment'):
    return True

  if _is_point_invalid_by_scope(view, match, shift, options):
    return True

  return False

def _is_point_invalid_by_key(view, match, shift, options, key, key2 = None):
  groups = options.get(key, None)
  if groups is True:
    return False

  point = _get_groups_position(match, groups)

  if point == None:
    return False

  if key in view.scope_name(point + shift):
    return True

  if key2 != None and key2 in view.scope_name(point + shift):
    return True

  return False

def _is_point_invalid_by_scope(view, match, shift, options):
  if 'scope' not in options:
    return False

  point, groups = None, options.get('scope_groups', None)
  if groups is True:
    return False

  point = _get_groups_position(match, groups)

  if point == None:
    return False

  return re.search(options['scope'], view.scope_name(point + shift)) == None

def _get_groups_position(match, groups):
  if groups == None or groups == False or groups == 'start':
    return match.start(0)

  return_non_empty, return_end = False, False
  if isinstance(groups, dict):
    groups = groups['groups']
    return_end = groups['end']
    return_non_empty = groups['non_empty']

  if isinstance(groups, list):
    for index in groups:
      if return_end:
        result = match.end(index)
      else:
        result = match.start(index)

      if result < 0:
        continue

      if return_non_empty and match.group(index) == '':
        continue

      return result
  elif groups == 'end':
    return match.end(0)
  elif groups == 'first_non_empty' or groups == 'last_non_empty':
    iterable = match.groups()
    if groups == 'last_non_empty':
      iterable = reversed(iterable)

    for index, group in enumerate(iterable):
      if group != '':
        if return_end:
          return match.end(index)
        else:
          return match.start(index)
    return None
  else:
    raise Exception('Unknown groups "' + str(groups) + '"')