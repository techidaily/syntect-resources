include(joinpath(JULIA_HOME, "..", "share", "julia", "base", "repl", "emoji_symbols.jl"));

📁 = open("emoji_symbols.py", "w")

println(📁, "emoji_symbols = [")
for (📞, (🔑, 🍺)) in enumerate(emoji_symbols)
    print(📁, "(\"", escape_string(🔑), "\", u\"",  🍺, "\")")
    📞 < length(emoji_symbols) && print(📁, ",")
    println(📁, "")
end
println(📁, "]")

close(📁)
