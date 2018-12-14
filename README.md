# ShadowProtect Backup Email Processing and Dashboard

ShadowProtect is a great backup solution however determining what that status of all your backups can be a challenge.
What this project does is process all your ShadowProtect emails and generates a dashboard. 
In addition to telling you if a backup completed or failed it can detect whether a backup is an unkown state. 

Requirements
- Debian Linux Server 
- Postfix 
- Fetchmail
- MySQL 
- PHP
- Apache 

## Theory Of Operation
1. ShadowProtect sends out emails to a dedicated email account.
2. Fetchmail downloads the emails and forwards it locally to postfix.
3. Postfix process the email using a postfix filter/hook which copies the email into a text file stored in a directory.
4. A PHP script run via cron parses these backup report email's into a MySQL database.
5. Another PHP script run via cron determines the status of each backup job and generates a web based dashboard. 

