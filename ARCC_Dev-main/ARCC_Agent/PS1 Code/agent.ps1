function Get-NetUserJson {
    # Ejecutar 'net user' y extraer la lista de usuarios
    $usersRaw = net user | Select-Object -Skip 4 | Where-Object { $_ -match '\S' }

    # Filtrar la última línea para evitar la frase "Se ha completado el comando correctamente."
    $usersRaw = $usersRaw | Where-Object { $_ -notmatch "Se ha completado el comando correctamente" }

    # Unir todas las líneas en una sola y luego dividir por múltiples espacios
    $usersList = ($usersRaw -join " ") -split '\s{2,}'

    # Crear objetos JSON con cada usuario
    $usersJson = $usersList | ForEach-Object { [PSCustomObject]@{ Username = $_ } } | ConvertTo-Json -Depth 1

    # Retornar el JSON de usuarios
    return $usersJson
}

function Get-NetstatJson {
    # Ejecutar netstat y capturar la salida
    $netstatOutput = netstat -ano | Select-Object -Skip 4

    # Procesar cada línea y extraer datos relevantes
    $connections = @()
    foreach ($line in $netstatOutput) {
        $columns = $line -split "\s+" | Where-Object { $_ -ne "" }
        
        if ($columns.Length -ge 5) {
            $obj = [PSCustomObject]@{
                Protocol       = $columns[0]
                LocalAddress   = $columns[1]
                RemoteAddress  = $columns[2]
                State          = if ($columns.Length -eq 5) { $columns[3] } else { "N/A" } # UDP no tiene estado
                PID            = $columns[-1]
            }
            $connections += $obj
        }
    }

    # Convertir a JSON y devolver
    return $connections | ConvertTo-Json -Depth 1
}

function Get-ProcessJson {
    $processes = Get-Process | Select-Object ProcessName, Id, Path
    return $processes | ConvertTo-Json -Depth 1
}

function Get-SecurityEventsJson {
    # Obtener los eventos de seguridad en formato XML
    $xmlData = wevtutil qe Security /c:150 /f:xml | Out-String

    # Agregar un nodo raíz para evitar errores de conversión
    $xmlData = "<Events>$xmlData</Events>"

    # Convertir la salida a XML
    [xml]$xmlEvents = $xmlData

    # Extraer información relevante de los eventos
    $events = $xmlEvents.Events.Event | ForEach-Object {
        [PSCustomObject]@{
            TimeCreated  = $_.System.TimeCreated.SystemTime
            EventID      = if ($_.System.EventID.'#text') { $_.System.EventID.'#text' } else { $_.System.EventID }
            Level        = if ($_.System.Level) { [int]$_.System.Level } else { "N/A" }
            Task         = if ($_.System.Task) { [int]$_.System.Task } else { "N/A" }
            Opcode       = if ($_.System.Opcode) { [int]$_.System.Opcode } else { "N/A" }
            Computer     = if ($_.System.Computer) { $_.System.Computer } else { "N/A" }
            ProviderName = if ($_.System.Provider.Name) { $_.System.Provider.Name } else { "N/A" }
            Message      = if ($_.RenderingInfo.Message) { $_.RenderingInfo.Message } else { "N/A" }
        }
    }

    # Convertir la lista de eventos a JSON
    return $events | ConvertTo-Json -Depth 1
}

function Get-StartupProgramsJson {
    # Obtener programas de inicio desde el Registro
    $startupRegistryUser = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object * -ExcludeProperty PS* 2>$null
    $startupRegistryAll = Get-ItemProperty -Path "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run" | Select-Object * -ExcludeProperty PS* 2>$null

    # Obtener programas desde carpetas de inicio
    $startupFolderUser = Get-ChildItem -Path "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup" | Select-Object Name, FullName
    $startupFolderAll = Get-ChildItem -Path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" | Select-Object Name, FullName

    # Convertir a JSON
    $result = [PSCustomObject]@{
        StartupRegistryUser = $startupRegistryUser
        StartupRegistryAll  = $startupRegistryAll
        StartupFolderUser   = $startupFolderUser
        StartupFolderAll    = $startupFolderAll
    }

    return $result | ConvertTo-Json -Depth 3
}

