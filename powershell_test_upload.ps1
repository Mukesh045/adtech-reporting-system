# Correct PowerShell command to test CSV upload API with multipart form data

$filePath = "sample.csv"
$uri = "http://localhost:8000/api/data/import"

$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    'Content-Disposition: form-data; name="file"; filename="' + [System.IO.Path]::GetFileName($filePath) + '"',
    'Content-Type: text/csv',
    "",
    [System.IO.File]::ReadAllText($filePath),
    "--$boundary--",
    ""
)

$body = [string]::Join($LF, $bodyLines)

$headers = @{
    "Content-Type" = "multipart/form-data; boundary=$boundary"
}

Invoke-RestMethod -Uri $uri -Method Post -Body $body -Headers $headers
