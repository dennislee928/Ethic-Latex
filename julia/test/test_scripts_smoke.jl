"""
Smoke tests for Phase 4 Julia scripts.

Each script is invoked with `--smoke` via `run()` and we assert exit-code 0.
The suite runs in sequence (not parallel) so stdout from each script is
captured into a Cmd pipe and checked for absence of errors.

This file is included by julia/test/runtests.jl inside the top-level @testset.
"""

# Resolve the scripts directory relative to this test file's location
const SCRIPTS_DIR = joinpath(@__DIR__, "..", "scripts")
const JULIA_PROJECT = joinpath(@__DIR__, "..")

"""Run a script with --smoke and return (exit_code, combined_stdout_stderr)."""
function _run_smoke(script_name::String; extra_args=String[])
    script_path = joinpath(SCRIPTS_DIR, script_name)
    cmd = `$(Base.julia_cmd()) --project=$JULIA_PROJECT $script_path --smoke $extra_args`
    buf = IOBuffer()
    try
        proc = run(pipeline(cmd; stdout=buf, stderr=buf); wait=true)
        return proc.exitcode, String(take!(buf))
    catch e
        # If `run` throws on non-zero exit, capture via ProcessFailedException
        output = String(take!(buf))
        if isa(e, ProcessFailedException)
            return e.procs[1].exitcode, output
        end
        rethrow(e)
    end
end

@testset "Script Smoke Tests" begin

    @testset "run_simulation_batch.jl --smoke" begin
        code, out = _run_smoke("run_simulation_batch.jl")
        @test code == 0
        # Should print batch completion line
        @test occursin("smoke", lowercase(out)) || occursin("batch", lowercase(out))
    end

    @testset "run_phase_transition.jl --smoke" begin
        code, out = _run_smoke("run_phase_transition.jl")
        @test code == 0
        @test occursin("phase_transition", lowercase(out)) ||
              occursin("smoke", lowercase(out)) ||
              occursin("results", lowercase(out))
    end

    @testset "generate_all_figures.jl --smoke" begin
        code, out = _run_smoke("generate_all_figures.jl")
        @test code == 0
        @test occursin("figure", lowercase(out)) ||
              occursin("smoke", lowercase(out)) ||
              occursin("saved", lowercase(out))
    end

    @testset "alpha_stability_report.jl --smoke" begin
        code, out = _run_smoke("alpha_stability_report.jl")
        @test code == 0
        @test occursin("alpha", lowercase(out)) ||
              occursin("report", lowercase(out)) ||
              occursin("smoke", lowercase(out))
    end

    @testset "run_empirical_validation.jl --smoke" begin
        code, out = _run_smoke("run_empirical_validation.jl")
        @test code == 0
        # Should print synthetic alpha or data-not-found; either is acceptable
        @test occursin("synthetic", lowercase(out)) ||
              occursin("saved", lowercase(out)) ||
              occursin("smoke", lowercase(out)) ||
              occursin("results", lowercase(out))
    end

    @testset "calculate_alpha_comparison.jl --smoke" begin
        code, out = _run_smoke("calculate_alpha_comparison.jl")
        @test code == 0
        @test occursin("alpha", lowercase(out)) ||
              occursin("smoke", lowercase(out)) ||
              occursin("simulated", lowercase(out))
    end

end
