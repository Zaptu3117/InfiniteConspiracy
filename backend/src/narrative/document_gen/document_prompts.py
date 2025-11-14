"""Document generation prompt templates for all document types."""

# Email Template
EMAIL_PROMPT = """Write a realistic {tone} email.

AUTHOR: {author_name} ({author_role})
Background: {author_background}
Personality: {author_personality}

RECIPIENTS: {recipients}

CONTEXT FROM STORY:
{story_context}

TIMELINE CONTEXT:
What happened before this email:
{timeline_context}

DOCUMENTS TO REFERENCE (if natural):
{referenced_docs}

REQUIRED ELEMENTS (embed naturally in email body):
{clues_list}

TIMESTAMP: {timestamp}

INSTRUCTIONS:
- Write naturally as {author_name} would
- Use appropriate tone for the situation
- Do NOT make required elements obvious
- Include realistic details unrelated to mystery
- If referencing other documents, do so naturally

Output valid JSON:
{{
  "from": "{author_email}",
  "to": {recipients_json},
  "subject": "...",
  "body": "...",
  "timestamp": "{timestamp}"
}}"""

# Diary Template
DIARY_PROMPT = """Write a realistic personal diary entry.

AUTHOR: {author_name} ({author_role})
Background: {author_background}
Personality: {author_personality}

CONTEXT:
{story_context}

RECENT EVENTS:
{timeline_context}

REQUIRED ELEMENTS (embed naturally):
{clues_list}

DATE: {date}

INSTRUCTIONS:
- Write in first person as {author_name}
- Reflect personal thoughts and feelings
- Include mundane details along with important ones
- Do NOT make clues obvious
- Natural introspective tone

Output valid JSON:
{{
  "date": "{date}",
  "entry_text": "Dear diary,\\n...",
  "author": "{author_name}",
  "mood": "..."
}}"""

# Police Report Template
POLICE_REPORT_PROMPT = """Write an official police report.

REPORTING OFFICER: {officer_name}
INCIDENT DATE: {incident_date}

CONTEXT:
{story_context}

INCIDENT DETAILS:
{incident_details}

REQUIRED ELEMENTS (include in report):
{clues_list}

INSTRUCTIONS:
- Professional, formal tone
- Factual and objective
- Include case number, officer name, date
- List witnesses if applicable
- Document evidence found

Output valid JSON:
{{
  "case_number": "...",
  "officer": "{officer_name}",
  "date": "{incident_date}",
  "incident_description": "...",
  "witnesses": [...],
  "evidence_list": [...]
}}"""

# Badge Log Template
BADGE_LOG_PROMPT = """Generate a facility access log.

FACILITY: {facility_name}
LOG PERIOD: {log_period}

CONTEXT:
{story_context}

REQUIRED ACCESS ENTRIES (include these):
{clues_list}

INSTRUCTIONS:
- System-generated format
- Include badge number, name, timestamp, location
- Mix required entries with routine entries
- Chronological order
- Professional formatting

Output valid JSON:
{{
  "facility_name": "{facility_name}",
  "log_period": "{log_period}",
  "entries": [
    {{
      "badge_number": "...",
      "name": "...",
      "entry_time": "ISO timestamp",
      "location": "..."
    }}
  ]
}}"""

# Witness Statement Template
WITNESS_STATEMENT_PROMPT = """Write a witness statement.

WITNESS: {witness_name}
INTERVIEWING OFFICER: {officer_name}
DATE: {date}

WITNESS BACKGROUND:
{witness_background}

WHAT THEY WITNESSED:
{witnessed_events}

REQUIRED ELEMENTS (include in statement):
{clues_list}

INSTRUCTIONS:
- First-person account from witness
- Mix of clear recollection and uncertainty
- Natural speech patterns
- Include officer's questions
- Signed statement format

Output valid JSON:
{{
  "witness_name": "{witness_name}",
  "date": "{date}",
  "statement_text": "...",
  "officer": "{officer_name}",
  "signed": true
}}"""

# Bank Statement Template
BANK_STATEMENT_PROMPT = """Generate a bank account statement.

ACCOUNT HOLDER: {account_holder}
ACCOUNT NUMBER: {account_number}
PERIOD: {period}

REQUIRED TRANSACTIONS (include these):
{clues_list}

CONTEXT:
{story_context}

INSTRUCTIONS:
- Professional banking format
- Include opening/closing balance
- Transaction details: date, description, amount
- Mix required transactions with routine ones
- Realistic transaction descriptions

Output valid JSON:
{{
  "account_holder": "{account_holder}",
  "account_number": "{account_number}",
  "period": "{period}",
  "opening_balance": 0.00,
  "transactions": [
    {{"date": "...", "description": "...", "amount": 0.00, "balance": 0.00}}
  ],
  "closing_balance": 0.00
}}"""

