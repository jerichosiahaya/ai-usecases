"""
Script to insert dummy candidate data into CosmosDB with Azure AI embeddings
Run this script to populate the candidates container with sample data

Usage:
  cd C:\code\eyds-dev\solution-accelerators\ai-hris\server
  python insert_dummy_candidates.py
"""

import sys
import os
import asyncio
import uuid
from pathlib import Path

# Add the server directory to the path
server_dir = Path(__file__).parent
sys.path.insert(0, str(server_dir))

from src.config.env import AppConfig
from src.repository.database import CosmosDB
from src.repository.embedding import AzureAIEmbedding
from src.domain.candidate import Candidate
from datetime import datetime, timedelta
from loguru import logger

# Initialize configuration
config = AppConfig()
cosmosdb = CosmosDB(config=config)
embedding_service = AzureAIEmbedding(config=config)

# Load the candidates container
cosmosdb._load_container("candidates", "candidates")

# Helper function to generate unique candidate IDs
def generate_candidate_id():
    """Generate a unique candidate ID using UUID"""
    return str(uuid.uuid4())

def generate_documents(candidate_name: str, candidate_id: str):
    """Generate dummy documents with Azure Blob Storage URLs"""
    name_slug = candidate_name.lower().replace(" ", "_")
    current_date = datetime.utcnow().isoformat() + "Z"
    
    documents = []
    
    # RESUME document
    documents.append({
        "type": "RESUME",
        "name": f"resume_{name_slug}.pdf",
        "url": f"https://candidatesdocs.blob.core.windows.net/resumes/{candidate_id}/resume_{name_slug}.pdf",
        "lastUpdated": current_date,
        "extractedContent": {
            "text": f"RESUME - {candidate_name}\n\nProfessional Summary:\nExperienced professional with strong skills and track record of success.\n\nSkills:\n- Leadership\n- Project Management\n- Team Collaboration\n- Strategic Planning\n\nExperience:\n- Senior Role at Major Company (2020-Present)\n- Professional Role at Tech Startup (2018-2020)\n\nEducation:\n- Bachelor's Degree in relevant field",
            "tables": [],
            "boundingBoxes": [
                {"page": 1, "x": 0.1, "y": 0.1, "width": 0.8, "height": 0.2, "label": "header"},
                {"page": 1, "x": 0.1, "y": 0.3, "width": 0.8, "height": 0.6, "label": "content"}
            ]
        }
    })
    
    # KTP document
    documents.append({
        "type": "KTP",
        "name": f"ktp_{name_slug}.jpg",
        "url": f"https://candidatesdocs.blob.core.windows.net/ktp/{candidate_id}/ktp_{name_slug}.jpg",
        "lastUpdated": current_date,
        "extractedContent": {
            "text": f"KTP (Indonesian ID Card)\nNama: {candidate_name}\nNomor Identitas: 1234567890123456\nTanggal Lahir: 15-05-1992\nAlamat: Jl. Sample Street No. 123, Jakarta, Indonesia\nKota Asal: Jakarta\nPekerjaan: Professional\nStatus Perkawinan: Single",
            "tables": [
                {
                    "header": ["Field", "Value"],
                    "rows": [
                        ["Nama", candidate_name],
                        ["NIK", "1234567890123456"],
                        ["Tempat Lahir", "Jakarta"],
                        ["Tanggal Lahir", "15-05-1992"]
                    ]
                }
            ],
            "boundingBoxes": [
                {"page": 1, "x": 0.05, "y": 0.05, "width": 0.9, "height": 0.9, "label": "id_card"}
            ]
        }
    })
    
    # KARTU KELUARGA document
    documents.append({
        "type": "KARTU_KELUARGA",
        "name": f"kk_{name_slug}.jpg",
        "url": f"https://candidatesdocs.blob.core.windows.net/kartu-keluarga/{candidate_id}/kk_{name_slug}.jpg",
        "lastUpdated": current_date,
        "extractedContent": {
            "text": f"KARTU KELUARGA (Family Card)\nNomor Kartu Keluarga: 1234567890123456\nAlamat: Jl. Sample Street No. 123, Jakarta 12345, Indonesia\nKepala Keluarga: {candidate_name}\nJumlah Anggota Keluarga: 4 orang\n\nAnggota Keluarga:\n1. {candidate_name} - Kepala Keluarga - Pekerjaan\n2. Family Member 1 - Istri - Pekerjaan\n3. Family Member 2 - Anak - Pelajar\n4. Family Member 3 - Anak - Pelajar",
            "tables": [
                {
                    "header": ["No", "Nama", "Hubungan", "Pekerjaan"],
                    "rows": [
                        ["1", candidate_name, "Kepala Keluarga", "Professional"],
                        ["2", "Family Member 1", "Istri", "Professional"],
                        ["3", "Family Member 2", "Anak", "Pelajar"],
                        ["4", "Family Member 3", "Anak", "Pelajar"]
                    ]
                }
            ],
            "boundingBoxes": [
                {"page": 1, "x": 0.05, "y": 0.05, "width": 0.9, "height": 0.9, "label": "family_card"}
            ]
        }
    })
    
    # IJAZAH document
    documents.append({
        "type": "IJAZAH",
        "name": f"ijazah_{name_slug}.pdf",
        "url": f"https://candidatesdocs.blob.core.windows.net/ijazah/{candidate_id}/ijazah_{name_slug}.pdf",
        "lastUpdated": current_date,
        "extractedContent": {
            "text": f"IJAZAH (Diploma Certificate)\n\nDijelaskan bahwa:\n{candidate_name}\nNIM: 20160001\n\nTelah berhasil menyelesaikan pendidikan pada Program Studi Sarjana di Universitas kami.\n\nDengan Predikat: Cum Laude\nIPK: 3.80\n\nJudul Skripsi: 'Advanced Studies in Professional Development'\n\nDiberi pada tanggal: 20 November 2016\nDi: Jakarta\n\nRektor Universitas",
            "tables": [
                {
                    "header": ["Keterangan", "Detail"],
                    "rows": [
                        ["Nama Penerima", candidate_name],
                        ["NIM", "20160001"],
                        ["Program", "Sarjana"],
                        ["Predikat", "Cum Laude"],
                        ["IPK", "3.80"],
                        ["Tanggal Serah Terima", "20 November 2016"]
                    ]
                }
            ],
            "boundingBoxes": [
                {"page": 1, "x": 0.1, "y": 0.1, "width": 0.8, "height": 0.8, "label": "diploma"}
            ]
        }
    })
    
    return documents

