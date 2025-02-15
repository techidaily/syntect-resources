import os.path
import logging
import re
import subprocess
import sublime, sublime_plugin

from fish.highlighter_base import BaseHighlighter
from fish.Tools.misc import getFishOutput

import yaml # external dependency pyyaml (see dependencies.json)


# Convert version strings to three fields, padding with zeroes if needed
def semver_conv(strA, strB):
  lA = [int(i) for i in strA.split(sep = '.')]
  lB = [int(i) for i in strB.split(sep = '.')]
  if max(len(lA), len(lB)) > 3:
    raise ValueError("semver should have 3 elements at most")

  if len(lA) < 3:
    lA.extend( [0]*(3 - len(lA)) )
  if len(lB) < 3:
    lB.extend( [0]*(3 - len(lB)) )

  return lA,lB


# Test if semver A is strictly less than semver B
def semver_lt(strA, strB):
  lA,lB = semver_conv(strA, strB)
  return lA[0] < lB[0] \
    or (lA[0] == lB[0] and lA[1] < lB[1]) \
    or (lA[0] == lB[0] and lA[1] == lB[1] and lA[2] < lB[2])


class CompatHighlighter(sublime_plugin.ViewEventListener, BaseHighlighter):
  # Database shared by all instances of the class
  database = None

  # System fish version
  sysFishVer = None

  def __init__(self, view):
    sublime_plugin.ViewEventListener.__init__(self, view)
    BaseHighlighter.__init__(self, view)

    # Only first instance will load database
    if CompatHighlighter.database is None:
      # We can't do this in the static class variable declaration because API not loaded yet
      CompatHighlighter.database = yaml.load(
        sublime.load_resource('Packages/fish/highlighter_compat_rules.yaml'),
        Loader = yaml.BaseLoader,
      )

    # Only first instance will set this
    if CompatHighlighter.sysFishVer is None:
      out,err = getFishOutput(['fish', '--version'], self.view.settings())
      match = None
      if out:
        # For builds from source, version string may be e.g. "fish, version 3.0.2-1588-g70fc2611"
        # Hence, we just search() for the match anywhere in the string
        match = re.search(r'[0-9]+\.[0-9]+\.[0-9]+', out.strip())
      else:
        CompatHighlighter.sysFishVer = 'not found' # Couldn't find executable

      if err:
        sublime.error_message(err)

      if match:
        CompatHighlighter.sysFishVer = match.group(0)
      elif out:
        CompatHighlighter.sysFishVer = 'error' # This shouldn't happen!

    # Fish version from file settings, which may be sysFishVer if that's "auto"
    self.settingsFishVer = None
    self._cache_settings_fish_version()

    # Set up a callback to update our cached value if file settings are changed.
    # However, the existence of the callback will prevent this instance being
    #   deleted by the garbage collector after a plugin reload, and we must
    #   first clear any existing callback to ensure that a *previous* instance
    #   gets properly destroyed. That destruction is vital to the previously
    #   drawn regions being cleared before their keys are lost
    self.view.settings().clear_on_change(__name__)
    self.view.settings().add_on_change(__name__, self._cache_settings_fish_version)

    # Fish version explicitly set at the top of the open file with "fishX[.Y[.Z]]"
    self.localFishVer = None
    self._cache_local_fish_version()

    # Mapping of regions to the appropriate history state
    self.regionStates = dict()

    # Override default properties of the template
    self.selectors = []
    for issue in CompatHighlighter.database['issues'].values():
      if isinstance(issue['selector'], list):
        self.selectors.extend(issue['selector'])
      else:
        self.selectors.append(issue['selector'])

  # def __del__(self):
  #   BaseHighlighter.__del__(self)

  @classmethod
  def is_applicable(self, settings):
    try:
      return 'Packages/fish/fish' in settings.get('syntax') and 'compatibility' in settings.get('enabled_highlighters')
    except TypeError: # In weird cases get() comes back NoneType
      return False

  @classmethod
  def applies_to_primary_view_only(self):
    return False

  # Using _async functions means regions may flash onscreen as they are changed,
  #   however the advantage is that input is not blocked. In very big files
  #   this is essential

  # Review full file at load
  def on_load_async(self):
    self.logger.debug("on_load")
    self._cache_local_fish_version()
    self._update_markup()

  # Review full file at save
  def on_post_save_async(self):
    self.logger.debug("on_post_save")
    self._cache_local_fish_version()
    self._update_markup()

  # Review current line after each modification
  # We still iterate over every currently drawn region to test if it should be
  #   erased, however we only test new regions that are on the current line
  def on_modified_async(self):
    self.logger.debug("on_modified")
    self._update_markup(local = True)

  def on_hover(self, point, hover_zone):
    # Ignore any hover that's not over text
    if hover_zone != sublime.HOVER_TEXT:
      return

    self.logger.debug("on_hover")

    for key,value in self.drawnRegions.items():
      region,issueID = value
      # Find the region which overlaps with the mouse hover location
      if not region.contains(point):
        continue

      issue = CompatHighlighter.database['issues'][issueID]
      state = self.regionStates[key]

      try:
        problem = CompatHighlighter.database['changes'][ state['change'] ].format(state['version'])
      except KeyError:
        self.logger.error("Unknown change {} from issue {}".format(state['change'], issueID))
        continue

      # In most cases, align popup to the first character of the region.
      # However if the region is on a newline, popup must be one character back or it will draw on the wrong line
      location = region.begin() + 1
      regChar = self.view.substr( region.begin() )
      if regChar == '\n':
        location -= 1

      self.view.show_popup(
        """
          <body id = "compatibility_highlight">
            <style>
              div.problem {{
                font-family: Sans, Helvetica, Arial, sans-serif;
                font-size: 0.9rem;
                font-style: italic;
                margin-bottom: 0.5rem;
              }}
              div.hint {{
                font-family: Sans, Helvetica, Arial, sans-serif;
              }}
              p {{
                margin: 0rem;
              }}
              code {{
                background-color: color(var(--background) blend(var(--foreground) 80%));
                padding-right: 0.2rem;
                padding-left: 0.2rem;
              }}
            </style>
            <div class = "problem">
              <p>{}</p>
              <p>(You are using fish {})</p>
            </div>
            <div class = "hint"> {} </div>
          </body>
        """.format(problem, self._fish_version(), issue['hint']),
        flags = sublime.HIDE_ON_MOUSE_MOVE_AWAY,
        location = location,
      )
      break

  def on_text_command(self, command_name, args):
    if command_name == 'run_highlighter_test_trigger' and self._is_highlighter_test():
      self._run_test()

  def _should_markup(self):
    if self._fish_version() is None:
      self.logger.info("Refusing to mark up because targeted fish version unknown")
      return False
    else:
      return True

  def _test_draw_region(self, region, selector, regionID):
    text = self.view.substr(region)
    self.logger.debug("Region {} text = {}".format(region, text))

    # re._MAXCACHE = 512 in builtin Python as of ST 3.2.1, so we needn't cache regexes ourselves

    found = False
    for issueID,issue in CompatHighlighter.database['issues'].items():
      if (
        (isinstance(issue['selector'], list) and selector in issue['selector'])
        or
        (not isinstance(issue['selector'], list) and selector == issue['selector'])
      ) and (
        issue['match'] == 'true'
        or
        # https://stackoverflow.com/a/30212799
        # Effectively backport re.fullmatch() to Python 3.3 by adding end-of-string anchor
        re.match('(?:' + issue['match'] + r')\Z', text)
      ):
        found = True
        self.logger.debug("Found as issueID {}".format(issueID))
        break
    if not found:
      return None

    # Check each state against targeted version
    state = None
    for testState in CompatHighlighter.database['issues'][issueID]['history']:
      c = testState['change']
      v = testState['version']
      if (
        # If the target version is less than this state then draw
        (c == 'added' or c == 'behaviour')
        and
        semver_lt(self._fish_version(), v)
      ) or (
        # If the target version is greater than or equal to this state then draw
        (c == 'deprecated' or c == 'removed')
        and
        not semver_lt(self._fish_version(), v)
      ):
        state = testState
        self.logger.debug("Version match to state {}".format(state))

    if not state:
      return None

    drawScope = 'source.shell.fish '
    changeType = None

    if state['change'] == 'added' or state['change'] == 'removed':
      drawScope += 'invalid.illegal.compatibility.error.fish'
      changeType = 'error'
    elif state['change'] == 'behaviour':
      # Technically the structure isn't illegal...it just won't work how the syntax shows.
      # All we want to do is warn the user. A different scope may be more appropriate
      drawScope += 'invalid.illegal.compatibility.warning.fish'
      changeType = 'behaviour'
    elif state['change'] == 'deprecated':
      # invalid.deprecated seems to be reliably defined, if rarely used
      drawScope += 'invalid.deprecated.compatibility.fish'
      changeType = 'deprecated'
    else:
      self.logger.error("Unknown change {} in issue {}".format(state['change'], issueID))
      return None

    # Skip any change types that aren't enabled, unless this is a highlighter test
    if not self._is_highlighter_test() and changeType not in self.view.settings().get('compat_highlighter_types'):
      self.logger.info("Skipping issue with change of disabled type: {}".format(changeType))
      return None

    drawStyle = sublime.DRAW_NO_FILL

    self.regionStates[regionID] = state
    return (issueID, drawScope, drawStyle)

  def _is_highlighter_test(self):
    return self.view.find(r'^#! HIGHLIGHTER TEST COMPATIBILITY', 0).begin() == 0

  # Return the targeted fish version of this file
  # We want this method to be very efficient, hence all the caching of the variables
  def _fish_version(self):
    if self.localFishVer:
      return self.localFishVer
    else:
      return self.settingsFishVer

  def _cache_settings_fish_version(self):
    versionStr = self.view.settings().get('compat_highlighter_fish_version', '')
    if versionStr == 'auto':
      if CompatHighlighter.sysFishVer == 'not found':
        self.settingsFishVer = None
        self.logger.error("fish not found! Version couldn't be determined automatically")
      elif CompatHighlighter.sysFishVer == 'error':
        self.settingsFishVer = None
        # Currently, I can't imagine this happening. Prove me wrong!
        sublime.error_message("Error in fish.sublime-settings: " \
          "The 'auto' setting was unable to determine your fish version. " \
          "Please report a bug using Preferences > Package Settings > Fish " \
          "> Report a bug. Include your system information, and the output " \
          "of 'fish --version' in your terminal. To work around this error, " \
          "set your fish version manually in the settings file."
        )
      else:
        self.settingsFishVer = CompatHighlighter.sysFishVer
        self.logger.info("Settings fish version is {} (system)".format(self.settingsFishVer))
    elif versionStr and re.match(r'[0-9]+\.[0-9]+\.[0-9]+\Z', versionStr):
      self.settingsFishVer = versionStr
      self.logger.info("Settings fish version is {}".format(self.settingsFishVer))
    else:
      sublime.error_message("Error in fish.sublime-settings: Invalid value '{}' for compat_highlighter_fish_version.".format(versionStr))
      self.settingsFishVer = None

  def _cache_local_fish_version(self):
    firstLine = self.view.substr(self.view.line( sublime.Region(0,0) ))
    match = re.search(
      r'fish([0-9]+(?:\.[0-9]+(?:\.[0-9]+)?)?)',
      firstLine,
    )
    if match:
      self.localFishVer = match.group(1)
      self.logger.info("Local fish version is {}".format(self.localFishVer))
    else:
      self.localFishVer = None