# Newspaper Template
NEWSPAPER_PROMPT = """Write a newspaper article.

REPORTER: {reporter_name}
PUBLICATION: {publication_name}
DATE: {date}

ARTICLE TOPIC:
{article_topic}

CONTEXT:
{story_context}

REQUIRED ELEMENTS (include in article):
{clues_list}

INSTRUCTIONS:
- Journalistic style (inverted pyramid)
- Catchy headline
- Objective tone with quotes
- Include reporter byline
- Date and section

Output valid JSON:
{{
  "headline": "...",
  "date": "{date}",
  "content": "...",
  "reporter": "{reporter_name}",
  "section": "..."
}}"""

# Internal Memo Template
INTERNAL_MEMO_PROMPT = """Write an internal company memo.

FROM: {from_person} ({from_role})
TO: {to_person}
DATE: {date}
SUBJECT: {subject}

CONTEXT:
{story_context}

REQUIRED ELEMENTS (include in memo):
{clues_list}

INSTRUCTIONS:
- Professional business tone
- Standard memo format
- Concise and direct
- Include relevant details
- Optional classification level

Output valid JSON:
{{
  "from": "{from_person}",
  "to": "{to_person}",
  "date": "{date}",
  "subject": "{subject}",
  "content": "...",
  "classification": "..."
}}"""

# Phone Record Template
PHONE_RECORD_PROMPT = """Generate phone call logs.

PHONE NUMBER: {phone_number}
ACCOUNT HOLDER: {account_holder}
PERIOD: {period}

REQUIRED CALLS (include these):
{clues_list}

CONTEXT:
{story_context}

INSTRUCTIONS:
- System-generated format
- Include date, time, number called, duration
- Mix required calls with routine calls
- Chronological order

Output valid JSON:
{{
  "phone_number": "{phone_number}",
  "account_holder": "{account_holder}",
  "period": "{period}",
  "call_log": [
    {{"date": "...", "time": "...", "number": "...", "duration": "...", "type": "outgoing/incoming"}}
  ]
}}"""

# Receipt Template
RECEIPT_PROMPT = """Generate a purchase receipt.

MERCHANT: {merchant_name}
DATE: {date}
TIME: {time}

REQUIRED ITEMS (include these):
{clues_list}

CONTEXT:
{story_context}

INSTRUCTIONS:
- Standard receipt format
- Itemized list with prices
- Include merchant info, date, time
- Payment method
- Transaction ID

Output valid JSON:
{{
  "merchant": "{merchant_name}",
  "date": "{date}",
  "time": "{time}",
  "items": [
    {{"item": "...", "quantity": 1, "price": 0.00}}
  ],
  "total": 0.00,
  "payment_method": "...",
  "transaction_id": "..."
}}"""

# Surveillance Log Template
SURVEILLANCE_LOG_PROMPT = """Generate a security surveillance log.

LOCATION: {location}
DATE: {date}
OPERATOR: {operator}

REQUIRED OBSERVATIONS (include these):
{clues_list}

CONTEXT:
{story_context}

INSTRUCTIONS:
- Security professional tone
- Timestamped entries
- Objective observations
- Include camera IDs if applicable
- Notable events logged

Output valid JSON:
{{
  "location": "{location}",
  "date": "{date}",
  "operator": "{operator}",
  "entries": [
    {{"time": "...", "camera_id": "...", "observation": "...", "action_taken": "..."}}
  ]
}}"""

# Medical Record Template
MEDICAL_RECORD_PROMPT = """Generate a medical record.

PATIENT: {patient_name}
DOCTOR: {doctor_name}
DATE: {date}
PROCEDURE/VISIT: {visit_type}

REQUIRED MEDICAL DETAILS (include these):
{clues_list}

CONTEXT:
{story_context}

INSTRUCTIONS:
- Professional medical terminology
- HIPAA-compliant format
- Include diagnosis, treatment, medications
- Doctor's notes
- Timestamps

Output valid JSON:
{{
  "patient_name": "{patient_name}",
  "date": "{date}",
  "procedure_or_visit": "{visit_type}",
  "doctor": "{doctor_name}",
  "diagnosis": "...",
  "treatment": "...",
  "medications": [...],
  "notes": "..."
}}"""


# Mapping of document types to prompts
DOCUMENT_PROMPTS = {
    "email": EMAIL_PROMPT,
    "diary": DIARY_PROMPT,
    "police_report": POLICE_REPORT_PROMPT,
    "badge_log": BADGE_LOG_PROMPT,
    "witness_statement": WITNESS_STATEMENT_PROMPT,
    "bank_statement": BANK_STATEMENT_PROMPT,
    "newspaper": NEWSPAPER_PROMPT,
    "internal_memo": INTERNAL_MEMO_PROMPT,
    "phone_record": PHONE_RECORD_PROMPT,
    "receipt": RECEIPT_PROMPT,
    "surveillance_log": SURVEILLANCE_LOG_PROMPT,
    "medical_record": MEDICAL_RECORD_PROMPT
}


def get_document_prompt_template(doc_type: str) -> str:
    """
    Get prompt template for a document type.
    
    Args:
        doc_type: Type of document
    
    Returns:
        Prompt template string
    """
    return DOCUMENT_PROMPTS.get(doc_type, EMAIL_PROMPT)

