"""
Streamlit Web Application for Ethical Riemann Hypothesis

This creates an interactive web interface for the ERH framework.
Run with: streamlit run app.py
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from core.action_space import generate_world, get_action_statistics
from core.judgement_system import (
    BiasedJudge, NoisyJudge, ConservativeJudge, RadicalJudge,
    evaluate_judgement, batch_evaluate
)
from core.ethical_primes import (
    select_ethical_primes, compute_Pi_and_error, analyze_error_growth
)
from analysis.zeta_function import build_m_sequence, compute_spectrum
from visualization.plots import setup_paper_style

# Page config
st.set_page_config(
    page_title="Ethical Riemann Hypothesis",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Ethical Riemann Hypothesis - Interactive Demo")
st.markdown("""
Explore the mathematical framework for analyzing moral judgment errors through 
an analogy with the Riemann Hypothesis in number theory.
""")

# Sidebar controls
# Sidebar controls
st.sidebar.header("Navigation")
mode = st.sidebar.radio("Mode", ["Live Simulation", "Results Browser"])

if mode == "Live Simulation":
    st.sidebar.header("Configuration")
    
    num_actions = st.sidebar.slider("Number of Actions", 100, 5000, 1000, 100)
    complexity_dist = st.sidebar.selectbox(
        "Complexity Distribution",
        ["zipf", "uniform", "power_law"],
        index=0
    )
    judge_type = st.sidebar.selectbox(
        "Judge Type",
        ["Biased", "Noisy", "Conservative", "Radical"],
        index=0
    )
    tau = st.sidebar.slider("Error Threshold (τ)", 0.1, 0.5, 0.3, 0.05)
    
    # Judge parameters
    st.sidebar.subheader("Judge Parameters")
    if judge_type == "Biased":
        bias_strength = st.sidebar.slider("Bias Strength", 0.0, 0.5, 0.2, 0.05)
        noise_scale = st.sidebar.slider("Noise Scale", 0.0, 0.3, 0.1, 0.05)
    elif judge_type == "Noisy":
        noise_scale = st.sidebar.slider("Noise Scale", 0.1, 0.5, 0.3, 0.05)
    elif judge_type == "Conservative":
        threshold = st.sidebar.slider("Threshold", 0.0, 1.0, 0.5, 0.1)
    elif judge_type == "Radical":
        amplification = st.sidebar.slider("Amplification", 1.0, 2.0, 1.5, 0.1)
    
    # Main content for Live Simulation
    st.header("Live Simulation")
    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running simulation..."):
            # Generate world
            actions = generate_world(
                num_actions=num_actions,
                complexity_dist=complexity_dist,
                random_seed=42
            )
            
            # Create judge
            if judge_type == "Biased":
                judge = BiasedJudge(bias_strength=bias_strength, noise_scale=noise_scale)
            elif judge_type == "Noisy":
                judge = NoisyJudge(noise_scale=noise_scale)
            elif judge_type == "Conservative":
                judge = ConservativeJudge(threshold=threshold)
            else:
                judge = RadicalJudge(amplification=amplification)
            
            # Evaluate
            evaluate_judgement(actions, judge, tau=tau)
            
            # Extract primes
            primes = select_ethical_primes(actions, importance_quantile=0.9)
            
            # Compute distributions
            Pi_x, B_x, E_x, x_vals = compute_Pi_and_error(primes, X_max=100)
            
            # Analyze
            analysis = analyze_error_growth(E_x, x_vals)
            
            # Display results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Actions", num_actions)
            with col2:
                st.metric("Mistakes", sum(a.mistake_flag for a in actions if a.mistake_flag))
            with col3:
                st.metric("Ethical Primes", len(primes))
            with col4:
                erh_status = "✓ Satisfied" if analysis['erh_satisfied'] else "✗ Not Satisfied"
                st.metric("ERH Status", erh_status)
            
            # Plot
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=x_vals, y=Pi_x, name='Π(x)', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=x_vals, y=B_x, name='B(x)', line=dict(color='red', dash='dash')))
            fig.add_trace(go.Scatter(x=x_vals, y=E_x, name='E(x)', line=dict(color='green')))
            
            fig.update_layout(
                title="Ethical Prime Distribution",
                xaxis_title="Complexity x",
                yaxis_title="Count",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Error growth
            abs_E = np.abs(E_x)
            valid_mask = (abs_E > 0) & (x_vals > 1)
            
            if np.sum(valid_mask) > 0:
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=x_vals[valid_mask],
                    y=abs_E[valid_mask],
                    mode='markers',
                    name='|E(x)|',
                    marker=dict(size=4)
                ))
                
                # Add fitted line if available
                if 'estimated_exponent' in analysis and not np.isnan(analysis['estimated_exponent']):
                    alpha = analysis['estimated_exponent']
                    C = analysis.get('constant_C', 1.0)
                    x_fit = np.logspace(np.log10(x_vals[valid_mask].min()), 
                                       np.log10(x_vals[valid_mask].max()), 100)
                    y_fit = C * (x_fit ** alpha)
                    fig2.add_trace(go.Scatter(
                        x=x_fit, y=y_fit,
                        name=f'Fit: C·x^{alpha:.3f}',
                        line=dict(dash='dash')
                    ))
                
                fig2.update_layout(
                    title="Error Growth (Log-Log Scale)",
                    xaxis_title="Complexity x",
                    yaxis_title="|E(x)|",
                    xaxis_type="log",
                    yaxis_type="log",
                    height=400
                )
                
                st.plotly_chart(fig2, use_container_width=True)
            
            # Statistics
            st.subheader("Analysis Results")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Error Growth Analysis:**")
                st.write(f"- Estimated exponent α: {analysis.get('estimated_exponent', 'N/A'):.3f}")
                st.write(f"- Expected (ERH): 0.500")
                st.write(f"- Growth rate: {analysis.get('growth_rate', 'N/A')}")
                st.write(f"- R² (fit quality): {analysis.get('r_squared', 0):.3f}")
            
            with col2:
                stats = get_action_statistics(actions)
                st.write("**Action Statistics:**")
                st.write(f"- Mistake rate: {stats['mistakes']['rate']:.1%}")
                st.write(f"- MAE: {stats['error']['mae']:.3f}")
                st.write(f"- RMSE: {stats['error']['rmse']:.3f}")

elif mode == "Results Browser":
    st.header("Results Browser")
    st.markdown("Upload JSON result files (generated by batch simulations) to analyze them.")
    
    uploaded_files = st.file_uploader("Upload .json Result Files", type="json", accept_multiple_files=True)
    
    if uploaded_files:
        import pandas as pd
        data = []
        for uploaded_file in uploaded_files:
            try:
                res = json.load(uploaded_file)
                row = {
                    'filename': uploaded_file.name,
                    'timestamp': res.get('timestamp'),
                    'complexity_dist': res['config']['complexity_dist'],
                    'num_actions': res['config']['num_actions'],
                    'mistake_rate': res['metrics']['mistake_rate'],
                    'ethical_primes_count': res['metrics']['ethical_primes_count'],
                    'erh_satisfied': res['metrics']['erh_satisfied'],
                    'estimated_exponent': res['metrics'].get('estimated_exponent'),
                }
                data.append(row)
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {e}")
        
        if data:
            df = pd.DataFrame(data)
            
            st.subheader("Aggregated Statistics")
            st.dataframe(df)
            
            st.subheader("Visualizations")
            col1, col2 = st.columns(2)
            
            with col1:
                fig_mistakes = go.Figure()
                fig_mistakes.add_trace(go.Box(
                    x=df['complexity_dist'],
                    y=df['mistake_rate'],
                    name="Mistake Rate"
                ))
                fig_mistakes.update_layout(title="Mistake Rate by Distribution", yaxis_title="Mistake Rate")
                st.plotly_chart(fig_mistakes, use_container_width=True)
                
            with col2:
                if 'estimated_exponent' in df.columns:
                    fig_alpha = go.Figure()
                    fig_alpha.add_trace(go.Box(
                        x=df['complexity_dist'],
                        y=df['estimated_exponent'],
                        name="Alpha"
                    ))
                    fig_alpha.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="ERH Limit")
                    fig_alpha.update_layout(title="Alpha (Exponent) Distribution", yaxis_title="Alpha")
                    st.plotly_chart(fig_alpha, use_container_width=True)

# Info section
with st.expander("About the Ethical Riemann Hypothesis"):
    st.markdown("""
    The Ethical Riemann Hypothesis (ERH) proposes that in a "healthy" moral judgment system,
    the error in predicting critical misjudgments grows at most like √x, where x is the complexity
    of the decision.
    
    **Key Concepts:**
    - **Ethical Primes**: Critical misjudgments that represent fundamental errors
    - **Π(x)**: Count of ethical primes up to complexity x
    - **E(x) = Π(x) - B(x)**: Error term comparing actual vs expected distribution
    - **ERH**: |E(x)| ≤ C·x^(1/2 + ε) for healthy systems
    
    **Interpretation:**
    - If ERH is satisfied (α ≈ 0.5): System is "Riemann-healthy"
    - If α < 0.5: Better than ERH predicts
    - If α > 0.5: Worse than ERH, may indicate systematic problems
    """)

