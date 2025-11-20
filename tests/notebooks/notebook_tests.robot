*** Settings ***
Documentation     Test suite for Jupyter notebooks in the Ethical Riemann Hypothesis project
Library           JupyterLibrary
Library           Collections
Library           OperatingSystem
Library           String
Resource          resources/variables.robot

*** Variables ***
${PROJECT_ROOT}    ${CURDIR}${/}..${/}..
${NOTEBOOKS_DIR}   ${PROJECT_ROOT}${/}simulation${/}notebooks
${OUTPUT_DIR}      ${PROJECT_ROOT}${/}simulation${/}output
${TEST_OUTPUT_DIR} ${CURDIR}${/}output

*** Test Cases ***
Test Notebook 01 Basic Simulation
    [Documentation]    Test that 01_basic_simulation.ipynb executes successfully and generates expected outputs
    [Tags]    notebook    basic
    ${notebook}=    Set Variable    01_basic_simulation.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify expected output files
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}paper_fig1_pi_b_e.pdf    1000
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}paper_fig2_error_growth.pdf    1000

Test Notebook 02 Judge Comparison
    [Documentation]    Test that 02_judge_comparison.ipynb executes successfully and generates comparison report
    [Tags]    notebook    comparison
    ${notebook}=    Set Variable    02_judge_comparison.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify expected output files
    Verify Output File Exists    ${OUTPUT_DIR}${/}judge_comparison_report.md    500
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}paper_fig3_judge_comparison.pdf    1000

Test Notebook 03 Zeta Zeros
    [Documentation]    Test that 03_zeta_zeros.ipynb executes successfully and generates zeta analysis plots
    [Tags]    notebook    zeta
    ${notebook}=    Set Variable    03_zeta_zeros.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify expected output files
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}03_zeros.pdf    1000
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}03_spectrum.pdf    1000

Test Notebook 04 Parameter Sensitivity
    [Documentation]    Test that 04_parameter_sensitivity.ipynb executes successfully
    [Tags]    notebook    sensitivity
    ${notebook}=    Set Variable    04_parameter_sensitivity.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify expected output files
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}04_sensitivity_bias.pdf    1000

Test Notebook 05 Generate Paper Figures
    [Documentation]    Test that 05_generate_paper_figures.ipynb generates all paper figures
    [Tags]    notebook    figures    paper
    ${notebook}=    Set Variable    05_generate_paper_figures.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify all paper figures exist
    @{figures}=    Create List
    ...    paper_fig1_pi_b_e.pdf
    ...    paper_fig2_error_growth.pdf
    ...    paper_fig3_judge_comparison.pdf
    ...    paper_fig4_exponent_comparison.pdf
    ...    paper_fig5_spectrum.pdf
    ...    paper_fig6_zeros.pdf
    ...    paper_fig7_complexity_dist.pdf
    
    FOR    ${figure}    IN    @{figures}
        Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}${figure}    1000
    END

Test Notebook 06 Baseline Comparison
    [Documentation]    Test that 06_baseline_comparison.ipynb executes successfully
    [Tags]    notebook    baseline
    ${notebook}=    Set Variable    06_baseline_comparison.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify expected output files
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}06_baseline_comparison.pdf    1000
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}06_error_terms_comparison.pdf    1000
    Verify Output File Exists    ${OUTPUT_DIR}${/}baseline_comparison_summary.csv    100

Test Notebook 07 Zeta Zeros Deep Analysis
    [Documentation]    Test that 07_zeta_zeros_deep_analysis.ipynb executes successfully
    [Tags]    notebook    zeta    deep
    ${notebook}=    Set Variable    07_zeta_zeros_deep_analysis.ipynb
    ${notebook_path}=    Join Path    ${NOTEBOOKS_DIR}    ${notebook}
    
    # Execute notebook
    Execute Notebook    ${notebook_path}
    
    # Verify expected output files
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}07_critical_line_analysis.pdf    1000
    Verify Output File Exists    ${OUTPUT_DIR}${/}figures${/}07_zero_correlation.pdf    1000

*** Keywords ***
Execute Notebook
    [Arguments]    ${notebook_path}
    [Documentation]    Execute a notebook and verify it completes without errors
    Log    Executing notebook: ${notebook_path}
    
    # Start Jupyter server if not running
    ${server_running}=    Run Keyword And Return Status    Jupyter Server Is Running
    Run Keyword If    not ${server_running}    Start Jupyter Server
    
    # Execute notebook
    ${result}=    Execute Jupyter Notebook    ${notebook_path}
    Should Be Equal    ${result}[status]    ok    Notebook execution failed
    
    Log    Notebook executed successfully

Verify Output File Exists
    [Arguments]    ${file_path}    ${min_size}=0
    [Documentation]    Verify that an output file exists and meets minimum size requirement
    ${exists}=    Run Keyword And Return Status    File Should Exist    ${file_path}
    Should Be True    ${exists}    Output file does not exist: ${file_path}
    
    ${size}=    Get File Size    ${file_path}
    Should Be True    ${size} >= ${min_size}    File ${file_path} is too small: ${size} bytes < ${min_size} bytes
    
    Log    Verified output file: ${file_path} (${size} bytes)

