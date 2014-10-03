import sublime
import sublime_plugin
from Expression import expression

class NestingResponder(sublime_plugin.EventListener):
  def on_query_context(self, view, key, operator, operand, match_all):
    if key != 'in_nesting':
      return None

    result = True
    for sel in view.sel():
      in_nesting = expression.find_match(view, sel.b, r'[\)\}\]]',
        {'range': [sel.b, min(sel.b + 1024 * 5, view.size())]}) != None

      if operator == sublime.OP_EQUAL:
        result = result and in_nesting == operand
      elif operator == sublime.OP_NOT_EQUAL:
        result = result and in_nesting != operand
      else:
        raise Exception('Operator "' + operator + '" is not supported')

      if not match_all:
        return result

    return result

class HighlightsCleaner(sublime_plugin.EventListener):
  def on_selection_modified_async(self, view):
    last_command, _, _ = view.command_history(0)
    if last_command == 'goto_expression':
      return

    view.erase_regions('expression')