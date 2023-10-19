import sys
from opencanary.modules import CanaryService, FileSystemWatcher
from opencanary.config import ConfigException

class SambaLogWatcher(FileSystemWatcher):
    def __init__(self, logFile=None, logger=None):
        super().__init__(fileName=logFile)
        self.logger = logger

    def handleLines(self, lines=None):
        audit_re = re.compile(r'^.*smbd_audit:.*$')

        for line in lines:
            matches = audit_re.match(line)

            if matches is None:
                continue

            data = self.extract_smb_data(line)
            self.log_smb_data(data)

    def extract_smb_data(self, line):
        data = {}
        parts = line.split('smbd_audit:', 1)[-1].strip().split('|')

        data['USER'] = parts[0] or "anonymous"
        data['SRC_HOST'] = parts[1]
        data['DST_HOST'] = parts[2]
        data['SRC_HOST_NAME'] = parts[3]
        data['SHARE_NAME'] = parts[4]
        data['DST_HOST_NAME'] = parts[5]
        data['SMB_VERSION'] = parts[6]
        data['SMB_ARCH'] = parts[7]
        data['DOMAIN_NAME'] = parts[9]
        data['AUDIT_ACTION'] = parts[10]
        data['AUDIT_STATUS'] = parts[11]
        data['PATH'] = parts[12]

        return data

    def log_smb_data(self, data):
        log_data = {
            'src_host': data['SRC_HOST'],
            'src_port': '-1',
            'dst_host': data['DST_HOST'],
            'dst_port': 445,
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
        self.logger.log(log_data)

class CanarySamba(CanaryService):
    NAME = 'smb'

    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)
        self.audit_file = config.getVal('smb.auditfile', default='/var/log/samba-audit.log')

    def startYourEngines(self, reactor=None):
        fs = SambaLogWatcher(logFile=self.audit_file, logger=self.logger)
        fs.start()
