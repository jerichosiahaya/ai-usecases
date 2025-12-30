-- CosmosDB SQL Script: Insert Dummy Candidate Data
-- This script inserts sample candidate data into the candidates container
-- CosmosDB uses SQL INSERT syntax but the data is stored as JSON documents

-- Candidate 1: Applied Status
{
    "id": "cand-001",
    "candidateId": "cand-001",
    "name": "Alice Johnson",
    "email": "alice.johnson@example.com",
    "phone": "+1-555-0101",
    "position": "Senior Software Engineer",
    "status": "applied",
    "appliedDate": "2025-11-20T08:30:00Z",
    "experience": 8,
    "skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
    "rating": 4.8,
    "notes": "Strong technical background with leadership experience",
    "embeddings": [0.1, 0.2, 0.3, 0.4, 0.5]
}

-- Candidate 2: Reviewing Status
{
    "id": "cand-002",
    "candidateId": "cand-002",
    "name": "Bob Smith",
    "email": "bob.smith@example.com",
    "phone": "+1-555-0102",
    "position": "Full Stack Developer",
    "status": "reviewing",
    "appliedDate": "2025-11-18T14:15:00Z",
    "experience": 5,
    "skills": ["JavaScript", "Node.js", "MongoDB", "React", "AWS"],
    "rating": 4.5,
    "notes": "Good full-stack capabilities, completed 2 successful projects",
    "embeddings": [0.15, 0.25, 0.35, 0.45, 0.55]
}

-- Candidate 3: Shortlisted Status
{
    "id": "cand-003",
    "candidateId": "cand-003",
    "name": "Carol Williams",
    "email": "carol.williams@example.com",
    "phone": "+1-555-0103",
    "position": "Product Manager",
    "status": "shortlisted",
    "appliedDate": "2025-11-15T10:45:00Z",
    "experience": 7,
    "skills": ["Product Strategy", "Agile", "Analytics", "User Research", "Leadership"],
    "rating": 4.9,
    "notes": "Excellent product strategy skills and cross-functional team experience",
    "embeddings": [0.2, 0.3, 0.4, 0.5, 0.6]
}

-- Candidate 4: Hired Status
{
    "id": "cand-004",
    "candidateId": "cand-004",
    "name": "David Brown",
    "email": "david.brown@example.com",
    "phone": "+1-555-0104",
    "position": "DevOps Engineer",
    "status": "hired",
    "appliedDate": "2025-11-10T09:20:00Z",
    "experience": 6,
    "skills": ["Kubernetes", "Docker", "CI/CD", "AWS", "Python", "Terraform"],
    "rating": 4.7,
    "notes": "Strong DevOps background with proven track record in cloud infrastructure",
    "embeddings": [0.25, 0.35, 0.45, 0.55, 0.65]
}

-- Candidate 5: Rejected Status
{
    "id": "cand-005",
    "candidateId": "cand-005",
    "name": "Eva Martinez",
    "email": "eva.martinez@example.com",
    "phone": "+1-555-0105",
    "position": "Frontend Developer",
    "status": "rejected",
    "appliedDate": "2025-11-12T16:30:00Z",
    "experience": 2,
    "skills": ["React", "CSS", "HTML", "JavaScript"],
    "rating": 3.2,
    "notes": "Limited experience in required tech stack",
    "embeddings": [0.3, 0.4, 0.5, 0.6, 0.7]
}

-- Candidate 6: Applied Status - Data Scientist
{
    "id": "cand-006",
    "candidateId": "cand-006",
    "name": "Frank Wilson",
    "email": "frank.wilson@example.com",
    "phone": "+1-555-0106",
    "position": "Data Scientist",
    "status": "applied",
    "appliedDate": "2025-11-22T11:00:00Z",
    "experience": 4,
    "skills": ["Python", "Machine Learning", "TensorFlow", "SQL", "Tableau", "Statistics"],
    "rating": 4.6,
    "notes": "Strong statistical background with ML experience at startup",
    "embeddings": [0.35, 0.45, 0.55, 0.65, 0.75]
}

