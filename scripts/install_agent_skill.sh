# #region agent log
#LOG_FILE="c:/Users/dennis.lee/Documents/GitHub/pandora_box_console_IDS-IPS/.cursor/debug.log"
#log_debug() {
#  echo "{\"id\":\"log_$(date +%s)_$$\",\"timestamp\":$(date +%s)000,\"location\":\"install_skills.sh:$1\",\"message\":\"$2\",\"data\":$3,\"sessionId\":\"debug-session\",\"runId\":\"run1\",\"hypothesisId\":\"$4\"}" >> "$LOG_FILE"
#}

# 錯誤處理函數：優雅地處理不存在的倉庫
install_skill_safe() {
  local repo=$1
  local description=$2
  # #region agent log
  #log_debug "$3" "Attempting to install: $description" "{\"repo\":\"$repo\"}" "A"
  # #endregion
  if npx openskills install "$repo" 2>&1; then
    # #region agent log
    #log_debug "$4" "Successfully installed: $description" "{\"repo\":\"$repo\",\"success\":true}" "A"
    # #endregion
    echo "✅ Installed: $description"
  else
    local exit_code=$?
    # #region agent log
    #log_debug "$5" "Failed to install: $description" "{\"repo\":\"$repo\",\"exit_code\":$exit_code,\"failed\":true}" "A"
    # #endregion
    echo "⚠️  Skipped: $description (repository not found or unavailable)"
    return 0  # 繼續執行，不中斷腳本
  fi
}
# #endregion

# 注意：awesome-claude-skills 只是一個列表倉庫，不包含實際技能
# systematic-debugging 已包含在 obra/superpowers 中，無需單獨安裝

# 安裝後端與通用開發增強
# #region agent log
#log_debug "10" "Installing obra/superpowers" "{\"source\":\"obra/superpowers\"}" "B"
# #endregion
npx openskills install obra/superpowers

# FastAPI 技能 - 使用 jezweb/claude-skills (包含 FastAPI 技能)
# #region agent log
#log_debug "11" "Installing jezweb/claude-skills (includes FastAPI skill)" "{\"source\":\"jezweb/claude-skills\"}" "C"
# #endregion
install_skill_safe "jezweb/claude-skills" "jezweb/claude-skills (FastAPI, Flask, Cloudflare, React, Tailwind)" "12" "13" "14"

# Go 相關技能說明
# ============================================
# 注意：目前沒有找到可以直接用 openskills 安裝的 Go 技能倉庫
# 
# Go Agent Skills 相關資源：
# 1. tRPC-Agent-Go 框架 (trpc.group/trpc-go/trpc-agent-go)
#    - 這是構建 Go AI Agent 的框架，支持 Skills 功能
#    - 安裝方式：go get trpc.group/trpc-go/trpc-agent-go
#    - 文檔：https://trpc-group.github.io/trpc-agent-go/zh/skill/
#    - 包含示例技能和完整的 Skills 實現
#
# 2. go-agentskills (github.com/niwoerner/go-agentskills)
#    - 這是 Skills 規範驗證工具，不是技能倉庫
#    - 用於驗證和處理 Agent Skills 規範
#
# 3. 創建自己的 Go 技能：
#    - 參考 agentskills.io 規範：https://agentskills.io/integrate-skills
#    - 創建包含 SKILL.md 的技能目錄
#    - 使用 tRPC-Agent-Go 框架來構建支持技能的 Go Agent
#
# 4. 臨時方案：
#    - 使用 obra/superpowers 中的通用開發技能
#    - 這些技能提供通用的開發模式，適用於多種語言包括 Go
# ============================================
echo "ℹ️  Go skills: No dedicated Go skill repository found."
echo "   - For Go Agent framework: trpc.group/trpc-go/trpc-agent-go"
echo "   - For skill validation: github.com/niwoerner/go-agentskills"
echo "   - For creating Go skills: See https://agentskills.io/integrate-skills"
echo "   - Using obra/superpowers for general development patterns"

# 安裝雲原生與測試（這些倉庫可能不存在，使用安全安裝函數）
install_skill_safe "cloud-native/k8s-skill" "cloud-native/k8s-skill" "15" "16" "17"
install_skill_safe "terraform-experts/iac-skill" "terraform-experts/iac-skill" "18" "19" "20"
install_skill_safe "test-automation/robot-skill" "test-automation/robot-skill" "21" "22" "23"

# 這個庫包含了多種開發與運維相關的 SKILL.md
install_skill_safe "skillmatic-ai/awesome-agent-skills" "skillmatic-ai/awesome-agent-skills" "24" "25" "26"

# 注意：chentsulin/claude-skills 倉庫不存在，已移除
# 如需類似技能，可考慮 jezweb/claude-skills

# #region agent log
#log_debug "27" "Syncing skills to AGENTS.md" "{\"action\":\"sync\"}" "D"
# #endregion
npx openskills sync