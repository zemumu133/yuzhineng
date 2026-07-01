param(
  [string]$InputJson = ""
)

$ErrorActionPreference = "Stop"

$defaultInput = @{
  product = "职业证书考评服务"
  target_customers = @("培训机构", "人力资源公司")
  platforms = @("小红书", "抖音")
  mode = "draft_only"
}

try {
  if ($InputJson.Trim().Length -gt 0) {
    $parsed = $InputJson | ConvertFrom-Json
    $product = if ($parsed.product) { [string]$parsed.product } else { $defaultInput.product }
    $targets = if ($parsed.target_customers) { @($parsed.target_customers) } else { $defaultInput.target_customers }
    $platforms = if ($parsed.platforms) { @($parsed.platforms) } else { $defaultInput.platforms }
    $mode = if ($parsed.mode) { [string]$parsed.mode } else { $defaultInput.mode }
  } else {
    $product = $defaultInput.product
    $targets = $defaultInput.target_customers
    $platforms = $defaultInput.platforms
    $mode = $defaultInput.mode
  }
} catch {
  $product = $defaultInput.product
  $targets = $defaultInput.target_customers
  $platforms = $defaultInput.platforms
  $mode = $defaultInput.mode
}

$targetText = ($targets -join "、")
$platformText = ($platforms -join "、")

$result = [ordered]@{
  skill = "domestic_signal_growth"
  mode = $mode
  received = [ordered]@{
    product = $product
    target_customers = $targets
    platforms = $platforms
  }
  opportunity_judgement = "$product 对 $targetText 有明确的内容获客机会，适合先用公开信息研究、痛点内容和人工审批触达验证需求。"
  target_customer_types = @(
    "职业培训机构：需要招生线索、课程转化和证书可信度内容",
    "人力资源服务公司：需要企业客户教育、岗位能力证明和培训合作线索",
    "本地教育咨询团队：需要低成本内容矩阵和私域沉淀"
  )
  xiaohongshu_content_ideas = @(
    "证书考评到底适合哪些人：用真实政策口径做科普，不夸大就业承诺",
    "培训机构如何把证书项目讲清楚：招生页、笔记、私域话术三件套",
    "HR 为什么关注职业证书：能力证明、岗位匹配和培训合规"
  )
  douyin_content_ideas = @(
    "60 秒解释职业证书考评服务的适用人群和注意事项",
    "培训机构招生常见误区：过度承诺、案例不清、转化路径断层",
    "HR 视角看证书培训：哪些内容适合公开传播，哪些必须人工确认"
  )
  followup_drafts = @(
    "您好，看到贵机构在做职业培训相关业务。我们在做 AI 获客和内容运营系统，可以先帮您梳理一版不外发的证书项目内容选题和线索跟进草稿，您人工确认后再使用。",
    "如果您正在推广职业证书类项目，我们可以先做一次公开信息研究，输出适合小红书/抖音的内容方向、风险提示和人工待办，不做自动私信或自动评论。"
  )
  todos = @(
    "补充目标城市、证书类别和合规宣传边界",
    "收集 10 个公开竞品页面或公开账号链接",
    "生成小红书笔记草稿、抖音脚本草稿和人工跟进待办",
    "由人工确认后再决定是否发布或联系"
  )
  risk_notes = @(
    "不得承诺包过、保就业、保收入或虚构合作案例",
    "外部发布、评论、私信、邮件必须进入人工审批",
    "没有公开联系方式时必须标记 unknown，不能编造联系人"
  )
}

$result | ConvertTo-Json -Depth 8
