from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_sk import CaseDetails

def _get_case_analysis_prompt(case_details: "CaseDetails") -> str:
    return f"""
    You are a helpful assistant. Your task is to help me analyze the following case:
    Title: {case_details.title}
    Description: {case_details.description}
    Files: {', '.join(file.filename for file in case_details.files)}

    # Guidelines:
    - Use Bahasa Indonesia for all response.
    - Summarize the key points of the case.
    - Identify potential fraud indicators.
    - Classify the case into appropriate categories.
    - Conduct analysis using the following approach:
      * Data Review: Correlate evidence, identify patterns.
      * Root Cause Analysis: Determine how and why the incident occurred.
      * Hypothesis Testing: Validate findings against initial assumptions.
    - Suggest next steps for investigation.
    - Provide your analysis in a clear and concise manner.
    - Use markdown formatting for better readability.
    - For all analysis sections (data_review, root_cause_analysis, hypothesis_testing): Use bullet points with proper markdown (each line starts with "- ").
    - Each bullet point should be on a NEW LINE (not escaped, actual line breaks).
    - Use markdown bold (**text**) for emphasis where appropriate.
    - Deepen your analysis by referencing the content of the files provided.
    - Ensure your response is well-structured and easy to follow.
    - Create insights based on the case details and file contents.
    - Provide actionable recommendations for further action based on the analysis.
    - Analyze applicable Indonesian laws (UU Indonesia) related to the case.
    - Identify potential legal violations and their corresponding articles in relevant laws.
    - Assess the legal impact and implications based on Indonesian legal framework.

    # Case Classification Categories:
    1. Financial & Cyber Crimes: Fraud/Financial Scam, Money Laundering, Bribery & Corruption, Cybercrime/Hacking, Identity Theft/Phishing
    2. People-Related Cases: Missing Persons, Human Trafficking, Kidnapping/Abduction, Harassment/Threats, Domestic Violence
    3. Property & Physical Crimes: Theft/Burglary, Robbery/Armed Assault, Vandalism/Property Damage, Arson
    4. Serious & Violent Crimes: Homicide/Murder, Assault/Attempted Murder, Sexual Offense/Abuse, Terrorism-Related Activity
    5. Digital & Data Crimes: Data Breach/Information Leak, Online Scams/Fake Identity, Cyberbullying/Online Harassment, Digital Evidence Tampering
    6. Organizational & Administrative Cases: Internal Misconduct/Policy Violation, Public Sector Corruption, Whistleblower Investigation, Compliance Breach/Regulatory Violation
    7. Other & Cross-Domain: Environmental Crime, Health & Safety Violation, Narcotics/Drug-Related Case, Customs/Smuggling Case

    # Response Format:
    {{
        "case_main_category": <str>,
        "case_sub_category": <str>,
        "applicable_laws": [
            {{
                "law_name": <str>,
                "articles": <list of str>,
                "violation_description": <str>,
                "penalty_level": <str>
            }}
        ],
        "law_impact_analysis": <str>,
        "analysis": {{
            "data_review": <str>,
            "root_cause_analysis": <str>,
            "hypothesis_testing": <str>
        }},
        "insights": [string],
        "recommendations": [string]
    }}

    # Remember to:
    - Use Bahasa Indonesia for all response.
    - Base your analysis solely on the information provided.
    - Avoid making assumptions beyond the given data.
    - For case_main_category, use one of the 7 main categories listed above.
    - For case_sub_category, use the specific sub-category that best matches the case from the category you selected.
    - For applicable_laws field, identify and reference specific Indonesian laws (UU) that are relevant to the case.
    - Include specific article numbers and descriptions of how they apply to the case violations.
    - In law_impact_analysis, provide comprehensive assessment of legal implications, potential consequences, and jurisdiction considerations.
    - Ensure law_impact_analysis includes penalties, liability exposure, and procedural implications based on Indonesian legal framework.
    """

def _get_file_description_prompt(file_name: str, file_content: str, case_details: "CaseDetails") -> str:
    # Build file list from case details
    file_list = ', '.join([file.filename for file in case_details.files]) if case_details.files else "No files"
    
    return f"""
    You are a helpful assistant. Your task is to help me understand the content of the given file, by providing a concise description.

    # Guidelines:
    - Use Bahasa Indonesia for all response.
    - Focus on what the file is about.
    - Summarize the key points of the file in one paragraph.
    - <file> html tag is containing the file information.
    - <context> html tag is containing overview information about the case related to the file.
    - Ensure your response is clear and concise.
    - Consider the context of other files in the case when providing the description.
    - Classify the document based on its type and purpose.

    <file>
    File Name: {file_name}
    File Content: {file_content}
    </file>

    <context>
    Case Title: {case_details.title}
    Case Description: {case_details.description}
    Related Files in Case: {file_list}
    </context>

    # Document Classification Categories:
    - Chat: Conversation logs, messages, or communication records
    - Audit: Audit reports, internal audit findings, compliance reviews
    - Finance: Financial statements, invoices, ledgers, bank statements, financial reports
    - Memo: Internal memorandums, notes, informal communications
    - Other: Any document that doesn't fit the above categories

    # Response Format:
    {{
        "description": <str>,
        "classification": <str>
    }}

    # Remember to:
    - Use Bahasa Indonesia for all response.
    - Base your analysis solely on the information provided.
    - Avoid making assumptions beyond the given data.
    - Provide description in the context of the overall case.
    - For classification, use one of the following values: Chat, Audit, Finance, Memo, or Other.
    """

def _get_knowledge_graph_creation_prompt(case_details: "CaseDetails") -> str:
    return f"""
    You are a helpful assistant. Your task is to help me create a knowledge graph based on the following case:
    Title: {case_details.title}
    Description: {case_details.description}
    Files: {', '.join(file.filename for file in case_details.files)}

    # Guidelines:
    - Use Bahasa Indonesia for all response.
    - Identify key entities and their relationships from the case details.
    - Structure the knowledge graph in a clear and logical manner.
    - Extract entities as nodes (organizations, people, projects, documents, assets, amounts, motives, case categories).
    - Define relationships as edges with descriptive labels.
    - Ensure your response is well-structured and easy to follow.

    # Example:
    nodes = {{
        node1: {{ name: "Node 1" }},
        node2: {{ name: "Node 2" }},
        node3: {{ name: "Node 3" }},
        node4: {{ name: "Node 4" }},
    }}

    edges = {{
        edge1: {{ source: "node1", target: "node2", label: "1 Gbps" }},
        edge2: {{ source: "node2", target: "node3", label: "100 Mbps" }},
        edge3: {{ source: "node2", target: "node4", label: "100 Mbps" }},
    }}

    # Response Format:
    {{
        "nodes": <list of objects>,
        "edges": <list of objects>
    }}

    # Node Types to Extract:
    - Organizations/Companies (PT, Yayasan, BUMN)
    - People/Roles (Pejabat, Officials)
    - Projects/Assets (Proyek, Aset Negara)
    - Documents (Memo, Minutes, Reports)
    - Accounts/Financial (Rekening, Dana)
    - Amounts/Values (Rp amounts)
    - Motives/Reasons
    - Case Categories

    # Remember to:
    - Use Bahasa Indonesia for all response.
    - Base your analysis solely on the information provided.
    - Avoid making assumptions beyond the given data.
    - Generate meaningful node IDs (node1, node2, etc.) and edge IDs (edge1, edge2, etc.).
    - Provide clear, concise labels for edges that describe the relationship.
    - Include all significant entities and their interconnections.
    """