param (
  [Parameter(Mandatory = $true)]
  [string] $DOTENV_KEY,
  $APPLICATION_APP,
  [string] $SERVER_HOSTNAME
)
function StartApp {

  param (
    [string] $SERVER_HOSTNAME,
    [string] $DOTENV_KEY,
    [string] $APPLICATION_APP
  )



  $env:IN_PRODUCTION = 'true'
  $env:DOTENV_KEY = $DOTENV_KEY
  $env:APPLICATION_APP = $APPLICATION_APP
  $env:SERVER_HOSTNAME = $SERVER_HOSTNAME

  if ($APPLICATION_APP -eq 'worker') {

    function StartWorker {
      param (
        [string] $DOTENV_KEY,
        [string] $APPLICATION_APP
      )

      poetry run python -m celery -A app.run.app

    }

    poetry run python -m celery -A app.worker.app worker -E --loglevel=INFO -P threads -c 50

  } elseif ($APPLICATION_APP -eq 'quart') {

    function StartASGI {
      param (
        [string] $DOTENV_KEY,
        [string] $APPLICATION_APP
      )

      poetry run python -m app.asgi

    }

  } elseif ($APPLICATION_APP -eq 'beat') {
    function StartBeat {
      param (
        [string] $DOTENV_KEY,
        [string] $APPLICATION_APP
      )

      poetry run python -m celery -A app.beat.app beat --loglevel=INFO --scheduler job.FlaskSchedule.DatabaseScheduler

    }
  }

  switch ($APPLICATION_APP) {
    'worker' { StartWorker -DOTENV_KEY $DOTENV_KEY }
    'quart' { StartASGI -DOTENV_KEY $DOTENV_KEY }
    'beat' { StartBeat -DOTENV_KEY $DOTENV_KEY }
    default { Throw "Opção inválida: $APPLICATION_APP" }
  }

}

if ($APPLICATION_APP -is [string]) {
  Write-Host "Initializing $APPLICATION_APP"
  StartApp -DOTENV_KEY $DOTENV_KEY -APPLICATION_APP $APPLICATION_APP -SERVER_HOSTNAME $SERVER_HOSTNAME
} elseif ($APPLICATION_APP -is [System.Object]) {


  foreach ($app in $APPLICATION_APP) {

    if ($app -eq 'worker' -or $app -eq 'beat') {

      Write-Host "Initializing celery[$app]"

    } elseif ($app -eq 'quart') {

      Write-Host "Initializing asgi[$app]"
    }


    StartApp -DOTENV_KEY $DOTENV_KEY -APPLICATION_APP $app -SERVER_HOSTNAME $SERVER_HOSTNAME
  }
} else {
  Throw "Opção inválida: $APPLICATION_APP"
}





