"""
Job ID Value Object

Represents a unique identifier for a scheduled job.
This is an immutable value object that encapsulates validation logic.
"""

from __future__ import annotations
from dataclasses import dataclass
import uuid
import re


@dataclass(frozen=True)
class JobId:
    """
    Job ID Value Object
    
    Immutable value object representing a unique job identifier.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the job ID after initialization"""
        if not self.value:
            raise ValueError("Job ID cannot be empty")
        
        # Validate UUID format
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {self.value}")
    
    @classmethod
    def generate(cls) -> JobId:
        """Generate a new unique job ID"""
        return cls(str(uuid.uuid4()))
    
    @classmethod
    def from_string(cls, value: str) -> JobId:
        """Create JobId from string"""
        return cls(value)
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"JobId('{self.value}')"


@dataclass(frozen=True)
class JobName:
    """
    Job Name Value Object
    
    Immutable value object representing a job name with validation.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the job name after initialization"""
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Job name cannot be empty")
        
        if len(self.value) > 120:
            raise ValueError("Job name cannot exceed 120 characters")
        
        # Allow alphanumeric, underscore, hyphen, and dot
        if not re.match(r'^[a-zA-Z0-9_.-]+$', self.value):
            raise ValueError("Job name can only contain alphanumeric characters, underscore, hyphen, and dot")
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"JobName('{self.value}')"


@dataclass(frozen=True)
class CronExpression:
    """
    Cron Expression Value Object
    
    Immutable value object representing a cron expression with validation.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the cron expression after initialization"""
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Cron expression cannot be empty")
        
        if len(self.value) > 64:
            raise ValueError("Cron expression cannot exceed 64 characters")
        
        # Basic cron validation (5 fields: minute hour day month weekday)
        parts = self.value.strip().split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have exactly 5 fields: minute hour day month weekday")
        
        # Validate each field
        for i, part in enumerate(parts):
            if not self._is_valid_cron_field(part, i):
                raise ValueError(f"Invalid cron field at position {i}: {part}")
    
    def _is_valid_cron_field(self, field: str, position: int) -> bool:
        """Validate a single cron field"""
        # Allow *, numbers, ranges, lists, and step values
        pattern = r'^(\*|(\d+(-\d+)?)(,\d+(-\d+)?)*)(/\d+)?$'
        return bool(re.match(pattern, field))
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"CronExpression('{self.value}')"
