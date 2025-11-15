"""Programmatic clue fragmentation to enforce multi-hop reasoning."""

import re
import logging
from typing import List, Dict, Any
import random
import string


logger = logging.getLogger(__name__)


class ClueFragment:
    """A single atomic fragment of evidence."""
    def __init__(self, text: str, fragment_type: str, identifiers: Dict[str, str]):
        self.text = text
        self.fragment_type = fragment_type  # "action", "mapping", "identity"
        self.identifiers = identifiers  # e.g. {"user_id": "jsmith", "ip": "192.168.1.42"}


class ClueFragmenter:
    """
    Programmatically fragment clues to enforce multi-hop reasoning.
    
    Takes combined clues and splits them into atomic pieces that MUST be
    connected across multiple documents.
    """
    
    def __init__(self):
        self.session_counter = 0
        self.request_counter = 0
        self.transaction_counter = 0
    
    def fragment_clue(self, clue_text: str) -> List[ClueFragment]:
        """
        Split a clue into atomic fragments with intermediate IDs.
        
        Example input: "User ID 'jsmith' accessed server from IP 192.168.1.42 at 2:30 AM"
        
        Output fragments:
        1. "IP address 192.168.1.42 connected to server at 2:30 AM"
        2. "Session #SID12345 originated from IP 192.168.1.42"
        3. "User ID 'jsmith' initiated session #SID12345 at 2:29 AM"
        
        Forces: IP → Session → User (multi-hop!)
        """
        logger.info(f"   🔪 Fragmenting clue: {clue_text[:80]}...")
        
        # Extract all identifiers from the clue
        identifiers = self._extract_identifiers(clue_text)
        
        # Check what types of identifiers we have
        has_user = "user_id" in identifiers
        has_ip = "ip" in identifiers
        has_badge = "badge" in identifiers
        has_device = "device_id" in identifiers
        has_employee_num = "employee_num" in identifiers
        has_time = "time" in identifiers
        has_action = self._extract_action(clue_text)
        
        fragments = []
        
        # SPECIAL CASE: HR/Directory links (multiple IDs in one statement)
        # Example: "user ID 'jsmith' assigned Device D-123 and Badge #456"
        if (has_user and (has_device or has_badge or has_employee_num)):
            # Count how many IDs we have
            id_count = sum([has_user, has_device, has_badge, has_employee_num])
            
            if id_count >= 3:
                logger.info(f"      🚨 MEGA-CLUE DETECTED: {id_count} identifiers in ONE clue!")
                logger.info(f"         This MUST be split into separate documents!")
                
                # Fragment 1: Device to intermediate ID
                if has_device:
                    asset_id = self._generate_transaction_id()  # Use as "asset record ID"
                    frag1_text = f"Asset record {asset_id}: Device ID '{identifiers['device_id']}' registered"
                    fragments.append(ClueFragment(
                        text=frag1_text,
                        fragment_type="evidence",
                        identifiers={"asset_id": asset_id, "device_id": identifiers["device_id"]}
                    ))
                    
                    # Fragment 2: Badge to same intermediate ID
                    if has_badge:
                        frag2_text = f"Asset record {asset_id} includes Badge #{identifiers['badge']}"
                        fragments.append(ClueFragment(
                            text=frag2_text,
                            fragment_type="mapping",
                            identifiers={"asset_id": asset_id, "badge": identifiers["badge"]}
                        ))
                    
                    # Fragment 3: User assigned to asset
                    frag3_text = f"User ID '{identifiers['user_id']}' assigned to asset record {asset_id}"
                    fragments.append(ClueFragment(
                        text=frag3_text,
                        fragment_type="identity",
                        identifiers={"user_id": identifiers["user_id"], "asset_id": asset_id}
                    ))
                    
                    # Fragment 4: Employee number (if present)
                    if has_employee_num:
                        frag4_text = f"Employee #{identifiers['employee_num']} has user ID '{identifiers['user_id']}'"
                        fragments.append(ClueFragment(
                            text=frag4_text,
                            fragment_type="identity",
                            identifiers={"employee_num": identifiers["employee_num"], "user_id": identifiers["user_id"]}
                        ))
                    
                    logger.info(f"      → Mega-clue split into {len(fragments)} fragments!")
                    return fragments
                
                elif has_badge and not has_device:
                    # Just user + badge + maybe employee num
                    # Use request ID as intermediate
                    req_id = self._generate_request_id()
                    
                    frag1_text = f"Badge #{identifiers['badge']} registered under access group {req_id}"
                    fragments.append(ClueFragment(
                        text=frag1_text,
                        fragment_type="evidence",
                        identifiers={"badge": identifiers["badge"], "request_id": req_id}
                    ))
                    
                    frag2_text = f"User ID '{identifiers['user_id']}' belongs to access group {req_id}"
                    fragments.append(ClueFragment(
                        text=frag2_text,
                        fragment_type="identity",
                        identifiers={"user_id": identifiers["user_id"], "request_id": req_id}
                    ))
                    
                    if has_employee_num:
                        frag3_text = f"Employee #{identifiers['employee_num']} has user ID '{identifiers['user_id']}'"
                        fragments.append(ClueFragment(
                            text=frag3_text,
                            fragment_type="identity",
                            identifiers={"employee_num": identifiers["employee_num"], "user_id": identifiers["user_id"]}
                        ))
                    
                    logger.info(f"      → Multi-ID clue split into {len(fragments)} fragments!")
                    return fragments
        
        # STRATEGY: If we have multiple identifiers, split them and add intermediate IDs
        if has_user and has_ip:
            # Generate intermediate session ID
            session_id = self._generate_session_id()
            
            # Fragment 1: Action with IP (no user!)
            if has_action:
                frag1_text = f"{identifiers['ip']} {has_action}"
                if has_time:
                    frag1_text += f" at {identifiers['time']}"
                fragments.append(ClueFragment(
                    text=frag1_text,
                    fragment_type="action",
                    identifiers={"ip": identifiers["ip"]}
                ))
            
            # Fragment 2: Session mapping to IP
            frag2_text = f"Session {session_id} originated from IP {identifiers['ip']}"
            fragments.append(ClueFragment(
                text=frag2_text,
                fragment_type="mapping",
                identifiers={"session_id": session_id, "ip": identifiers["ip"]}
            ))
            
            # Fragment 3: User initiated session (no IP!)
            time_adjusted = self._adjust_time(identifiers.get("time", ""), -1)  # 1 min earlier
            frag3_text = f"User ID '{identifiers['user_id']}' initiated session {session_id}"
            if time_adjusted:
                frag3_text += f" at {time_adjusted}"
            fragments.append(ClueFragment(
                text=frag3_text,
                fragment_type="identity",
                identifiers={"user_id": identifiers["user_id"], "session_id": session_id}
            ))
            
            logger.info(f"      → Split into {len(fragments)} fragments (IP ← Session → User)")
            return fragments
        
        elif has_user and has_badge:
            # Split user and badge with intermediate identifier
            request_id = self._generate_request_id()
            
            # Fragment 1: Badge physical access
            if has_action:
                frag1_text = f"Badge #{identifiers['badge']} {has_action}"
                if has_time:
                    frag1_text += f" at {identifiers['time']}"
                fragments.append(ClueFragment(
                    text=frag1_text,
                    fragment_type="action",
                    identifiers={"badge": identifiers["badge"]}
                ))
            
            # Fragment 2: Request tied to badge
            frag2_text = f"Access request {request_id} authenticated via badge #{identifiers['badge']}"
            fragments.append(ClueFragment(
                text=frag2_text,
                fragment_type="mapping",
                identifiers={"request_id": request_id, "badge": identifiers["badge"]}
            ))
            
            # Fragment 3: User submitted request
            frag3_text = f"User ID '{identifiers['user_id']}' submitted access request {request_id}"
            fragments.append(ClueFragment(
                text=frag3_text,
                fragment_type="identity",
                identifiers={"user_id": identifiers["user_id"], "request_id": request_id}
            ))
            
            logger.info(f"      → Split into {len(fragments)} fragments (Badge ← Request → User)")
            return fragments
        
        elif has_user and has_action:
            # Even single user + action should be split
            # Use generic "system event" intermediate
            event_id = self._generate_transaction_id()
            
            # Fragment 1: Action happened (no user!)
            frag1_text = f"System event {event_id}: {has_action}"
            if has_time:
                frag1_text += f" at {identifiers['time']}"
            fragments.append(ClueFragment(
                text=frag1_text,
                fragment_type="action",
                identifiers={"event_id": event_id}
            ))
            
            # Fragment 2: User triggered event
            frag2_text = f"User ID '{identifiers['user_id']}' triggered system event {event_id}"
            fragments.append(ClueFragment(
                text=frag2_text,
                fragment_type="identity",
                identifiers={"user_id": identifiers["user_id"], "event_id": event_id}
            ))
            
            logger.info(f"      → Split into {len(fragments)} fragments (Event ← User)")
            return fragments
        
        else:
            # Single identifier or no split needed - keep as is but make it atomic
            logger.info(f"      → Kept as single fragment (atomic evidence)")
            return [ClueFragment(
                text=clue_text,
                fragment_type="evidence",
                identifiers=identifiers
            )]
    
    def _extract_identifiers(self, text: str) -> Dict[str, str]:
        """Extract all technical identifiers from text."""
        identifiers = {}
        text_lower = text.lower()
        
        # User IDs (patterns like: user ID 'jsmith', userid: mpatel, user 'lramirez')
        user_match = re.search(r"user\s*(?:id)?\s*['\"]([a-z][a-z0-9_]*)['\"]", text_lower)
        if user_match:
            identifiers["user_id"] = user_match.group(1)
        
        # IP addresses
        ip_match = re.search(r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b", text)
        if ip_match:
            identifiers["ip"] = ip_match.group(1)
        
        # Badge numbers
        badge_match = re.search(r"badge\s*#?(\d+)", text_lower)
        if badge_match:
            identifiers["badge"] = badge_match.group(1)
        
        # Times (HH:MM format or HH:MM AM/PM)
        time_match = re.search(r"(\d{1,2}:\d{2}(?:\s*[AP]M)?)", text)
        if time_match:
            identifiers["time"] = time_match.group(1)
        
        # Device IDs
        device_match = re.search(r"device\s*(?:id)?\s*['\"]?([A-Z0-9\-]+)['\"]?", text, re.IGNORECASE)
        if device_match:
            identifiers["device_id"] = device_match.group(1)
        
        # Employee numbers
        emp_match = re.search(r"employee\s*(?:number|#|num)?\s*[:\s]?(\d+)", text_lower)
        if emp_match:
            identifiers["employee_num"] = emp_match.group(1)
        
        return identifiers
    
    def _extract_action(self, text: str) -> str:
        """Extract the action verb from the clue."""
        text_lower = text.lower()
        
        # Common action verbs in mysteries
        actions = [
            "accessed", "deleted", "modified", "created", "uploaded", "downloaded",
            "logged in", "logged out", "executed", "initiated", "approved", "rejected",
            "scanned", "entered", "exited", "opened", "closed", "sent", "received"
        ]
        
        for action in actions:
            if action in text_lower:
                # Extract context around the action
                idx = text_lower.index(action)
                # Get some context after the action
                context_end = min(idx + len(action) + 50, len(text))
                action_context = text[idx:context_end]
                return action_context
        
        return ""
    
    def _adjust_time(self, time_str: str, minutes_offset: int) -> str:
        """Adjust time by minutes (for creating slightly different timestamps)."""
        if not time_str:
            return ""
        
        # Simple time adjustment (just for demo - doesn't handle edge cases)
        match = re.match(r"(\d{1,2}):(\d{2})(\s*[AP]M)?", time_str)
        if match:
            hours = int(match.group(1))
            mins = int(match.group(2))
            suffix = match.group(3) or ""
            
            mins += minutes_offset
            if mins < 0:
                mins += 60
                hours -= 1
            elif mins >= 60:
                mins -= 60
                hours += 1
            
            if hours < 1:
                hours = 12
            elif hours > 12 and suffix:
                hours -= 12
            
            return f"{hours}:{mins:02d}{suffix}"
        
        return time_str
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        self.session_counter += 1
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"SID{random_part}"
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        self.request_counter += 1
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"REQ{random_part}"
    
    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        self.transaction_counter += 1
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"TXN{random_part}"

