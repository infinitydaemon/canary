import subprocess
from opencanary.modules import CanaryService, FileSystemWatcher

class SynLogWatcher(FileSystemWatcher):
    """Custom log watcher for handling SYN scans."""
    def __init__(self, logger=None, logFile=None, ignore_localhost=False):
        super().__init__(fileName=logFile)
        self.logger = logger
        self.ignore_localhost = ignore_localhost

    def handleLines(self, lines=None):
        # ... (handling logic for log lines)

class CanaryPortscan(CanaryService):
    NAME = 'portscan'

    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)
        self.audit_file = config.getVal('portscan.logfile', default='/var/log/kern.log')
        self.synrate = int(config.getVal('portscan.synrate', default=5))
        self.nmaposrate = int(config.getVal('portscan.nmaposrate', default=5))
        self.lorate = int(config.getVal('portscan.lorate', default=3))
        self.listen_addr = config.getVal('device.listen_addr', default='')
        self.ignore_localhost = config.getVal('portscan.ignore_localhost', default=False)

    def _execute_iptables_rule(self, rule, rate_limit, prefix):
        """Execute iptables rule."""
        command = f'sudo /sbin/iptables -t mangle {rule} -j LOG --log-level=warning --log-prefix="{prefix}" -m limit --limit="{rate_limit}"'
        subprocess.run(command, shell=True, check=True)

    def setupIptablesRules(self, rule, rate_limit):
        self._execute_iptables_rule(f'-D PREROUTING {rule} -i lo', f'{rate_limit}/hour')
        self._execute_iptables_rule(f'-A PREROUTING {rule} -i lo', f'{rate_limit}/hour')
        self._execute_iptables_rule(f'-D PREROUTING {rule} --syn ! -i lo', f'{rate_limit}/second')
        self._execute_iptables_rule(f'-A PREROUTING {rule} --syn ! -i lo', f'{rate_limit}/second')

    def setupNmapRule(self, rule, rate_limit, prefix):
        self._execute_iptables_rule(f'-D PREROUTING {rule}', f'{rate_limit}/second', prefix)
        self._execute_iptables_rule(f'-A PREROUTING {rule}', f'{rate_limit}/second', prefix)

    def startYourEngines(self, reactor=None):
        self.setupIptablesRules('-p tcp', self.lorate)
        self.setupNmapRule('--tcp-flags ALL URG,PSH,SYN,FIN -m u32 --u32 "40=0x03030A01 && 44=0x02040109 && 48=0x080Affff && 52=0xffff0000 && 56=0x00000402"', self.nmaposrate, 'canarynmap: ')
        self.setupNmapRule('-p tcp -m u32 --u32 "6&0xFF=0x6 && 0>>22&0x3C@12=0x50000400"', self.nmaposrate, 'canarynmapNULL: ')
        self.setupNmapRule('-p tcp -m u32 --u32 "6&0xFF=0x6 && 0>>22&0x3C@12=0x50290400"', self.nmaposrate, 'canarynmapXMAS: ')
        self.setupNmapRule('-p tcp -m u32 --u32 "6&0xFF=0x6 && 0>>22&0x3C@12=0x50010400"', self.nmaposrate, 'canarynmapFIN: ')

        fs = SynLogWatcher(logFile=self.audit_file, logger=self.logger, ignore_localhost=self.ignore_localhost)
        fs.start()

    def configUpdated(self):
        pass