# Sample candidate data (embeddings will be generated using Azure AI)
dummy_candidates = [
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Siti Nurhaliza",
        "email": "siti.nurhaliza@example.com",
        "phone": "+62-812-0101",
        "gender": "Female",
        "dateOfBirth": "1992-05-15",
        "position": "Product Designer I",
        "status": "applied",
        "appliedDate": (datetime.utcnow() - timedelta(days=5)).isoformat() + "Z",
        "experience": 8,
        "skills": ["Visual Design", "UX Research", "Figma", "Prototyping", "Design Systems"],
        "rating": 4.8,
        "notes": "Portofolio yang kuat dengan kemampuan desain visual dan riset pengguna yang luar biasa",
        "cvUrl": "https://example.com/resumes/siti_nurhaliza_cv.pdf",
        "profileSummary": "Siti Nurhaliza - Desainer Produk dengan 8 tahun pengalaman di desain visual dan riset UX",
        "education": [
            {
                "institution": "Institut Teknologi Bandung",
                "degree": "Sarjana",
                "fieldOfStudy": "Desain Grafis",
                "graduationYear": 2016,
                "gpa": 3.8
            }
        ],
        "workExperiences": [
            {
                "company": "Tokopedia",
                "position": "Senior Product Designer",
                "startDate": "2020-01-15",
                "endDate": None,
                "isCurrent": True,
                "description": "Memimpin tim desain produk untuk fitur marketplace dan payment gateway"
            },
            {
                "company": "Grab",
                "position": "Product Designer",
                "startDate": "2018-03-01",
                "endDate": "2019-12-31",
                "isCurrent": False,
                "description": "Mendesain interface pengguna untuk aplikasi mobile driver dan konsumen"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Budi Santoso",
        "email": "budi.santoso@example.com",
        "phone": "+62-812-0102",
        "gender": "Male",
        "dateOfBirth": "1988-12-22",
        "position": "Senior Engineer",
        "status": "reviewing",
        "appliedDate": (datetime.utcnow() - timedelta(days=7)).isoformat() + "Z",
        "experience": 5,
        "skills": ["JavaScript", "React", "Node.js", "AWS", "MongoDB"],
        "rating": 4.5,
        "notes": "Menyelesaikan 2 proyek sukses dengan kualitas kode yang sangat baik dan kolaborasi tim yang solid",
        "cvUrl": "https://example.com/resumes/budi_santoso_cv.pdf",
        "profileSummary": "Budi Santoso - Senior Engineer dengan 5 tahun pengalaman full-stack development",
        "education": [
            {
                "institution": "Universitas Indonesia",
                "degree": "Sarjana",
                "fieldOfStudy": "Teknik Informatika",
                "graduationYear": 2019,
                "gpa": 3.7
            }
        ],
        "workExperiences": [
            {
                "company": "Gojek",
                "position": "Backend Engineer",
                "startDate": "2021-06-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Mengembangkan microservices untuk platform logistics dan payment"
            },
            {
                "company": "Bukalapak",
                "position": "Full Stack Developer",
                "startDate": "2019-08-01",
                "endDate": "2021-05-31",
                "isCurrent": False,
                "description": "Membangun fitur e-commerce dan API integration dengan payment gateway"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Carla Wijaya",
        "email": "carla.wijaya@example.com",
        "phone": "+62-812-0103",
        "gender": "Female",
        "dateOfBirth": "1990-03-08",
        "position": "Product Manager",
        "status": "shortlisted",
        "appliedDate": (datetime.utcnow() - timedelta(days=10)).isoformat() + "Z",
        "experience": 7,
        "skills": ["Product Strategy", "Analytics", "Roadmapping", "Stakeholder Management", "Agile"],
        "rating": 4.9,
        "notes": "Latar belakang strategi produk yang sangat baik dengan track record memimpin tim lintas fungsi",
        "cvUrl": "https://example.com/resumes/carla_wijaya_cv.pdf",
        "profileSummary": "Carla Wijaya - Product Manager dengan 7 tahun pengalaman strategi produk dan kepemimpinan",
        "education": [
            {
                "institution": "BINUS University",
                "degree": "Magister",
                "fieldOfStudy": "Manajemen Bisnis",
                "graduationYear": 2017,
                "gpa": 3.9
            }
        ],
        "workExperiences": [
            {
                "company": "Blibli",
                "position": "Senior Product Manager",
                "startDate": "2021-02-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Memimpin product roadmap untuk kategori fashion dan lifestyle"
            },
            {
                "company": "OVO",
                "position": "Product Manager",
                "startDate": "2018-11-01",
                "endDate": "2021-01-31",
                "isCurrent": False,
                "description": "Mengelola produk digital wallet dan payment solutions"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Dimas Pratama",
        "email": "dimas.pratama@example.com",
        "phone": "+62-812-0104",
        "gender": "Male",
        "dateOfBirth": "1995-07-14",
        "position": "DevOps Engineer",
        "status": "hired",
        "appliedDate": (datetime.utcnow() - timedelta(days=15)).isoformat() + "Z",
        "experience": 6,
        "skills": ["Kubernetes", "Docker", "CI/CD", "Terraform", "AWS"],
        "rating": 4.7,
        "notes": "Pengalaman otomasi infrastruktur yang kuat dengan keahlian platform cloud yang proven",
        "cvUrl": "https://example.com/resumes/dimas_pratama_cv.pdf",
        "profileSummary": "Dimas Pratama - DevOps Engineer dengan 6 tahun pengalaman infrastruktur dan otomasi",
        "education": [
            {
                "institution": "Politeknik Negeri Bandung",
                "degree": "Diploma",
                "fieldOfStudy": "Teknik Komputer dan Jaringan",
                "graduationYear": 2018,
                "gpa": 3.6
            }
        ],
        "workExperiences": [
            {
                "company": "Shopify",
                "position": "DevOps Engineer",
                "startDate": "2020-05-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Mengelola infrastruktur cloud dan CI/CD pipeline untuk aplikasi e-commerce"
            },
            {
                "company": "Traveloka",
                "position": "Infrastructure Engineer",
                "startDate": "2018-09-01",
                "endDate": "2020-04-30",
                "isCurrent": False,
                "description": "Setup dan maintenance Kubernetes cluster dan Docker containerization"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Eka Putri",
        "email": "eka.putri@example.com",
        "phone": "+62-812-0105",
        "gender": "Female",
        "dateOfBirth": "2001-09-10",
        "position": "Frontend Developer",
        "status": "rejected",
        "appliedDate": (datetime.utcnow() - timedelta(days=13)).isoformat() + "Z",
        "experience": 2,
        "skills": ["React", "CSS", "HTML", "JavaScript", "Vue.js"],
        "rating": 3.2,
        "notes": "Pengalaman terbatas di teknologi yang dibutuhkan - rekomendasikan untuk role entry-level",
        "cvUrl": "https://example.com/resumes/eka_putri_cv.pdf",
        "profileSummary": "Eka Putri - Junior Frontend Developer dengan 2 tahun pengalaman React dan CSS",
        "education": [
            {
                "institution": "Universitas Gunadarma",
                "degree": "Sarjana",
                "fieldOfStudy": "Sistem Informasi",
                "graduationYear": 2022,
                "gpa": 3.3
            }
        ],
        "workExperiences": [
            {
                "company": "Startup XYZ",
                "position": "Junior Frontend Developer",
                "startDate": "2023-01-15",
                "endDate": None,
                "isCurrent": True,
                "description": "Mengembangkan komponen React untuk aplikasi web startup"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Fajar Rahman",
        "email": "fajar.rahman@example.com",
        "phone": "+62-812-0106",
        "gender": "Male",
        "dateOfBirth": "1993-11-28",
        "position": "Data Scientist",
        "status": "applied",
        "appliedDate": (datetime.utcnow() - timedelta(days=3)).isoformat() + "Z",
        "experience": 4,
        "skills": ["Python", "Machine Learning", "Statistical Analysis", "SQL", "Data Visualization"],
        "rating": 4.6,
        "notes": "Latar belakang statistik yang kuat dengan pengalaman proyek ML yang relevan dari startup",
        "cvUrl": "https://example.com/resumes/fajar_rahman_cv.pdf",
        "profileSummary": "Fajar Rahman - Data Scientist dengan 4 tahun pengalaman machine learning dan analytics",
        "education": [
            {
                "institution": "Institut Pertanian Bogor",
                "degree": "Magister",
                "fieldOfStudy": "Statistika Terapan",
                "graduationYear": 2020,
                "gpa": 3.85
            }
        ],
        "workExperiences": [
            {
                "company": "PT. Data Analytics Indonesia",
                "position": "Senior Data Scientist",
                "startDate": "2021-03-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Mengembangkan model machine learning untuk predictive analytics dan recommendation engine"
            },
            {
                "company": "Tech Startup ABC",
                "position": "Data Analyst",
                "startDate": "2020-06-01",
                "endDate": "2021-02-28",
                "isCurrent": False,
                "description": "Analisis data dan business intelligence untuk mobile app"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Gita Maharani",
        "email": "gita.maharani@example.com",
        "phone": "+62-812-0107",
        "gender": "Female",
        "dateOfBirth": "1996-02-19",
        "position": "UX Designer",
        "status": "reviewing",
        "appliedDate": (datetime.utcnow() - timedelta(days=8)).isoformat() + "Z",
        "experience": 5,
        "skills": ["Figma", "User Research", "Wireframing", "UI Design", "Design Thinking"],
        "rating": 4.4,
        "notes": "Portofolio desain yang kuat menunjukkan pendekatan user-centric dengan perhatian detail yang sempurna",
        "cvUrl": "https://example.com/resumes/gita_maharani_cv.pdf",
        "profileSummary": "Gita Maharani - UX Designer dengan 5 tahun pengalaman riset pengguna dan desain",
        "education": [
            {
                "institution": "Universitas Negeri Jakarta",
                "degree": "Sarjana",
                "fieldOfStudy": "Desain Komunikasi Visual",
                "graduationYear": 2018,
                "gpa": 3.7
            }
        ],
        "workExperiences": [
            {
                "company": "PT. Digital Creative Studio",
                "position": "Lead UX Designer",
                "startDate": "2021-04-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Memimpin tim desain UX untuk aplikasi mobile dan web enterprise"
            },
            {
                "company": "Agency Design Pro",
                "position": "UI/UX Designer",
                "startDate": "2019-07-01",
                "endDate": "2021-03-31",
                "isCurrent": False,
                "description": "Design interface dan user experience untuk berbagai client korporat"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Hendra Kusuma",
        "email": "hendra.kusuma@example.com",
        "phone": "+62-812-0108",
        "gender": "Male",
        "dateOfBirth": "1991-06-05",
        "position": "QA Engineer",
        "status": "shortlisted",
        "appliedDate": (datetime.utcnow() - timedelta(days=11)).isoformat() + "Z",
        "experience": 6,
        "skills": ["Test Automation", "Selenium", "API Testing", "JIRA", "Performance Testing"],
        "rating": 4.5,
        "notes": "Pengalaman otomasi yang luas dengan tools testing modern dan identifikasi bug yang excellent",
        "cvUrl": "https://example.com/resumes/hendra_kusuma_cv.pdf",
        "profileSummary": "Hendra Kusuma - QA Engineer dengan 6 tahun pengalaman test automation dan quality assurance",
        "education": [
            {
                "institution": "Universitas Negeri Surabaya",
                "degree": "Sarjana",
                "fieldOfStudy": "Teknik Informatika",
                "graduationYear": 2017,
                "gpa": 3.6
            }
        ],
        "workExperiences": [
            {
                "company": "PT. Software Testing Solutions",
                "position": "Senior QA Engineer",
                "startDate": "2020-02-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Memimpin tim QA dan mengembangkan automation framework untuk testing"
            },
            {
                "company": "E-commerce Platform Corp",
                "position": "QA Automation Engineer",
                "startDate": "2018-05-01",
                "endDate": "2020-01-31",
                "isCurrent": False,
                "description": "Automation testing menggunakan Selenium dan API testing dengan Postman"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Ika Suwandi",
        "email": "ika.suwandi@example.com",
        "phone": "+62-812-0109",
        "gender": "Female",
        "dateOfBirth": "1998-04-20",
        "position": "HR Specialist",
        "status": "applied",
        "appliedDate": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
        "experience": 3,
        "skills": ["Recruitment", "HRIS", "Employee Relations", "Training", "HR Compliance"],
        "rating": 4.3,
        "notes": "Dasar-dasar HR yang solid dengan fokus kuat pada recruitment dan employee engagement",
        "cvUrl": "https://example.com/resumes/ika_suwandi_cv.pdf",
        "profileSummary": "Ika Suwandi - HR Specialist dengan 3 tahun pengalaman recruitment dan employee relations",
        "education": [
            {
                "institution": "Universitas Trisakti",
                "degree": "Sarjana",
                "fieldOfStudy": "Manajemen Sumber Daya Manusia",
                "graduationYear": 2021,
                "gpa": 3.65
            }
        ],
        "workExperiences": [
            {
                "company": "PT. Human Resources Consulting",
                "position": "HR Specialist",
                "startDate": "2022-01-15",
                "endDate": None,
                "isCurrent": True,
                "description": "Menangani recruitment, onboarding, dan employee relations untuk corporate client"
            },
            {
                "company": "Korporat ABC Indonesia",
                "position": "HR Executive",
                "startDate": "2021-07-01",
                "endDate": "2022-01-14",
                "isCurrent": False,
                "description": "Recruitment dan employee engagement activities"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    },
    {
        "id": generate_candidate_id(),
        "candidateId": generate_candidate_id(),
        "name": "Joko Hardianto",
        "email": "joko.hardianto@example.com",
        "phone": "+62-812-0110",
        "gender": "Male",
        "dateOfBirth": "1989-10-12",
        "position": "Business Analyst",
        "status": "reviewing",
        "appliedDate": (datetime.utcnow() - timedelta(days=6)).isoformat() + "Z",
        "experience": 7,
        "skills": ["Requirements Analysis", "SQL", "Excel", "Business Process", "Data Analysis"],
        "rating": 4.6,
        "notes": "Kemampuan analitik yang excellent dan skill komunikasi yang kuat dengan track record optimasi proses",
        "cvUrl": "https://example.com/resumes/joko_hardianto_cv.pdf",
        "profileSummary": "Joko Hardianto - Business Analyst dengan 7 tahun pengalaman analisis requirements dan process improvement",
        "education": [
            {
                "institution": "Universitas Bina Nusantara",
                "degree": "Sarjana",
                "fieldOfStudy": "Sistem Informasi",
                "graduationYear": 2017,
                "gpa": 3.75
            }
        ],
        "workExperiences": [
            {
                "company": "PT. Financial Services Indonesia",
                "position": "Senior Business Analyst",
                "startDate": "2021-08-01",
                "endDate": None,
                "isCurrent": True,
                "description": "Analisis requirement sistem dan process improvement untuk backend banking"
            },
            {
                "company": "Manufacturing Corp XYZ",
                "position": "Business Analyst",
                "startDate": "2018-03-01",
                "endDate": "2021-07-31",
                "isCurrent": False,
                "description": "Requirement gathering dan documentation untuk enterprise resource planning"
            }
        ],
        "documents": None  # Will be populated later in the insertion function
    }
]

def insert_dummy_candidates():
    """Insert dummy candidate data into CosmosDB with Azure AI embeddings"""
    try:
        container = cosmosdb.get_container("candidates")
        
        print("Starting to insert dummy candidate data with Azure AI embeddings...\n")
        
        for idx, candidate_data in enumerate(dummy_candidates, 1):
            try:
                # Generate embedding using Azure AI for the candidate profile summary
                profile_summary = candidate_data.get("profileSummary", "")
                print(f"[{idx}/{len(dummy_candidates)}] Generating embedding for {candidate_data['name']}...", end=" ", flush=True)
                
                embedding = asyncio.run(embedding_service.generate_query_embedding(profile_summary))
                
                if embedding:
                    candidate_data["embeddings"] = embedding
                    print(f"✓ Embedding generated ({len(embedding)} dimensions)")
                else:
                    print("⚠ Warning: Empty embedding, using fallback")
                    candidate_data["embeddings"] = [0.0] * 1536  # Azure default embedding size
                
                # Generate documents for the candidate
                candidate_data["documents"] = generate_documents(candidate_data["name"], candidate_data["candidateId"])
                print(f"  ✓ Generated {len(candidate_data['documents'])} documents (RESUME, KTP, KARTU_KELUARGA, IJAZAH)")
                
                # Create Candidate object from dict to validate
                candidate = Candidate(**candidate_data)
                
                # Insert into CosmosDB
                response = container.create_item(body=candidate_data)
                
                print(f"  ✓ Inserted: {candidate_data['name']} ({candidate_data['candidateId']}) - Status: {candidate_data['status']}\n")
                
            except Exception as e:
                print(f"\n  ✗ Failed to insert {candidate_data['name']}: {str(e)}\n")
                logger.error(f"Error inserting candidate {candidate_data['candidateId']}: {str(e)}")
        
        print(f"\n{'='*70}")
        print(f"✓ Successfully inserted {len(dummy_candidates)} dummy candidates with embeddings and documents!")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"Error connecting to CosmosDB: {str(e)}")
        logger.error(f"CosmosDB connection error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    insert_dummy_candidates()
