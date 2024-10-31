import re
from opencanary.modules import CanaryService, FileSystemWatcher
from opencanary.config import ConfigException

class SambaLogWatcher(FileSystemWatcher):
    def __init__(self, log_file=None, logger=None):
        super().__init__(fileName=log_file)
        self.logger = logger

    def handleLines(self, lines=None):
        """Process lines from the log file and extract relevant audit information."""
        audit_pattern = re.compile(r'^.*smbd_audit:.*$')

        for line in lines:
            if not audit_pattern.match(line):
                continue

            try:
                data = self.extract_smb_data(line)
                if data:
                    self.log_smb_data(data)
            except IndexError as e:
                self.logger.error(f"Error parsing SMB data: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error while processing line: {e}")

    def extract_smb_data(self, line):
        """Extract SMB data fields from a log line."""
        parts = line.split('smbd_audit:', 1)[-1].strip().split('|')

        # Ensure all expected fields are present to avoid IndexError
        if len(parts) < 13:
            raise IndexError("Log line does not contain the required number of fields.")

        return {
            'USER': parts[0] or "anonymous",
            'SRC_HOST': parts[1],
            'DST_HOST': parts[2],
            'SRC_HOST_NAME': parts[3],
            'SHARE_NAME': parts[4],
            'DST_HOST_NAME': parts[5],
            'SMB_VERSION': parts[6],
            'SMB_ARCH': parts[7],
            'DOMAIN_NAME': parts[9],
            'AUDIT_ACTION': parts[10],
            'AUDIT_STATUS': parts[11],
            'PATH': parts[12]
        }

    def log_smb_data(self, data):
        """Log the extracted SMB data with a structured log entry."""
        log_entry = {
            'src_host': data['SRC_HOST'],
            'src_port': '-1',  # Default value; actual port could be added if available
            'dst_host': data['DST_HOST'],
            'dst_port': 445,   # SMB default port
            'logtype': self.logger.LOG_SMB_FILE_OPEN,
            'logdata': {
                'USER': data['USER'],
                'REMOTENAME': data['SRC_HOST_NAME'],
                'SHARENAME': data['SHARE_NAME'],
                'LOCALNAME': data['DST_HOST_NAME'],
                'SMBVER': data['SMB_VERSION'],
                'SMBARCH': data['SMB_ARCH'],
                'DOMAIN': data['DOMAIN_NAME'],
                'AUDITACTION': data['AUDIT_ACTION'],
                'STATUS': data['AUDIT_STATUS'],
                'FILENAME': data['PATH']
            }
        }
        self.logger.log(log_entry)

class CanarySamba(CanaryService):
    NAME = 'smb'

    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)
        self.audit_file = config.getVal('smb.auditfile', default='/var/log/samba-audit.log')

    def startYourEngines(self, reactor=None):
        """Initialize and start the log watcher for SMB audit logs."""
        try:
            fs = SambaLogWatcher(log_file=self.audit_file, logger=self.logger)
            fs.start()
        except ConfigException as e:
            self.logger.error(f"Configuration error starting Samba log watcher: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error starting Samba log watcher: {e}")
