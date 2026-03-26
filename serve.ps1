$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add("http://localhost:8888/")
$listener.Start()
Write-Host "Server running on http://localhost:8888/"
while($listener.IsListening) {
    $ctx = $listener.GetContext()
    $path = $ctx.Request.Url.LocalPath
    if($path -eq "/") { $path = "/8bit_cyberpunk_FIXED.html" }
    $file = Join-Path "C:\Users\carlo\OneDrive\game" $path.TrimStart("/")
    if(Test-Path $file) {
        $bytes = [IO.File]::ReadAllBytes($file)
        $ext = [IO.Path]::GetExtension($file).ToLower()
        $mime = switch($ext) {
            ".html" { "text/html; charset=utf-8" }
            ".css"  { "text/css" }
            ".js"   { "application/javascript" }
            ".png"  { "image/png" }
            ".jpg"  { "image/jpeg" }
            ".jpeg" { "image/jpeg" }
            ".json" { "application/json" }
            ".gif"  { "image/gif" }
            default { "application/octet-stream" }
        }
        $ctx.Response.ContentType = $mime
        $ctx.Response.ContentLength64 = $bytes.Length
        $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
        $ctx.Response.StatusCode = 404
    }
    $ctx.Response.Close()
}
