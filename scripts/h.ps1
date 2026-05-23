# h.ps1 -- Hammerstein quick-fire wrapper (PowerShell)
#
# Maps shortcut verbs to Hammerstein templates so muscle-memory
# slash-style invocations work without typing the full template name.
# Bare invocation falls through to classifier auto-detect.
#
#   .\h.ps1 audit "<plan>"        -> --template audit-this-plan
#   .\h.ps1 scope "<idea>"        -> --template scope-this-idea
#   .\h.ps1 worth "<proposal>"    -> --template is-this-worth-doing
#   .\h.ps1 next "<context>"      -> --template what-should-we-do-next
#   .\h.ps1 sharper "<position>"  -> --template review-from-different-angle
#   .\h.ps1 "<any query>"         -> bare query (classifier auto-detects)
#
# Default model: openrouter (cheapest paid; conserves Anthropic).
# Override via $env:HAMMERSTEIN_MODEL or pass --model after the verb.
# ollama opt-in: set HAMMERSTEIN_MODEL=ollama (no API cost).

$shortcuts = @{
  "audit"   = "audit-this-plan"
  "scope"   = "scope-this-idea"
  "worth"   = "is-this-worth-doing"
  "next"    = "what-should-we-do-next"
  "sharper" = "review-from-different-angle"
}

$model = if ($env:HAMMERSTEIN_MODEL) { $env:HAMMERSTEIN_MODEL } else { "openrouter" }

if ($args.Count -eq 0) {
  Write-Host "Usage: .\h.ps1 <verb|query> [extra-flags...]"
  Write-Host "Verbs: audit / scope / worth / next / sharper"
  Write-Host "Or pass a bare query as the first arg to auto-classify."
  Write-Host "Default model: $model. Override via HAMMERSTEIN_MODEL env."
  exit 1
}

$first = ([string]$args[0]).ToLower()
if ($shortcuts.ContainsKey($first)) {
  $template = $shortcuts[$first]
  if ($args.Count -gt 1) {
    $rest = $args[1..($args.Count - 1)]
    & hammerstein --model $model --template $template @rest
  } else {
    & hammerstein --model $model --template $template
  }
} else {
  # Bare invocation: classifier handles template selection
  & hammerstein --model $model @args
}

exit $LASTEXITCODE
