"""
    FluidModel — Continuous fluid/field model for error-density evolution.

    Mirrors erh_core/analysis/fluid_model.py.

    PDE:  ∂u/∂t + ∂(v·u)/∂x = D·∂²u/∂x² − α·u + S(x,t)

    where:
    - u(x,t) : error density at complexity x, time t
    - v       : convection velocity (error growth trend)
    - D       : diffusion coefficient (error propagation)
    - α       : natural correction rate
    - S(x,t)  : source term (new error generation)

    Solved via an implicit-explicit (IMEX) finite-difference scheme:
    - Implicit: diffusion (D·∂²u/∂x²) and correction (−α·u)
    - Explicit: convection (−∂(v·u)/∂x, upwind) + source

    Uses OrdinaryDiffEq.jl for the optional `solve_ode_formulation` helper.
"""
module FluidModel

using LinearAlgebra
using Statistics
using OrdinaryDiffEq

export solve_error_density_pde, detect_critical_phenomena,
       fit_fluid_parameters, compute_steady_state,
       solve_ode_formulation

# ---------------------------------------------------------------------------
# Tridiagonal matrix helpers
# ---------------------------------------------------------------------------

"""Build the (nx × nx) diffusion-correction matrix for implicit step."""
function _build_diffusion_matrix(
    nx::Int,
    dx::Float64,
    D::Float64,
    alpha::Float64,
    boundary_conditions::String
)
    # Diagonal and off-diagonal values
    diag_val  = -2D / dx^2 - alpha
    off_val   = D / dx^2

    d  = fill(diag_val, nx)
    dl = fill(off_val, nx-1)
    du = fill(off_val, nx-1)

    # Neumann BC: zero-flux (one-sided stencil at boundaries)
    if boundary_conditions == "neumann"
        d[1]   = -D / dx^2 - alpha
        du[1]  =  D / dx^2
        d[end] = -D / dx^2 - alpha
        dl[end]=  D / dx^2
    end
    # Dirichlet BC: boundary rows replaced by identity
    # (handled in the solve loop directly)

    return Tridiagonal(dl, d, du)
end

# ---------------------------------------------------------------------------
# Main PDE solver
# ---------------------------------------------------------------------------

"""
    solve_error_density_pde(x_range, t_range; nx, nt, v, D, alpha, S,
                             initial_condition, boundary_conditions)
        → (u_xt, x_grid, t_grid)

Solve the error-density PDE with an IMEX finite-difference scheme.

Returns:
- `u_xt`   : Matrix{Float64} of size `(nt, nx)` — solution at each (t, x) point
- `x_grid` : Vector{Float64} of length `nx`
- `t_grid` : Vector{Float64} of length `nt`
"""
function solve_error_density_pde(
    x_range::Tuple{Float64,Float64},
    t_range::Tuple{Float64,Float64};
    nx::Int=100,
    nt::Int=100,
    v::Float64=0.1,
    D::Float64=0.01,
    alpha::Float64=0.05,
    S::Union{Function, Nothing}=nothing,
    initial_condition::Union{Vector{Float64}, Nothing}=nothing,
    boundary_conditions::String="neumann"
)::Tuple{Matrix{Float64}, Vector{Float64}, Vector{Float64}}

    x_min, x_max = x_range
    t_min, t_max = t_range

    x_grid = range(x_min, x_max, length=nx) |> collect
    t_grid = range(t_min, t_max, length=nt) |> collect
    dx     = (x_max - x_min) / (nx - 1)
    dt     = (t_max - t_min) / (nt - 1)

    u_xt   = zeros(Float64, nt, nx)

    # --- Initial condition ---
    if initial_condition !== nothing
        @assert length(initial_condition) == nx
        u_xt[1, :] = initial_condition
    else
        x_center = (x_min + x_max) / 2
        sigma    = (x_max - x_min) / 10
        u_xt[1, :] = exp.(-(( x_grid .- x_center).^2) ./ (2sigma^2))
    end

    # --- Source function ---
    S_fn = S === nothing ? (x, t) -> 0.0 : S

    # --- Diffusion matrix (implicit) ---
    A = _build_diffusion_matrix(nx, dx, D, alpha, boundary_conditions)
    A_mat = Matrix(A)   # convert Tridiagonal → dense for lu factorisation once

    # Crank-Nicolson-like: solve (I - dt*A) * u_{n+1} = b
    LHS   = I(nx) - dt .* A_mat

    if boundary_conditions == "dirichlet"
        LHS[1, :]   .= 0.0;  LHS[1, 1]   = 1.0
        LHS[end, :] .= 0.0;  LHS[end, end] = 1.0
    end

    LHS_lu = lu(LHS)

    # --- Time stepping ---
    for n in 1:(nt - 1)
        u_n = u_xt[n, :]
        t_n = t_grid[n]

        # Upwind convection term
        conv = zeros(Float64, nx)
        if v > 0
            for i in 2:nx
                conv[i] = -v * (u_n[i] - u_n[i-1]) / dx
            end
            conv[1] = 0.0
        else
            for i in 1:(nx-1)
                conv[i] = -v * (u_n[i+1] - u_n[i]) / dx
            end
            conv[nx] = 0.0
        end

        # Source term
        source = Float64[S_fn(x_grid[i], t_n) for i in 1:nx]

        # RHS
        b = u_n .+ dt .* (conv .+ source)

        if boundary_conditions == "dirichlet"
            b[1]   = 0.0
            b[end] = 0.0
        end

        u_xt[n+1, :] = LHS_lu \ b
    end

    return u_xt, x_grid, t_grid