# SIG # Begin signature block
# MIII5QYJKoZIhvcNAQcCoIII1jCCCNICAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUhrIwCdepDJJtXvWlDPfjsrxZ
# VlqgggZIMIIGRDCCBSygAwIBAgITHgAAFw+vQ2JVyMWIGwAAAAAXDzANBgkqhkiG
# 9w0BAQsFADBPMRgwFgYKCZImiZPyLGQBGRYIaW50cmFuZXQxEzARBgoJkiaJk/Is
# ZAEZFgNmbXYxHjAcBgNVBAMTFWZtdi1TUlYtQVNHQVJELURDMi1DQTAeFw0yNTAy
# MTExNDI3NDhaFw0yNjAyMTExNDI3NDhaMHAxGDAWBgoJkiaJk/IsZAEZFghpbnRy
# YW5ldDETMBEGCgmSJomT8ixkARkWA2ZtdjERMA8GA1UECxMIVVNVQVJJT1MxEzAR
# BgNVBAsTClQuSS4gLSBERVYxFzAVBgNVBAMTDk5pY2hvbGFzIFNpbHZhMIIBIjAN
# BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2Btk8f9LgKVhfATflFIO2qNGiDnk
# hzkTrSht5E92DKeQATHz8gBoeb/tgsFCxbmhD/Tz8pwPrFnef5MxQO4qgdW17wUa
# hIVRgvsVgEWxm/FyQVw6rxty+ceVnHgD0BiQUfS7gA87tpwXhRpm7VoBg1+HtGQ7
# 8nX/eZsBVpvq1oCWRggrsSspo9Y/WF6fSszz2RgPTtb3PGR9hfCxt3sMf0/7rfar
# EaULKIINY3E6CWqyrmo7mdBWrQOBu+BcsnC2NODozcVyDgT/aWPNx5E29SxLlA9m
# cklwzNNZjMwbMm4B4RCxswWEDpgqZVceKUMGAbZWBkY3NlI88fW1L8FNDQIDAQAB
# o4IC9jCCAvIwJQYJKwYBBAGCNxQCBBgeFgBDAG8AZABlAFMAaQBnAG4AaQBuAGcw
# EwYDVR0lBAwwCgYIKwYBBQUHAwMwDgYDVR0PAQH/BAQDAgeAMB0GA1UdDgQWBBRP
# IYTcQglIKFxsAk+It2wecPU8mTAfBgNVHSMEGDAWgBQHujZf+/2B9+kUeELE3EIs
# MzGpbTCB2wYDVR0fBIHTMIHQMIHNoIHKoIHHhoHEbGRhcDovLy9DTj1mbXYtU1JW
# LUFTR0FSRC1EQzItQ0EsQ049U1JWLUFTR0FSRC1EQzIsQ049Q0RQLENOPVB1Ymxp
# YyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZpY2VzLENOPUNvbmZpZ3VyYXRpb24s
# REM9Zm12LERDPWludHJhbmV0P2NlcnRpZmljYXRlUmV2b2NhdGlvbkxpc3Q/YmFz
# ZT9vYmplY3RDbGFzcz1jUkxEaXN0cmlidXRpb25Qb2ludDCB/QYIKwYBBQUHAQEE
# gfAwge0wgbUGCCsGAQUFBzAChoGobGRhcDovLy9DTj1mbXYtU1JWLUFTR0FSRC1E
# QzItQ0EsQ049QUlBLENOPVB1YmxpYyUyMEtleSUyMFNlcnZpY2VzLENOPVNlcnZp
# Y2VzLENOPUNvbmZpZ3VyYXRpb24sREM9Zm12LERDPWludHJhbmV0P2NBQ2VydGlm
# aWNhdGU/YmFzZT9vYmplY3RDbGFzcz1jZXJ0aWZpY2F0aW9uQXV0aG9yaXR5MDMG
# CCsGAQUFBzABhidodHRwOi8vU1JWLUFTR0FSRC1EQzIuZm12LmludHJhbmV0L29j
# c3AwNgYDVR0RBC8wLaArBgorBgEEAYI3FAIDoB0MG25pY2hvbGFzLnNpbHZhQGZt
# di5pbnRyYW5ldDBOBgkrBgEEAYI3GQIEQTA/oD0GCisGAQQBgjcZAgGgLwQtUy0x
# LTUtMjEtNjIzMTQyOTQxLTM4NTI4ODkxMjMtMTQyNDU1NDMxNy0xMTQyMA0GCSqG
# SIb3DQEBCwUAA4IBAQDDsgCQ8r2xmf/XVeOk4ENIK9UTla4tVwoauX6FgqBsKJ+S
# SDyiKJgKpotv2nevoxHdzFp+EnpeCVFfkH54cXPzvB/aIJDSeLlIUXNgfBqbBi3C
# h7owZ6t0ktB6rvFwXWvW7UPAPU2PPYcv2F5smjcHS+LlE99Z8OMCxw2+B4YLIGt0
# iGsOXzSEczxAwd+QB0j6rRFfnw8rSmVMt7XAfb/xtV5NXb1OgarEhj8S1U8SME7Q
# tjirWcvmO2jaHwn8MQnLYLBfkDorebphdQnEJkWFx4fnhLQYAj5K/eY5gY8CZ+SM
# kxzJk1rawLFRa1SkhCc5TscGusK2WG3PzxhXXYXPMYICBzCCAgMCAQEwZjBPMRgw
# FgYKCZImiZPyLGQBGRYIaW50cmFuZXQxEzARBgoJkiaJk/IsZAEZFgNmbXYxHjAc
# BgNVBAMTFWZtdi1TUlYtQVNHQVJELURDMi1DQQITHgAAFw+vQ2JVyMWIGwAAAAAX
# DzAJBgUrDgMCGgUAoHgwGAYKKwYBBAGCNwIBDDEKMAigAoAAoQKAADAZBgkqhkiG
# 9w0BCQMxDAYKKwYBBAGCNwIBBDAcBgorBgEEAYI3AgELMQ4wDAYKKwYBBAGCNwIB
# FTAjBgkqhkiG9w0BCQQxFgQUYl6Mi/T253SBhen3rC+sgYlaowwwDQYJKoZIhvcN
# AQEBBQAEggEAwhf4jjimA5qkLh1d5yXVPfGdbB5HiOwu2UV1R1MjRz3WUig2Ysn9
# STN6RgoQJXAJv2WbpZk8ZxTeEEypQ22UeOLDLVd3pzuq4GIAUvCjqNCBZDSIjQi4
# mQ/xEgWDNwGnx8JYSFf/hO80RtcQ/8Cn9yiKIaMnZ6jlZj1GVievO2pxuvjrYysz
# wPeYdocHSXCmVEg3VilZgSD5C1KRwuCBO1r69jXaqrOKEf4Z73VsZcGKL2mMCzZc
# CybAKP8izWcUeiYfIUuU5XD90YY2cXVFgf6v5HMM9f7rhaZUkVvRM+IlQsLPtvgu
# c/ujYR3lYLR7YJA5PxWBI1Vv2WDjbxM3ow==
# SIG # End signature block
