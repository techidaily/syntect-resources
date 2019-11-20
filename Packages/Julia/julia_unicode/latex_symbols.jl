include(joinpath(JULIA_HOME, "..", "share", "julia", "base", "repl", "latex_symbols.jl"));

φ = open("latex_symbols.py", "w")

println(φ, "latex_symbols = [")
for (ω, (α, β)) in enumerate(latex_symbols)
    print(φ, "(\"", escape_string(α), "\", u\"",  β, "\")")
    ω < length(latex_symbols) && print(φ, ",")
    println(φ, "")
end
println(φ, "]")

close(φ)
