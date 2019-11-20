# SYNTAX TEST "AWK.sublime-syntax"
# <- punctuation.definition.comment.awk
# <- comment.line.number-sign.awk
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ comment.line.number-sign.awk
function f(x,y){
# <-             storage.type.function.awk
#        ^       entity.name.function.awk
#         ^      punctuation.definition.parameters.begin.awk
#          ^     variable.parameter.function.awk
#            ^   variable.parameter.function.awk
#             ^  punctuation.definition.parameters.end.awk
}

/^ab$/ {
# <-   punctuation.definition.regex.begin.awk
#^^^^  string.regexp
#    ^ punctuation.definition.regex.end.awk
}

BEGIN {
# <- constant.language.awk

    var = 1/4
#       ^      keyword.operator.assignment.awk
#         ^    constant.numeric.awk
#          ^   keyword.operator.arithmetic.awk
#           ^  constant.numeric.awk

    var = /1\/4/
#       ^        keyword.operator.assignment.awk
#         ^      punctuation.definition.regex.begin.awk
#          ^^^^  string.regexp
#              ^ punctuation.definition.regex.end.awk

    var = f(1/4,/1\/4/,1/4,/1\/4/)
#       ^ keyword.operator.assignment.awk
#           ^    constant.numeric.awk
#            ^   keyword.operator.arithmetic.awk
#             ^  constant.numeric.awk
#              ^        punctuation.separator.parameters.awk
#               ^       punctuation.definition.regex.begin.awk
#                ^^^^   string.regexp
#                    ^  punctuation.definition.regex.end.awk
#                     ^     punctuation.separator.parameters.awk
#                      ^    constant.numeric.awk
#                       ^   keyword.operator.arithmetic.awk
#                        ^  constant.numeric.awk
#                         ^       punctuation.separator.parameters.awk
#                          ^      punctuation.definition.regex.begin.awk
#                           ^^^^  string.regexp
#                               ^ punctuation.definition.regex.end.awk
    var = 1 / 4 + 1 / 4
#         ^             constant.numeric.awk
#           ^           keyword.operator.arithmetic.awk
#             ^         constant.numeric.awk
#               ^       keyword.operator.arithmetic.awk
#                 ^     constant.numeric.awk
#                   ^   keyword.operator.arithmetic.awk
#                     ^ constant.numeric.awk
}
# <- meta.brace.curly.awk

BEGIN {
  if (/\{\}/) {
# ^^ keyword.control.awk
#     ^ punctuation.definition.regex.begin.awk
#          ^ punctuation.definition.regex.end.awk
  } else {
#   ^^^^ keyword.control.awk
  }

}