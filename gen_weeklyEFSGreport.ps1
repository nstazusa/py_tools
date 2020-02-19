################
#	Create by AST			2020-02-19
#	Export the Solawind ticket for weekly report purpose

# Local variables
$limit = (Get-Date).AddDays(-30)
$path = "D:\Reports\EFSG Outstanding Incident Summary"
$reportName = "EFSG Outstanding Incident Summary $((Get-Date).ToString("yyyy-MM-dd")).csv"
$smtpServer = "SNMP Server IP"
$senderName = "Sender e-mail"
$receiverName = "Receiver e-mail"

# Remove any file(s) older than 30 day in the dir
Get-ChildItem -Path $path -Recurse -Force | Where-Object { !$_.PSIsContainer -and $_.CreationTime -lt $limit } | Remove-Item -Force

# Generated the report 
sqlcmd -S 127.0.0.1  -i "D:\Generate ticket Report\3)EFSG Incident List.sql" -o "$path\$reportName" -W -w 9999  -s ","  -k -m 1 -f 65001

# Sent the report via e-mail 
Send-MailMessage -From $senderName -To $receiverName -Subject "[Weekly Report] $reportName" -Body "Please check the the report - $reportName in the attachment." -Attachments "$path\$reportName" -SmtpServer $smtpServer


