"""Generate realistic, neutral document names that don't leak evidence information."""

import random
from datetime import datetime, timedelta
from typing import Dict, Any


class DocumentNameGenerator:
    """Generate realistic document names for on-chain storage."""
    
    # Prefixes by category (don't reveal evidence type)
    PREFIXES = {
        "technical": [
            "System_Report", "Technical_Log", "Network_Archive", "Server_Data",
            "Infrastructure_Doc", "Diagnostic_File", "Maintenance_Record",
            "Audit_Trail", "Performance_Log", "Security_Scan"
        ],
        "administrative": [
            "Internal_Memo", "Staff_Notice", "Department_Bulletin",
            "Management_Brief", "Policy_Update", "Committee_Minutes",
            "Directive", "Circular", "Announcement", "Briefing"
        ],
        "personal": [
            "Private_Journal", "Personal_Notes", "Daily_Log", "Diary_Entry",
            "Correspondence", "Letter", "Message", "Communication"
        ],
        "operational": [
            "Operations_Report", "Field_Notes", "Activity_Log", "Status_Update",
            "Incident_Report", "Case_File", "Investigation_Doc", "Evidence_Log"
        ],
        "surveillance": [
            "Camera_Feed", "Monitoring_Data", "Observation_Log", "Surveillance_Archive",
            "Security_Footage", "Tracking_Data", "Watch_Report"
        ],
        "generic": [
            "Document", "File", "Record", "Archive", "Data", "Report",
            "Log", "Entry", "Item", "Asset"
        ]
    }
    
    # All documents are JSON - no fake extensions
    EXTENSION = "json"
    
    def __init__(self):
        self.used_names = set()
    
    def generate_name(
        self,
        doc_type: str,
        doc_id: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate a realistic document name that reveals nothing about evidence type.
        
        Args:
            doc_type: Internal document type (e.g., "badge_log", "email", "diary")
            doc_id: Internal document ID
            context: Optional context (conspiracy name, date, etc.)
        
        Returns:
            Realistic document name like "System_Report_2024_11_23_7F3A.txt"
        """
        context = context or {}
        
        # Choose category based on doc_type (but don't reveal it)
        category = self._map_type_to_category(doc_type)
        
        # Generate components
        prefix = random.choice(self.PREFIXES[category])
        date_str = self._generate_date_string()
        identifier = self._generate_identifier()
        
        # Build name (always .json since all docs are JSON)
        name = f"{prefix}_{date_str}_{identifier}.json"
        
        # Ensure uniqueness
        while name in self.used_names:
            identifier = self._generate_identifier()
            name = f"{prefix}_{date_str}_{identifier}.json"
        
        self.used_names.add(name)
        return name
    
    def _map_type_to_category(self, doc_type: str) -> str:
        """Map internal doc type to a neutral category."""
        # Technical/system logs
        if any(t in doc_type for t in [
            "log", "firewall", "network", "server", "vpn", "access_control",
            "badge", "door", "device", "asset", "inventory", "scan"
        ]):
            return "technical"
        
        # Personal documents
        if any(t in doc_type for t in ["diary", "journal", "personal"]):
            return "personal"
        
        # Administrative
        if any(t in doc_type for t in ["memo", "email", "notice", "bulletin"]):
            return "administrative"
        
        # Surveillance/monitoring
        if any(t in doc_type for t in ["camera", "surveillance", "photo", "video"]):
            return "surveillance"
        
        # Operational
        if any(t in doc_type for t in ["report", "statement", "witness", "police"]):
            return "operational"
        
        # Default
        return "generic"
    
    def _generate_date_string(self) -> str:
        """Generate a realistic date string."""
        # Random date within last 2 years
        days_ago = random.randint(0, 730)
        date = datetime.now() - timedelta(days=days_ago)
        
        # Multiple formats
        formats = [
            date.strftime("%Y_%m_%d"),      # 2024_11_23
            date.strftime("%Y%m%d"),        # 20241123
            date.strftime("%d%b%Y").upper(), # 23NOV2024
            date.strftime("%Y_Q%q"),        # 2024_Q4 (custom)
        ]
        
        return random.choice(formats)
    
    def _generate_identifier(self) -> str:
        """Generate a random identifier (looks like hash/code)."""
        # Various formats
        formats = [
            lambda: f"{random.randint(1000, 9999)}",  # 7F3A
            lambda: f"{''.join(random.choices('ABCDEF0123456789', k=4))}",  # 7F3A
            lambda: f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))}{random.randint(10, 99)}",  # XZ42
            lambda: f"{random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])}{random.randint(100, 999)}",  # A742
        ]
        
        return random.choice(formats)()
    
    
    def generate_batch(
        self,
        assignments: list,
        context: Dict[str, Any] = None
    ) -> Dict[str, str]:
        """
        Generate names for a batch of documents.
        
        Returns:
            Dict mapping doc_id -> document_name
        """
        mapping = {}
        for assignment in assignments:
            doc_id = assignment.document_id
            doc_type = assignment.document_type
            name = self.generate_name(doc_type, doc_id, context)
            mapping[doc_id] = name
        
        return mapping