-- Candidate 7: Reviewing Status - UX Designer
{
    "id": "cand-007",
    "candidateId": "cand-007",
    "name": "Grace Lee",
    "email": "grace.lee@example.com",
    "phone": "+1-555-0107",
    "position": "UX Designer",
    "status": "reviewing",
    "appliedDate": "2025-11-17T13:45:00Z",
    "experience": 5,
    "skills": ["Figma", "User Research", "Prototyping", "UI Design", "Adobe XD"],
    "rating": 4.4,
    "notes": "Portfolio shows strong design sense and user-centric approach",
    "embeddings": [0.4, 0.5, 0.6, 0.7, 0.8]
}

-- Candidate 8: Shortlisted Status - QA Engineer
{
    "id": "cand-008",
    "candidateId": "cand-008",
    "name": "Henry Davis",
    "email": "henry.davis@example.com",
    "phone": "+1-555-0108",
    "position": "QA Engineer",
    "status": "shortlisted",
    "appliedDate": "2025-11-14T10:15:00Z",
    "experience": 6,
    "skills": ["Selenium", "Java", "Test Automation", "API Testing", "Jira"],
    "rating": 4.5,
    "notes": "Extensive test automation experience with modern tools",
    "embeddings": [0.45, 0.55, 0.65, 0.75, 0.85]
}

-- Candidate 9: Applied Status - HR Specialist
{
    "id": "cand-009",
    "candidateId": "cand-009",
    "name": "Iris Anderson",
    "email": "iris.anderson@example.com",
    "phone": "+1-555-0109",
    "position": "HR Specialist",
    "status": "applied",
    "appliedDate": "2025-11-23T09:30:00Z",
    "experience": 3,
    "skills": ["Recruitment", "Employee Relations", "HRIS", "Payroll", "Training"],
    "rating": 4.3,
    "notes": "Good HR fundamentals with focus on employee engagement",
    "embeddings": [0.5, 0.6, 0.7, 0.8, 0.9]
}

-- Candidate 10: Reviewing Status - Business Analyst
{
    "id": "cand-010",
    "candidateId": "cand-010",
    "name": "Jack Miller",
    "email": "jack.miller@example.com",
    "phone": "+1-555-0110",
    "position": "Business Analyst",
    "status": "reviewing",
    "appliedDate": "2025-11-19T15:20:00Z",
    "experience": 7,
    "skills": ["Requirements Gathering", "SQL", "Excel", "Process Improvement", "Communication"],
    "rating": 4.6,
    "notes": "Excellent analytical skills and strong communication abilities",
    "embeddings": [0.55, 0.65, 0.75, 0.85, 0.95]
}

-- ============================================
-- INSERT USING PYTHON SCRIPT (Recommended)
-- ============================================
-- Instead of running SQL directly, use the Python script below:
--
-- from azure.cosmos import CosmosClient
-- from datetime import datetime
-- 
-- # Initialize CosmosDB client
-- client = CosmosClient(endpoint, key)
-- database = client.get_database_client(database_name)
-- container = database.get_container_client("candidates")
-- 
-- candidates = [
--     {
--         "id": "cand-001",
--         "candidateId": "cand-001",
--         "name": "Alice Johnson",
--         "email": "alice.johnson@example.com",
--         "phone": "+1-555-0101",
--         "position": "Senior Software Engineer",
--         "status": "applied",
--         "appliedDate": "2025-11-20T08:30:00Z",
--         "experience": 8,
--         "skills": ["Python", "JavaScript", "React", "AWS", "Docker"],
--         "rating": 4.8,
--         "notes": "Strong technical background with leadership experience",
--         "embeddings": [0.1, 0.2, 0.3, 0.4, 0.5]
--     },
--     # ... more candidates ...
-- ]
-- 
-- for candidate in candidates:
--     container.create_item(body=candidate)
--
-- print("Dummy data inserted successfully!")
