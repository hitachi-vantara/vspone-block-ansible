param (
    [string]$serial = "440726",
    [Parameter(Mandatory=$true)][string]$username,
	[Parameter(Mandatory=$true)][string]$pass,
	[Parameter(Mandatory=$true)][string]$storageip,
	[Parameter(Mandatory=$true)][string]$lunid
)

write-output "serial = $serial"			#440726
write-output $storageip		    #172.17.41.66
write-output $username			#ms_vmware
write-output $pass				#Hitachi1
write-output $lunid				#10
write-output "---------------------"

Write-Host "Adding PSS Snapin..."
add-pssnapin Hitachi.Storage.Management.Powershell2.Admin
Write-Host "Adding Storage..."
Add-StorageDevice -s $serial -u $username -p $pass -ip $storageip
Write-Host "Getting LU..."
Get-LU -s $serial -LogicalUnitId $lunid | fl
Write-Host "Your script executed successfully!"