end

# ---------------------------------------------------------------------------
# ODE formulation (using OrdinaryDiffEq.jl)
# ---------------------------------------------------------------------------

"""
    solve_ode_formulation(x_range, t_span; nx, v, D, alpha, S,
                           initial_condition, solver, kwargs...)
        → (u_xt, x_grid, t_vals)

Alternative solver: discretise in space, then hand the resulting ODE system
to OrdinaryDiffEq.  Useful for stiff problems or adaptive time-stepping.
"""
function solve_ode_formulation(
    x_range::Tuple{Float64,Float64},
    t_span::Tuple{Float64,Float64};
    nx::Int=50,
    v::Float64=0.1,
    D::Float64=0.01,
    alpha::Float64=0.05,
    S::Union{Function, Nothing}=nothing,
    initial_condition::Union{Vector{Float64}, Nothing}=nothing,
    solver=Tsit5(),
    saveat_pts::Int=50,
    kwargs...
)
    x_min, x_max = x_range
    x_grid = range(x_min, x_max, length=nx) |> collect
    dx     = (x_max - x_min) / (nx - 1)
    S_fn   = S === nothing ? (x, t) -> 0.0 : S

    u0 = if initial_condition !== nothing
        initial_condition
    else
        x_center = (x_min + x_max) / 2
        sigma    = (x_max - x_min) / 10
        exp.(-(( x_grid .- x_center).^2) ./ (2sigma^2))
    end

    function pde_rhs!(du, u, p, t)
        dx, v, D, alpha = p
        # Interior
        for i in 2:(nx-1)
            conv = v > 0 ?
                   -v * (u[i] - u[i-1]) / dx :
                   -v * (u[i+1] - u[i]) / dx
            diff = D * (u[i+1] - 2u[i] + u[i-1]) / dx^2
            du[i] = conv + diff - alpha * u[i] + S_fn(x_grid[i], t)
        end
        # Neumann boundaries
        du[1]  = D * (u[2]  - u[1])  / dx^2 - alpha * u[1]  + S_fn(x_grid[1],  t)
        du[nx] = D * (u[nx-1]-u[nx]) / dx^2 - alpha * u[nx] + S_fn(x_grid[nx], t)
    end

    prob    = ODEProblem(pde_rhs!, u0, t_span, (dx, v, D, alpha))
    t_save  = range(t_span[1], t_span[2], length=saveat_pts)
    sol     = solve(prob, solver; saveat=t_save, kwargs...)

    t_vals  = sol.t
    u_xt    = hcat(sol.u...)'  # (nt, nx)

    return Matrix(u_xt), x_grid, t_vals
end

# ---------------------------------------------------------------------------
# Critical-phenomenon detection
# ---------------------------------------------------------------------------

