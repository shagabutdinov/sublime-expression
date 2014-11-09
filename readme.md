# Expression

This is really glorious plugin that provides api used by many other plugins of
sublime-enhanced as well as great amount of navigation keyboard shortcuts.


### Demo

![Demo](https://github.com/shagabutdinov/sublime-enhanced-demos/raw/master/expression.gif "Demo")


### Installation

This plugin is part of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
plugin set. You can install sublime-enhanced and this plugin will be installed
automatically.

If you would like to install this package separately check "Installing packages
separately" section of [sublime-enhanced](http://github.com/shagabutdinov/sublime-enhanced)
package.


### Usage

Hit keyboard shortcut to navigate in opened file according to table below.


### Commands

| Description                                     | Keyboard shortcuts
|-------------------------------------------------|---------------------------|
| Goto block up                                   | ctrl+i                    |
| Goto block down                                 | ctrl+k                    |
| Select block up                                 | ctrl+shift+i              |
| Select block down                               | ctrl+shift+k              |
| Goto end of next brackets                       | ctrl+alt+\                |
| Goto in brackets forward                        | alt+enter                 |
| Goto out of brackets or string forward          | alt+shift+enter           |
| Goto over next brackets forward                 | ctrl+shift+enter          |
| Goto in brackets backward                       | alt+ctrl+backspace        |
| Goto out of brackets or string backward         | alt+shift+backspace       |
| Goto over brackets backward                     | alt+ctrl+shift+backspace  |
| Goto matched bracket or quote                   | ctrl+alt+enter            |
| Select in brackets or string                    | alt+ctrl+shift+enter      |
| Select in brackets or string including wrapping | alt+ctrl+shift+\          |
| Delete in brackets or string                    | ctrl+alt+shift+/          |
| Select to bracket or quote forward              | alt+shift+\               |
| Select to bracket or quote backward             | ctrl+shift+\              |
| Delete brackets or string backward              | alt+backspace             |
| Delete brackets or string forward               | ctrl+alt+/                |
| Goto over brackets or string forward            | alt+ctrl+l                |
| Select brackets or string forward               | alt+ctrl+shift+l          |
| Goto over brackets or string backward           | ctrl+alt+j                |
| Select brackets or string backward              | ctrl+alt+shift+j          |
| Clean brackets or quotes forward                | ctrl+/                    |
| Clean brackets or quotes backward               | ctrl+backspace            |
| Goto search result forward                      | alt+enter                 |
| Goto search result backward                     | alt+shift+enter           |


### API

Guys, API of this plugin is a bit bloated; sorry for that.


##### find_matches(view, cursor, expression, options = {})

Description:

  Find all matches of expression in view according from the cursor and filter it
  according to options.

Arguments:

  - view - view where to look for brackets

  - cursor - int; point inside view from which expression should be matched

  - expression - string; regexp to match

  - options:

    "backward" - bool; whether to find matches backward or forward from cursor;
    note that matches will be sorted from closest to most far match.

    "range" - [int, int]; range in view where to look for matches; put a huge
    attention that view.substr(sublime.Region(*options['range'])) will be called
    and to find resulting match position you explicitly need to add
    options['range'][0] manually to match.start(group) or match.end(group)

    "nesting" - how to treat brackets; True - allow matching in brackets; False
    or "start" - disallow matching in brackets for match.start(0); "end" -
    disallow matching in brackets for match.end(0); int - disallow matching in
    brackets for match.start(int); array of int's - disallow matching in
    brackets for each element of array

    "in_current_nesting" - bool; look only into the current brackets

    "string" - same that "nesting" option do but for string (don't allow
    specified regexp group to hit string)

    "comment" - same that "nesting" option do but for comment (don't allow
    specified regexp group to hit comment)

    "scope" - regexp; scope of groups, specified in "scope_groups" should match
    this regexp; this is useful when you need to match only operators or keyword
    or another specific scope; if you need to ignore some scope you can specify
    negative lookahead (e.g. (?!.*operator) - do not match "operator" scope)

    "scope_groups" - same that "nesting" but for "scope" option (scope of
    specified regexp groups should match "scope" option)

    "cursor" - same that "nesting" but for cursor point (don't allow
    specified regexp group to be out of cursor according to "backward" option)

    "limit" - how many matches you need

Result:

  List of matches.

Comment:

  I have find out that regexps is very fast but filtering is very slow and lugs
  can be noticeable and be really annoying on large files (2k+ lines) even for
  simple regexps that hit a lot of matches. So specify 'range' and 'limit'
  where it is possible to reduce execution time.

  Probably I'll rewrite this part or whole library in order to minimize
  execution time and clean out interface of library.

Example:

  ```
  from Expression import expression

  class MyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
      # find three last r'("|\')(\s*)(+)' before cursor where (\s*)(+) is not
      # string and (+) is operator

      options = {
        'nesting': False,
        'scope': r'operator',
        'scope_groups': [2],
        'string': [2, 3],
        'limit': 3,
        'backward': True
      }

      print(expression.find_matches(self.view, self.view.sel()[0].b,
        r'("|\')(\s*)(+)', options))
  ```

##### find_match(view, cursor, expression, options = {})

Description:

  Like find_matches but returns one match or None if no matches found. Just a
  helper.


##### get_nesting(view, cursor, search_range = None, options = {}, expression = r'[({\[]')

Description:

  Get position inside of brackets that surrounds cursor. Note that it will
  return position **inside** of brackets, e.g. for "(value)" position of "v"
  and ")" will be returned.

Arguments:

  - view - view where to look for brackets

  - cursor - int, point inside view where to look for brackets

  - search_range - int or array([int, int]) for how many symbols should be
    analyzed; if array passed, first element will be for backward count,
    second - for forward count of bytes to be analyzed

  - options - dict with options (see above for options description)

  - expression - regexp to find first bracket

Result:

  Array with 2 integers or None if nothing was found.

Example:

  ```
  from Expression import expression

  class MyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
      cursor = self.view.sel()[0].b
      print(expression.get_nesting(self.view, cursor, 1024, {}, r'\('))
  ```

There is a bit more methods but probably I'll add them to "deprecated" as there
is no need of them


### Dependencies

None