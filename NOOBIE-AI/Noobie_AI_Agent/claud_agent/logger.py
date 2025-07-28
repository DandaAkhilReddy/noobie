"""
NOOBIE AI Logging System
=======================

Production-grade logging with colored console output, file rotation,
and structured JSON logging for Azure Application Insights.
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and emojis for console output"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    # Emoji indicators
    EMOJIS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '💥'
    }
    
    def format(self, record):
        # Add color and emoji
        level_name = record.levelname
        color = self.COLORS.get(level_name, self.COLORS['RESET'])
        emoji = self.EMOJIS.get(level_name, '📝')
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Create formatted message
        message = super().format(record)
        
        return f"[{timestamp}] {emoji} {color}{level_name}{self.COLORS['RESET']} - {record.name}:{record.funcName}:{record.lineno} - {message}"

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'module': record.module,
            'pathname': record.pathname
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry.update(record.extra_data)
        
        return json.dumps(log_entry, ensure_ascii=False)

class NoobieLogger:
    """NOOBIE AI Logger with advanced features"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.name = name
        self._handlers_configured = False
    
    def configure_handlers(self, 
                          log_level: str = "INFO",
                          enable_console: bool = True,
                          enable_file: bool = True,
                          log_file: Optional[str] = None):
        """Configure logging handlers"""
        
        if self._handlers_configured:
            return
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set log level
        numeric_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(numeric_level)
        
        # Console handler with colors
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(numeric_level)
            console_formatter = ColoredFormatter()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with JSON formatting
        if enable_file:
            # Create logs directory
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Use provided log file or default
            if not log_file:
                log_file = log_dir / f"noobie_{datetime.now().strftime('%Y-%m-%d')}.log"
            
            # Rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)  # Always DEBUG for files
            file_formatter = JSONFormatter()
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        self._handlers_configured = True
    
    def debug(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log debug message"""
        if extra_data:
            self.logger.debug(message, extra={'extra_data': extra_data})
        else:
            self.logger.debug(message)
    
    def info(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log info message"""
        if extra_data:
            self.logger.info(message, extra={'extra_data': extra_data})
        else:
            self.logger.info(message)
    
    def warning(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log warning message"""
        if extra_data:
            self.logger.warning(message, extra={'extra_data': extra_data})
        else:
            self.logger.warning(message)
    
    def error(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log error message"""
        if extra_data:
            self.logger.error(message, extra={'extra_data': extra_data})
        else:
            self.logger.error(message)
    
    def critical(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log critical message"""
        if extra_data:
            self.logger.critical(message, extra={'extra_data': extra_data})
        else:
            self.logger.critical(message)
    
    def exception(self, message: str, extra_data: Optional[Dict[str, Any]] = None):
        """Log exception with stack trace"""
        if extra_data:
            self.logger.exception(message, extra={'extra_data': extra_data})
        else:
            self.logger.exception(message)

# Global logger registry
_loggers: Dict[str, NoobieLogger] = {}

def get_logger(name: str) -> NoobieLogger:
    """Get or create a logger instance"""
    if name not in _loggers:
        _loggers[name] = NoobieLogger(name)
    return _loggers[name]

def setup_logging(log_level: str = "INFO",
                 enable_console: bool = True,
                 enable_file: bool = True,
                 log_file: Optional[str] = None) -> None:
    """Setup global logging configuration"""
    
    # Configure root logger
    root_logger = get_logger("noobie_ai")
    root_logger.configure_handlers(log_level, enable_console, enable_file, log_file)
    
    # Configure all existing loggers
    for logger in _loggers.values():
        logger.configure_handlers(log_level, enable_console, enable_file, log_file)
    
    root_logger.info(f"📋 Logging configured - Level: {log_level}, Console: {enable_console}, File: {enable_file}")

def log_execution_stats(stats: Dict[str, Any]) -> None:
    """Log execution statistics in structured format"""
    logger = get_logger("noobie_ai.stats")
    logger.info("📊 Execution Statistics", extra_data=stats)

def log_performance_metric(metric_name: str, value: float, unit: str = "") -> None:
    """Log performance metric"""
    logger = get_logger("noobie_ai.performance")
    logger.info(f"📈 {metric_name}: {value}{unit}", extra_data={
        'metric_name': metric_name,
        'value': value,
        'unit': unit,
        'timestamp': datetime.utcnow().isoformat()
    })

# Context manager for operation logging
class LogOperation:
    """Context manager for logging operation start/end with timing"""
    
    def __init__(self, operation_name: str, logger: Optional[NoobieLogger] = None):
        self.operation_name = operation_name
        self.logger = logger or get_logger("noobie_ai.operations")
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(f"🚀 Starting: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(f"❌ Failed: {self.operation_name} ({duration:.2f}s)", extra_data={
                'operation': self.operation_name,
                'duration_seconds': duration,
                'success': False,
                'error_type': exc_type.__name__ if exc_type else None,
                'error_message': str(exc_val) if exc_val else None
            })
        else:
            self.logger.info(f"✅ Completed: {self.operation_name} ({duration:.2f}s)", extra_data={
                'operation': self.operation_name,
                'duration_seconds': duration,
                'success': True
            })

# Export main functions
__all__ = [
    'get_logger',
    'setup_logging',
    'log_execution_stats',
    'log_performance_metric',
    'LogOperation',
    'NoobieLogger'
]