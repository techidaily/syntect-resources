Changelog
=========

3.0.0 (ST3 only)
----------------

Support for fish 3.0:
- A literal `{}` now "expands" to itself, rather than undergoing brace expansion to an empty string
- Brace expansion may contain unescaped whitespace, including newlines
- Commands may be linked by `&&` and `||` to form conditional pipelines
- `!` may be used as a synonymous command for `not`
- Command names may contain variable expansion
- `&&`, `||`, and `|` may be used for line continuation (to continue a pipeline to the next line)

New features:
- Compatibility highlighter - Outline structures in fish scripts that are incompatible with the targeted version:
  - Complements the normal syntax highlighting to spot subtle mistakes
  - The version of fish to target can be given on the first line of the file, or is otherwise taken from the settings
    - Settings can specify a particular version, or `auto` to use the version installed on the system
- Path highlighter - Underline valid file paths in fish scripts:
  - Imitates native fish behaviour for underlining valid paths
  - Compatible with all platforms, depending only on how Python's os.path library interprets absolute paths

Improvements:
- Use `meta.function-call.operator.redirection.`{`stdin`,`stdout`,`stderr`}`.`{`explicit`,`implicit`} for different types of redirections
- Distinguish job expansion and process expansion

Settings changes:
- `fish_indent_directory` renamed to `fish_directory`
- `blacklist` renamed to `indent_on_save_blacklist`

Bugfixes:
- Inline comments after `switch var` and `while cmd` statements were not scoped correctly
- Some scope names were not applied entirely consistently, or named consistently

2.5.0 (ST2 and ST3)
-------------------

This is the first version of the package to support ST2 and ST3 from separate development branches. Meaning, it exists in two different forms which each implement all the following changes.

Packaging:
- Rename syntax to "Friendly Interactive Shell (fish)", as the de facto standard for syntax names is title cased
- Rename package settings menu item to "Fish", as the de facto standard for this menu is the title-cased package name

Improvements:
- Use `meta.function-call.name` for command names
- Use `meta.function-call.parameter` for all parameters
- Use `meta.function-call.operator.control` for control operators specifically
- Use `meta.function-call.operator.redirection` for redirection
- Use `meta.function-call.operator.pipe` for piping

Bugfixes:
- Comments immediately after builtin commands were not scoped correctly
- Comments immediately after redirection into file were not shown as invalid

2.4.1
-----

Bugfixes:
- Redirection with two arrows `>>` did not highlight correctly at all (!)
- The caret redirection operator `^` was still given special treatment inside of some words
- Redirection didn't identify certain invalid characters in paths
- `and`/`or` weren't shown as invalid when they were used directly after a pipe
- Redirection wasn't shown as invalid when it was used directly after a pipe
- Backgrounding of `and`/`or`/`not` wasn't shown as invalid
- Defining a function starting with `~` highlighted it as a special character
- Invalid structures in the `function` block were not identified

2.4.0
-----

Improvements:
- Support the `[ ]` form of `test` (#8)
- Highlight a `~` in redirect paths
- Distinguish arguments which might be paths with `meta.parameter.argument.path`
- Distinguish option and argument parameter types, and long and short option types (as well as the "end of options" option).
  We now provide the following scopes:
  - `meta.parameter.option.long`
  - `meta.parameter.option.short`
  - `meta.parameter.option.end`
  - `meta.parameter.argument`
  - `punctuation.definition.option.long.begin`
  - `punctuation.definition.option.long.separator`
  - `punctuation.definition.option.short`
  - `punctuation.definition.option.end`
- Distinguish operator types.
  We now provide the following scopes:
  - `keyword.operator.control`
  - `keyword.operator.pipe`
  - `keyword.operator.redirect`
  - `keyword.operator.range`

Bugfixes:
- Some structures were not highlighted correctly if they were immediately followed by the EOF
- Unescaped spaces in brace expansion weren't marked up as invalid
- Quoted integers were not allowed as file descriptors in redirection

Internal changes:
- Rename "argument" to "parameter"
- Rename "nonoption argument" to "argument"
- Rename "command chain" to "pipeline"

2.3.0
-----

New feature:
- Automatic indentation and prettification of fish files (#16):
  - Utilises the `fish_indent` program that comes with fish
  - Compatible with Sublime Text 2 and 3 on all platforms
    - No additional configuration is necessary for standard fish installs
  - Indentation respects user preferences of tab size
  - Indentation is restricted to highlighted regions if any are present, otherwise the full file is acted on
  - Default shortcut for indentation is `ctrl+alt+i`
  - Build system execution is also available
  - Optionally, turn on automatic indentation at every save in settings

Bugfixes:
- A block would not scope correctly if an `&` appeared immediately before the `end` command
- Redirected piping would not scope correctly under `builtin`, `command`, or `exec`
- Escaping a newline could extend the scope one line too far

2.2.6
-----

Bugfixes:
- ST2 would freeze encountering consecutive command substitutions (#14)
- ST2 would freeze encountering consecutive variable expansions (#14)
- `end` at end of file wasn't highlighted correctly (#15)

2.2.5
-----

Bugfixes:
- ST2 would freeze encountering an escaped newline (#14)
- ST2 would freeze encountering a pipe (#14)
- `not` wasn't recognised in a command chain

2.2.4
-----

Bugfix:
- Control characters appearing in brace expansion would freeze ST2 (#14)

2.2.3
-----

Bugfix:
- Menu options could not open the README or CHANGELOG files

2.2.2
-----

Bugfix:
- Snippets did not use tabs for indenting (#12)

2.2.1
-----

Bugfix:
- An argument consisting of a lone `-` was scoped as an option

2.2.0
-----

Improvement:
- Make numeric scoping more consistent, and now recognise numbers starting with a plus or minus sign.
  After the end of options argument `--`, an argument like `-5` will be scoped as numeric rather than as an option. Additionally, recognition of sign is important for when numbers are used in index expansion

Bugfix:
- Redirected process expansion failed to recognise special names like "self"

2.1.2
-----

Bugfixes:
- A command call line ending with `=` did not terminate (#11)
- An `=` could not safely be a command name

2.1.1
-----

Bugfix:
- A lone `.` was scoped as a decimal point for a numeric (#10)

2.1.0
-----

New features:
- Support for short (`-x`) and long (`--x=arg`) option arguments using the `variable.parameter` scope (#5)
- Recognise `--` as the end of options and treat further arguments as normal, even if they start with a dash

2.0.1
-----

Bugfixes:
- Comment lines could incorrectly appear after certain line continuations
- stderr redirection into pipe (`^|` and `^^|`) was not recognised
