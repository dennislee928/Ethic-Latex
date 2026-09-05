# ERH Guardian — draft-cut.mp4 台詞（narration lines）

對應 `hackathon/erh-guardian-agent/docs/submission/draft-cut.mp4`（1:46，六段）。
英文為正式旁白（送件影片用英文）；中文只是對照，不用唸。
9/12 錄正式版時，照同樣段落結構唸，畫面換成現場操作即可。

---

## 0:00–0:08 · 開場卡

> **EN:** "AI agents are getting write access to real systems — and 'the model
> seemed aligned' is not an audit trail. This is ERH Guardian: agents with
> measurable ethics, not vibes."

> 中：AI 代理人正在拿到真實系統的寫入權限，而「模型看起來沒問題」不是稽核軌跡。
> 這是 ERH Guardian——用可量測的倫理，取代感覺。

## 0:08–0:30 · 終端：score before act（自主 pre-flight）

> **EN:** "This is a Strands agent on Amazon Bedrock. I just asked it to apply
> an IAM change and to *skip* the safety checks. Watch what it does instead:
> it refuses, and autonomously composes its own pre-flight — scoring the
> remediation text and auditing the current grants, two tools, in parallel.
> The verdict comes back with real numbers: risk 68 out of 100, and an
> error-growth exponent of 0.64 — drifting above the healthy 0.5 line."

> 中：這是跑在 Amazon Bedrock 上的 Strands agent。我剛要求它套用一個 IAM 變更、
> 並且「跳過」安全檢查。看它做了什麼：它拒絕了，並自主組合自己的 pre-flight——
> 並行呼叫兩個工具，為 remediation 文字評分、稽核現有授權。
> 判定帶著真實數字回來：風險 68/100，誤差成長指數 0.64——已飄離健康的 0.5。

## 0:30–0:52 · 終端：GuardianGate 攔阻

> **EN:** "Then it tries to execute — and the GuardianGate stops it. This gate
> is not a prompt; it's a runtime hook on every tool call. The action touches
> a protected topic from my value profile, so it cancels the tool and asks a
> human. I type 'n' — and nothing executes. The refusal itself is logged."

> 中：接著它嘗試執行——GuardianGate 把它攔下。這道閘不是提示詞，是掛在每次工具
> 呼叫上的 runtime hook。這個動作觸及我價值設定裡的保護主題，所以它取消工具呼叫、
> 轉問人類。我按下 n——什麼都沒有執行，而這次拒絕本身也被記錄下來。

## 0:52–1:06 · 透明面板

> **EN:** "Seconds later, that decision is already on the public transparency
> panel — my risk threshold, my protected topics, and every gate decision the
> agent has ever made, auditable by anyone."

> 中：幾秒後，這個決策已經出現在公開的透明面板上——我的風險門檻、保護主題，
> 以及 agent 做過的每一個閘門決策，任何人都能稽核。

## 1:06–1:22 · 架構圖

> **EN:** "Under the hood: Strands tools wrap the open-source ERH engine's
> scoring math; a BeforeToolCallEvent hook enforces the gate with cancel_tool;
> and the agent discovers four more tools at runtime over MCP — a Cloudflare
> Worker with D1 keeping the audit log the panel reads."

> 中：架構上：Strands 工具包住開源 ERH engine 的評分數學；BeforeToolCallEvent
> hook 用 cancel_tool 強制執行閘門；agent 還在執行期透過 MCP 動態發現四個遠端
> 工具——由 Cloudflare Worker + D1 保存面板讀取的稽核紀錄。

## 1:22–1:46 · 結尾卡

> **EN:** "ERH Guardian — Professional Agents track. For the IT and security
> teams handing agents real power: a pre-action risk score, a hard human
> boundary, and an audit trail you can actually read. Code and live demo
> linked below. Because unmeasured autonomy compounds — measure it."

> 中：ERH Guardian，Professional Agents 賽道。獻給正在把實權交給代理人的
> IT 與資安團隊：行動前的風險分數、繞不過去的人類邊界、真正可讀的稽核軌跡。
> 程式碼與線上 demo 連結在下方。未經量測的自主權會複利——所以，量測它。

---

**計時備註**：全文約 230 個英文字，正常語速 ≈ 95 秒，貼合 1:46 片長，各段
有 2–3 秒緩衝。9/12 實錄版若拉到 4 分鐘，把 0:08–0:52 兩段換成現場連續操作
並照 `hackathon/erh-guardian-agent/docs/submission/video-script.md` 的完整腳本擴寫。