function Get-RecentFilesJson {
    param (
        [string[]]$dangerousExtensions = @(".exe", ".dll", ".bat", ".vbs", ".ps1", ".scr", ".com", ".jar", ".js", ".wsf")
    )

    # Definir las rutas de interés
    $paths = @(
        "$env:APPDATA",
        "$env:LOCALAPPDATA",
        "$env:PROGRAMDATA",
        "$env:TEMP",
        "$env:USERPROFILE\Downloads",
        "$env:USERPROFILE\Desktop",
        "$env:USERPROFILE\Documents"
    )

    # Obtener la fecha de hace 5 días
    $dateLimit = (Get-Date).AddDays(-5)

    # Lista para almacenar los archivos recientes
    $recentFiles = @()

    foreach ($path in $paths) {
        if (Test-Path $path) {
            # Obtener archivos modificados en los últimos 5 días y con tamaño mayor a 0
            $files = Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | 
                     Where-Object { $_.LastWriteTime -gt $dateLimit -and $_.Length -gt 0 } | 
                     Select-Object FullName, @{Name="LastWriteTime"; Expression={$_.LastWriteTime.ToString("yyyy-MM-ddTHH:mm:ssZ")}}, Length

            foreach ($file in $files) {
                $fileInfo = [PSCustomObject]@{
                    FullName      = $file.FullName
                    LastWriteTime = $file.LastWriteTime
                    Length        = $file.Length
                    MD5           = $null
                }

                # Calcular hash si la extensión está en la lista de archivos peligrosos
                if ($dangerousExtensions -contains [System.IO.Path]::GetExtension($file.FullName).ToLower()) {
                    try {
                        $fileStream = [System.IO.File]::OpenRead($file.FullName)
                        $md5 = New-Object System.Security.Cryptography.MD5CryptoServiceProvider
                        $hashBytes = $md5.ComputeHash($fileStream)
                        $fileStream.Close()
                        $fileInfo.MD5 = ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
                    } catch {
                        $fileInfo.MD5 = "Error al calcular hash"
                    }
                }

                $recentFiles += $fileInfo
            }
        }
    }

    # Convertir a JSON y retornar
    return $recentFiles | ConvertTo-Json -Depth 2
}

function Get-ScheduledTasksJson {
    # Obtener la salida de 'schtasks' en formato LIST
    $tasksRaw = schtasks /query /fo LIST /v | Out-String

    # Dividir por líneas
    $tasksArray = $tasksRaw -split "`r`n"

    # Lista de tareas
    $tasks = @()
    $task = @{}

    foreach ($line in $tasksArray) {
        if ($line -match "^(.*?):\s(.*)$") {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()

            if ($key -eq "Nombre de tarea" -or $key -eq "TaskName") {
                if ($task.Count -gt 0) {
                    $tasks += [PSCustomObject]$task
                    $task = @{}
                }
            }

            $task[$key] = $value
        }
    }

    if ($task.Count -gt 0) {
        $tasks += [PSCustomObject]$task
    }

    # Convertir la lista a JSON
    return $tasks | ConvertTo-Json -Depth 2
}

