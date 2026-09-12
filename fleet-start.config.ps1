# Per-repo fleet start config for mixx-dj-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'mixx-dj-mcp'
    BackendPort  = 11116
    FrontendPort = 11117
    HealthPath   = '/api/health'
    WebRoot      = 'web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'mixx_dj_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '11116' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
