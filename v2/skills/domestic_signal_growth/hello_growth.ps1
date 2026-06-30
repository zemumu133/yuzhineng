param(
  [string]$Product = ""
)

$baseMessage = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("5Zu95YaF6JCl6ZSA5L+h5Y+356m/6YCPIFNraWxsIOWNoOS9je+8mui+k+WFpeS6p+WTge+8jOi+k+WHuuWVhuacuuWIpOaWreOAgeWGheWuueW7uuiuruWSjOW+heWKnuOAgg=="))
$productPrefix = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("IOW9k+WJjei+k+WFpeS6p+WTge+8mg=="))

if ($Product) {
  Write-Output ($baseMessage + $productPrefix + $Product)
} else {
  Write-Output $baseMessage
}