function Get-SuspiciousRegistryKeys {
    # Lista de claves críticas
    $registryKeys = @(
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce",
        "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Winlogon",
        "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Userinit",
        "HKLM:\Software\Microsoft\Windows NT\CurrentVersion\Winlogon\Shell",
        "HKLM:\Software\Policies\Microsoft\Windows Defender",
        "HKLM:\Software\Policies\Microsoft\WindowsFirewall",
        "HKLM:\System\CurrentControlSet\Control\Terminal Server",
        "HKLM:\Software\Google\Chrome\Extensions",
        "HKCU:\Software\Mozilla\Firefox\Extensions"
    )

    # Analizar cada clave
    $registryEntries = @()

    foreach ($key in $registryKeys) {
        if (Test-Path $key) {
            try {
                $values = Get-ItemProperty -Path $key | Select-Object * -ExcludeProperty PS* 2>$null
                foreach ($property in $values.PSObject.Properties) {
                    $data = $property.Value
                    $registryEntries += [PSCustomObject]@{
                        RegistryKey = $key
                        ValueName   = $property.Name
                        ValueData   = $data
                    }
                }
            } catch {
                $registryEntries += [PSCustomObject]@{
                    RegistryKey = $key
                    ValueName   = "Error al acceder"
                    ValueData   = "Clave protegida o permiso denegado"
                }
            }
        }
    }

    # Convertir a JSON y retornar
    return $registryEntries | ConvertTo-Json -Depth 2
}

function Send-AgentData {
    param (
        [int]$caseID,  # Case ID ingresado por consola
        [string]$domain  # Dominio ingresado por consola
    )

    # Construir la URL completa de la API
    $apiURL = "http://127.0.0.1:8000/api/v1/agent_data/"

    # Obtener datos del sistema
    $users = Get-NetUserJson | ConvertFrom-Json
    $connections = Get-NetstatJson | ConvertFrom-Json
    $processes = Get-ProcessJson | ConvertFrom-Json
    $events = Get-SecurityEventsJson | ConvertFrom-Json
    $startupPrograms = Get-StartupProgramsJson | ConvertFrom-Json
    $recentFiles = Get-RecentFilesJson | ConvertFrom-Json
    $tasks = Get-ScheduledTasksJson | ConvertFrom-Json
    $suspiciousRegistryKeys = Get-SuspiciousRegistryKeys | ConvertFrom-Json

    # Crear JSON con los datos recopilados asegurando UTF-8
    $data = @{
        case_id            = $caseID
        users              = $users
        network_connections = $connections
        processes          = $processes
        security_events    = $events
        startup_programs   = $startupPrograms
        recent_files       = $recentFiles
        scheduled_tasks    = $tasks
        registry_keys      = $suspiciousRegistryKeys
    } | ConvertTo-Json -Depth 3

    # Guardar JSON en un archivo temporal con UTF-8 sin BOM
    $tempJsonPath = "$env:TEMP\data.json"
    [System.IO.File]::WriteAllText($tempJsonPath, $data, (New-Object System.Text.UTF8Encoding($false)))

    # Leer el JSON con codificación correcta
    $jsonData = Get-Content -Path $tempJsonPath -Raw -Encoding UTF8

    # Enviar datos a la API Django
    try {
        $response = Invoke-RestMethod -Uri $apiURL -Method Post -Body $jsonData -ContentType "application/json; charset=utf-8"
        Write-Host "Datos enviados exitosamente al caso ID: $caseID a $apiURL" -ForegroundColor Green
        return $response
    } catch {
        Write-Host "Error al enviar los datos: $_" -ForegroundColor Red
    }
}

# Solicitar Case ID y Dominio por consola
$caseID = Read-Host "Ingrese el Case ID"
$domain = Read-Host "Ingrese el dominio del servidor (ejemplo: 192.168.2.10:8000 o api.example.com)"

# Call the function and display the result
$users = Get-NetUserJson
$connections = Get-NetstatJson
$processes = Get-ProcessJson
$events = Get-SecurityEventsJson
$startupPrograms = Get-StartupProgramsJson
$recentFiles = Get-RecentFilesJson
$tasks = Get-ScheduledTasksJson
$suspiciousRegistryKeys = Get-SuspiciousRegistryKeys

# Llamar a la función con los valores ingresados
Send-AgentData -caseID $caseID -domain $domain
Set-ExecutionPolicy Restricted -Scope CurrentUser
