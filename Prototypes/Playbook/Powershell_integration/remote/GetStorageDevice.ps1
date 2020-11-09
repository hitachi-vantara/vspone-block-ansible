param (
    [string]$serial = "440726",
    [Parameter(Mandatory=$true)][string]$username,
	[Parameter(Mandatory=$true)][string]$pass,
	[Parameter(Mandatory=$true)][string]$storageip
)

write-output "serial = $serial"
write-output $storageip
write-output $username
write-output $pass
write-output "---------------------"

Write-Host "Adding PSS Snapin..."
add-pssnapin Hitachi.Storage.Management.Powershell2.Admin
Write-Host "Adding Storage..."
Add-StorageDevice -s $serial -u $username -p $pass -ip $storageip
Write-Host "Getting Storage Device..."
Get-StorageDevice -s $serial
Write-Host "Your script executed successfully!"