"""
Security Logger Module
======================
Logs security events for monitoring and auditing
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

class SecurityLogger:
    """Logs security events with structured format."""
    
    def __init__(self, log_dir: str = "logs/security"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
        
        log_file = self.log_dir / f"security_{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_event(self, event_type: str, client_id: str, action: str, 
                  details: Optional[dict] = None, severity: str = "INFO"):
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "client_id": client_id,
            "action": action,
            "severity": severity,
            "details": details or {}
        }
        
        message = f"{event_type} | {client_id} | {action}"
        
        if severity == "WARNING":
            self.logger.warning(message)
        elif severity == "ERROR":
            self.logger.error(message)
        else:
            self.logger.info(message)
        
        json_log_file = self.log_dir / f"security_events_{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(json_log_file, 'a') as f:
            f.write(json.dumps(event) + chr(10))
    
    def log_auth_attempt(self, client_id: str, success: bool, method: str = "API_KEY"):
        self.log_event(
            event_type="AUTH",
            client_id=client_id,
            action=f"Login {'successful' if success else 'failed'}",
            details={"method": method, "success": success},
            severity="WARNING" if not success else "INFO"
        )
    
    def log_rate_limit(self, client_id: str, requests: int, limit: int):
        self.log_event(
            event_type="RATE_LIMIT",
            client_id=client_id,
            action="Rate limit exceeded",
            details={"requests": requests, "limit": limit},
            severity="WARNING"
        )
    
    def log_injection_attempt(self, client_id: str, prompt: str, detected_patterns: list):
        self.log_event(
            event_type="INJECTION",
            client_id=client_id,
            action="Prompt injection detected",
            details={
                "prompt_length": len(prompt),
                "patterns_detected": detected_patterns
            },
            severity="ERROR"
        )
    
    def log_vulnerability(self, client_id: str, vulnerability_type: str, details: dict):
        self.log_event(
            event_type="VULNERABILITY",
            client_id=client_id,
            action=f"Potential {vulnerability_type} detected",
            details=details,
            severity="ERROR"
        )

_security_logger = None

def get_security_logger() -> SecurityLogger:
    global _security_logger
    if _security_logger is None:
        _security_logger = SecurityLogger()
    return _security_logger