"""
    detect_critical_phenomena(u_xt, x_grid, t_grid; threshold=2.0)
        → Vector{Dict{String,Any}}

Detect sudden jumps in error density exceeding `mean + threshold·std`.
Returns list of event dicts with keys: `"time"`, `"time_value"`, `"complexity"`,
`"density"`, `"density_jump"`, `"severity"`.
"""
function detect_critical_phenomena(
    u_xt::Matrix{Float64},
    x_grid::Vector{Float64},
    t_grid::Union{Vector{Float64}, AbstractRange};
    threshold::Float64=2.0
)::Vector{Dict{String,Any}}
    events = Dict{String,Any}[]
    nt, nx = size(u_xt)
    t_vec  = collect(t_grid)

    mu  = mean(u_xt)
    sig = std(u_xt)
    threshold_value = mu + threshold * sig

    for t in 2:nt, xi in 1:nx
        curr = u_xt[t,  xi]
        prev = u_xt[t-1, xi]
        if curr > threshold_value
            jump = curr - prev
            if jump > sig
                severity = jump > 3sig ? "critical" : jump > 2sig ? "high" : "medium"
                push!(events, Dict{String,Any}(
                    "time"         => t - 1,   # 0-indexed for Python parity
                    "time_value"   => t_vec[t],
                    "complexity"   => x_grid[xi],
                    "density"      => curr,
                    "density_jump" => jump,
                    "severity"     => severity
                ))
            end
        end
    end
    return events
end

# ---------------------------------------------------------------------------
# Parameter fitting from observed data
# ---------------------------------------------------------------------------

"""
    fit_fluid_parameters(E_xt, x_values, t_values) → Dict{String,Float64}

Estimate `v`, `D`, `alpha` from the observed error array `E_xt` of shape
`(time_steps, X_max)` — the same heuristic as the Python implementation.
"""
function fit_fluid_parameters(
    E_xt::Matrix{Float64},
    x_values::Vector{Float64},
    t_values::Vector{Float64}
)::Dict{String,Float64}
    abs_E      = abs.(E_xt)
    mean_errors = vec(mean(abs_E, dims=1))   # (X_max,)

    # v: slope of mean_error vs x
    v_estimate = 0.1
    if length(x_values) > 1 && std(mean_errors) > 0
        mx = mean(x_values);  mE = mean(mean_errors)
        slope = sum((x_values .- mx) .* (mean_errors .- mE)) /
                (sum((x_values .- mx).^2) + 1e-10)
        v_estimate = clamp(abs(slope), 0.01, 1.0)
    end

    # D: variance of errors across complexity
    error_variance = vec(var(abs_E, dims=1))
    D_estimate = clamp(mean(error_variance) / 10, 0.001, 0.1)

    # alpha: exponential decay rate over time
    time_decays = Float64[]
    for xi in 1:size(E_xt, 2)
        row = abs_E[:, xi]
        maximum(row) == 0 && continue
        log_row = log.(row .+ 1e-10)
        t_vals  = Float64.(0:(length(row)-1))
        mt, mr  = mean(t_vals), mean(log_row)
        slope   = sum((t_vals .- mt) .* (log_row .- mr)) /
                  (sum((t_vals .- mt).^2) + 1e-10)
        -slope > 0 && push!(time_decays, -slope)
    end
    alpha_estimate = isempty(time_decays) ? 0.05 :
                     clamp(mean(time_decays), 0.001, 0.5)

    return Dict{String,Float64}("v" => v_estimate, "D" => D_estimate, "alpha" => alpha_estimate)
end

# ---------------------------------------------------------------------------
# Steady-state solver
# ---------------------------------------------------------------------------

"""
    compute_steady_state(v, D, alpha, S_fn, x_range; nx=100) → (u_steady, x_grid)

Compute the steady-state solution ∂u/∂t = 0 by solving the linear BVP:
  D·u'' − v·u' − α·u = −S(x)
with Neumann (zero-flux) boundary conditions.
"""
function compute_steady_state(
    v::Float64,
    D::Float64,
    alpha::Float64,
    S_fn::Function,
    x_range::Tuple{Float64,Float64};
    nx::Int=100
)::Tuple{Vector{Float64}, Vector{Float64}}

    x_min, x_max = x_range
    x_grid = range(x_min, x_max, length=nx) |> collect
    dx     = (x_max - x_min) / (nx - 1)

    # Matrix for D·u'' − v·u' − α·u  (centred differences)
    d   = fill(-2D / dx^2 - alpha, nx)
    du  = fill(D / dx^2 + v / (2dx), nx-1)
    dl  = fill(D / dx^2 - v / (2dx), nx-1)

    # Neumann BC
    d[1]   = -D / dx^2 - alpha;  du[1]   = D / dx^2 + v / (2dx)
    d[end] = -D / dx^2 - alpha;  dl[end] = D / dx^2 - v / (2dx)

    A = Tridiagonal(dl, d, du) |> Matrix
    b = Float64[-S_fn(x) for x in x_grid]

    u_steady = try
        A \ b
    catch
        [S_fn(x) / alpha for x in x_grid]
    end

    return u_steady, x_grid
end

end # module FluidModel
