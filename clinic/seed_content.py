"""Synthetic reference content used by ``seed_demo_data``.

Every person, address, plan, and phone number here is fictional. Phone numbers
use the 555-01xx range reserved for fiction.
"""

import datetime

# ---------------------------------------------------------------------------
# Demo passwords (documented in USER-GUIDE.md)
# ---------------------------------------------------------------------------

PASSWORDS = {
    "patient": "Patient2026!",
    "front_office": "FrontDesk2026!",
    "doctor": "Doctor2026!",
    "ai_engineer": "AIEngineer2026!",
    "admin": "Admin2026!",
}

# ---------------------------------------------------------------------------
# Practice directory
# ---------------------------------------------------------------------------

SPECIALTIES = [
    ("family-medicine", "Family Medicine", "Comprehensive primary care for patients of every age, from preventive checkups to chronic disease management."),
    ("pediatrics", "Pediatrics", "Well-child visits, immunizations, sick visits, and developmental care from birth through age 18."),
    ("internal-medicine", "Internal Medicine", "Primary care for adults, with particular depth in complex and chronic conditions such as diabetes and heart disease."),
    ("dermatology", "Dermatology", "Diagnosis and treatment of skin, hair, and nail conditions, including skin cancer screening."),
    ("sports-medicine", "Sports Medicine", "Non-surgical care for sprains, strains, overuse injuries, and joint pain, with return-to-activity planning."),
    ("womens-health", "Women's Health", "Gynecologic care, contraception, prenatal care, and menopause management."),
]

INSURANCE_PLANS = [
    # code, name, carrier, plan type, member services phone
    ("silverpeak-ppo", "SilverPeak PPO", "SilverPeak Health", "PPO", "(800) 555-0141"),
    ("silverpeak-hmo", "SilverPeak HMO Select", "SilverPeak Health", "HMO", "(800) 555-0141"),
    ("canyon-mutual", "Canyon Mutual Choice PPO", "Canyon Mutual Insurance", "PPO", "(800) 555-0152"),
    ("lakeshore-epo", "Lakeshore Employers Health EPO", "Lakeshore Benefits Group", "EPO", "(800) 555-0163"),
    ("beehive-community", "Beehive Community Health Plan", "Beehive Community Health", "MCD", "(800) 555-0174"),
    ("redrock-advantage", "Redrock Medicare Advantage", "Redrock Senior Health", "MA", "(800) 555-0185"),
    ("self-pay", "Self-pay", "None", "SELF", ""),
]

# Which plan types each specialty accepts (contracting rules).
SPECIALTY_PLAN_RULES = {
    "family-medicine": ["silverpeak-ppo", "silverpeak-hmo", "canyon-mutual", "lakeshore-epo", "beehive-community", "redrock-advantage", "self-pay"],
    "pediatrics": ["silverpeak-ppo", "silverpeak-hmo", "canyon-mutual", "lakeshore-epo", "beehive-community", "self-pay"],
    "internal-medicine": ["silverpeak-ppo", "silverpeak-hmo", "canyon-mutual", "lakeshore-epo", "redrock-advantage", "self-pay"],
    "dermatology": ["silverpeak-ppo", "canyon-mutual", "lakeshore-epo", "redrock-advantage", "self-pay"],
    "sports-medicine": ["silverpeak-ppo", "canyon-mutual", "lakeshore-epo", "redrock-advantage", "self-pay"],
    "womens-health": ["silverpeak-ppo", "silverpeak-hmo", "canyon-mutual", "lakeshore-epo", "beehive-community", "self-pay"],
}
# Individual exceptions: provider slug -> extra plan codes.
PROVIDER_EXTRA_PLANS = {
    "kathryn-wells": ["beehive-community"],
}

OFFICES = [
    {
        "slug": "sugar-house",
        "name": "Alderwick Sugar House Clinic",
        "address_line": "1420 E Ashbury Avenue, Suite 200",
        "city": "Salt Lake City",
        "postal_code": "84106",
        "phone": "(801) 555-0110",
        "fax": "(801) 555-0111",
        "description": "Our flagship clinic, offering primary care, pediatrics, dermatology, sports medicine, and women's health under one roof.",
        "services": "Primary care\nPediatrics\nDermatology\nSports medicine\nWomen's health\nOn-site lab draw station\nX-ray",
        "parking_notes": "Free parking in the covered garage off Ashbury Avenue. Bring your ticket to the front desk for validation.",
        "accessibility_notes": "Step-free entrance from the garage, elevator to the second floor, and wheelchair-accessible exam rooms.",
        "hours": {0: ("07:30", "18:00"), 1: ("07:30", "18:00"), 2: ("07:30", "18:00"), 3: ("07:30", "18:00"), 4: ("07:30", "18:00"), 5: ("08:00", "12:00")},
    },
    {
        "slug": "holladay",
        "name": "Alderwick Holladay Clinic",
        "address_line": "4680 S Larkspur Drive",
        "city": "Holladay",
        "postal_code": "84117",
        "phone": "(801) 555-0120",
        "fax": "(801) 555-0121",
        "description": "A neighborhood clinic focused on adult primary care, internal medicine, dermatology, and sports medicine.",
        "services": "Primary care\nInternal medicine\nDermatology\nSports medicine\nWomen's health\nOn-site lab draw station",
        "parking_notes": "Free surface parking directly in front of the building.",
        "accessibility_notes": "Single-story building with automatic doors and accessible restrooms.",
        "hours": {0: ("08:00", "17:00"), 1: ("08:00", "17:00"), 2: ("08:00", "17:00"), 3: ("08:00", "17:00"), 4: ("08:00", "17:00")},
    },
    {
        "slug": "sandy",
        "name": "Alderwick Sandy Clinic",
        "address_line": "9350 S Juniper Hollow Road",
        "city": "Sandy",
        "postal_code": "84070",
        "phone": "(801) 555-0130",
        "fax": "(801) 555-0131",
        "description": "Family-focused care for the south valley, including pediatrics, dermatology, and sports medicine. Open Saturday mornings.",
        "services": "Primary care\nPediatrics\nInternal medicine\nDermatology\nSports medicine\nOn-site lab draw station",
        "parking_notes": "Free parking in the east lot. Overflow parking is available behind the building.",
        "accessibility_notes": "Accessible parking stalls next to the main entrance; all exam rooms are on the ground floor.",
        "hours": {0: ("08:00", "18:00"), 1: ("08:00", "18:00"), 2: ("08:00", "18:00"), 3: ("08:00", "18:00"), 4: ("08:00", "18:00"), 5: ("09:00", "13:00")},
    },
    {
        "slug": "west-valley",
        "name": "Alderwick West Valley Clinic",
        "address_line": "3175 W Meadowlark Way",
        "city": "West Valley City",
        "postal_code": "84119",
        "phone": "(801) 555-0140",
        "fax": "(801) 555-0141",
        "description": "Bilingual English-Spanish clinic offering family medicine, pediatrics, internal medicine, dermatology, and women's health.",
        "services": "Primary care\nPediatrics\nInternal medicine\nDermatology\nWomen's health and prenatal care\nSpanish-speaking staff at every visit\nOn-site lab draw station",
        "parking_notes": "Free parking in the shared lot. A UTA bus stop is one block north on Meadowlark Way.",
        "accessibility_notes": "Ground-floor clinic with accessible entrance and restrooms. Interpreter services available in more than 200 languages.",
        "hours": {0: ("08:00", "17:30"), 1: ("08:00", "17:30"), 2: ("08:00", "17:30"), 3: ("08:00", "17:30"), 4: ("08:00", "17:30")},
    },
    {
        "slug": "virtual-care",
        "name": "Alderwick Virtual Care",
        "is_virtual": True,
        "phone": "(801) 555-0150",
        "description": "Secure video visits with Alderwick clinicians for follow-ups, medication checks, minor illnesses, and many routine concerns.",
        "services": "Video follow-up visits\nMedication management\nMinor illness visits\nBehavioral health check-ins",
        "parking_notes": "",
        "accessibility_notes": "Video visits support closed captioning and three-way interpreter calls.",
        "hours": {0: ("07:00", "19:00"), 1: ("07:00", "19:00"), 2: ("07:00", "19:00"), 3: ("07:00", "19:00"), 4: ("07:00", "19:00")},
    },
]

APPOINTMENT_TYPES = [
    # code, name, minutes, description, telehealth
    ("new-patient", "New patient visit", 40, "First visit to establish care with an Alderwick provider.", False),
    ("annual-physical", "Annual physical", 40, "Yearly preventive visit, screening, and health review.", False),
    ("follow-up", "Follow-up visit", 20, "Follow-up on an existing condition or recent visit.", False),
    ("sick-visit", "Sick visit", 20, "New illness or minor injury.", False),
    ("well-child", "Well-child visit", 40, "Pediatric checkup and immunizations.", False),
    ("skin-check", "Skin check", 20, "Full-body skin exam or evaluation of a skin concern.", False),
    ("procedure", "Procedure visit", 40, "In-office procedure such as a biopsy or joint injection.", False),
    ("prenatal", "Prenatal visit", 20, "Routine prenatal care.", False),
    ("telehealth", "Video visit", 20, "Secure video visit for follow-ups and minor concerns.", True),
]

# Provider tuple fields:
# first, last, credentials, specialty, gender, languages, office slugs, telehealth,
# accepting new patients, practicing since, board certification, education
PROVIDERS = [
    ("Elena", "Marquez", "MD", "family-medicine", "F", "English, Spanish", ["west-valley", "virtual-care"], True, True, 2011,
     "American Board of Family Medicine", "MD, University of New Mexico School of Medicine\nResidency, Family Medicine, University of Utah"),
    ("James", "Whitaker", "MD", "family-medicine", "M", "English", ["sugar-house"], False, False, 2003,
     "American Board of Family Medicine", "MD, Oregon Health & Science University\nResidency, Family Medicine, Swedish Medical Center"),
    ("Priyanka", "Desai", "DO", "family-medicine", "F", "English, Hindi, Gujarati", ["holladay", "virtual-care"], True, True, 2015,
     "American Board of Family Medicine", "DO, Rocky Vista University\nResidency, Family Medicine, McKay-Dee Family Medicine"),
    ("Thomas", "Nguyen", "MD", "family-medicine", "M", "English, Vietnamese", ["sandy"], False, True, 2009,
     "American Board of Family Medicine", "MD, University of Washington\nResidency, Family Medicine, University of Utah"),
    ("Rachel", "Kimball", "PA-C", "family-medicine", "F", "English", ["sugar-house", "virtual-care"], True, True, 2017,
     "National Commission on Certification of Physician Assistants", "MPAS, University of Utah Physician Assistant Program"),
    ("Marcus", "Bennett", "FNP-C", "family-medicine", "M", "English", ["west-valley"], False, True, 2016,
     "American Academy of Nurse Practitioners", "MSN, Family Nurse Practitioner, Westminster University"),
    ("Hannah", "Sorensen", "MD", "family-medicine", "F", "English", ["sandy"], False, True, 2013,
     "American Board of Family Medicine", "MD, University of Colorado\nResidency, Family Medicine, Intermountain St. Mark's"),
    ("David", "Okafor", "MD", "family-medicine", "M", "English", ["holladay"], False, False, 2005,
     "American Board of Family Medicine", "MD, University of Michigan\nResidency, Family Medicine, Utah Valley"),
    ("Grace", "Liu", "MD", "pediatrics", "F", "English, Mandarin", ["sugar-house"], False, True, 2012,
     "American Board of Pediatrics", "MD, Baylor College of Medicine\nResidency, Pediatrics, Primary Children's Hospital"),
    ("Samuel", "Tuilagi", "MD", "pediatrics", "M", "English, Samoan", ["west-valley"], False, True, 2014,
     "American Board of Pediatrics", "MD, University of Hawaiʻi John A. Burns School of Medicine\nResidency, Pediatrics, Primary Children's Hospital"),
    ("Megan", "Holloway", "DO", "pediatrics", "F", "English", ["sandy"], False, True, 2018,
     "American Board of Pediatrics", "DO, Kansas City University\nResidency, Pediatrics, University of Utah"),
    ("Ana", "Castillo", "CPNP", "pediatrics", "F", "English, Spanish", ["west-valley", "holladay"], False, True, 2019,
     "Pediatric Nursing Certification Board", "MSN, Pediatric Nurse Practitioner, University of Utah College of Nursing"),
    ("Robert", "Chen", "MD", "internal-medicine", "M", "English, Cantonese", ["holladay"], False, True, 2002,
     "American Board of Internal Medicine", "MD, University of California, San Francisco\nResidency, Internal Medicine, University of Utah"),
    ("Laura", "Petersen", "MD", "internal-medicine", "F", "English", ["sugar-house", "virtual-care"], True, True, 2010,
     "American Board of Internal Medicine", "MD, University of Minnesota\nResidency, Internal Medicine, Mayo Clinic"),
    ("Ibrahim", "Haddad", "MD", "internal-medicine", "M", "English, Arabic", ["sandy"], False, True, 2014,
     "American Board of Internal Medicine", "MD, University of Arizona\nResidency, Internal Medicine, University of Utah"),
    ("Kathryn", "Wells", "AGNP-C", "internal-medicine", "F", "English", ["west-valley", "virtual-care"], True, True, 2015,
     "American Academy of Nurse Practitioners", "MSN, Adult-Gerontology Nurse Practitioner, University of Utah"),
    ("Natalie", "Brooks", "MD", "dermatology", "F", "English", ["sugar-house", "sandy"], False, True, 2011,
     "American Board of Dermatology", "MD, Vanderbilt University\nResidency, Dermatology, University of Utah"),
    ("Daniel", "Moreno", "MD", "dermatology", "M", "English, Spanish", ["holladay", "west-valley"], False, False, 2007,
     "American Board of Dermatology", "MD, University of Texas Southwestern\nResidency, Dermatology, University of Colorado"),
    ("Olivia", "Grant", "PA-C", "dermatology", "F", "English", ["sandy", "virtual-care"], True, True, 2020,
     "National Commission on Certification of Physician Assistants", "MPAS, Rocky Mountain University of Health Professions"),
    ("Kevin", "Larsen", "MD", "sports-medicine", "M", "English", ["holladay", "sandy"], False, True, 2012,
     "American Board of Family Medicine, Certificate of Added Qualification in Sports Medicine", "MD, University of Utah\nFellowship, Primary Care Sports Medicine, University of Utah"),
    ("Jasmine", "Patel", "DO", "sports-medicine", "F", "English, Hindi", ["sugar-house"], False, True, 2017,
     "American Board of Family Medicine, Certificate of Added Qualification in Sports Medicine", "DO, Touro University Nevada\nFellowship, Sports Medicine, Intermountain Health"),
    ("Sarah", "Jensen", "MD", "womens-health", "F", "English", ["sugar-house"], False, True, 2008,
     "American Board of Obstetrics and Gynecology", "MD, University of Iowa\nResidency, Obstetrics and Gynecology, University of Utah"),
    ("Leilani", "Fonoti", "CNM", "womens-health", "F", "English, Samoan", ["west-valley"], False, True, 2016,
     "American Midwifery Certification Board", "MSN, Nurse-Midwifery, University of Utah"),
    ("Claire", "Donovan", "WHNP-BC", "womens-health", "F", "English", ["holladay", "virtual-care"], True, True, 2018,
     "National Certification Corporation", "MSN, Women's Health Nurse Practitioner, University of Utah"),
]

TITLES = {
    "family-medicine": "Family Medicine",
    "pediatrics": "Pediatrics",
    "internal-medicine": "Internal Medicine",
    "dermatology": "Dermatology",
    "sports-medicine": "Sports Medicine",
    "womens-health": "Women's Health",
}

BIO_FOCUS = {
    "family-medicine": "preventive care, chronic disease management, and helping families stay healthy across generations",
    "pediatrics": "well-child care, asthma and allergy management, and supporting parents through every stage of childhood",
    "internal-medicine": "diabetes, heart health, and coordinating care for adults with multiple chronic conditions",
    "dermatology": "skin cancer screening, acne, eczema, and psoriasis",
    "sports-medicine": "running injuries, joint pain, and getting active people safely back to the activities they love",
    "womens-health": "annual well-woman care, contraception, prenatal care, and menopause",
}

FRONT_OFFICE_STAFF = [
    # first, last, office slug, job title
    ("Brittany", "Hale", "sugar-house", "Front Office Supervisor"),
    ("Jordan", "Ellis", "sugar-house", "Patient Services Representative"),
    ("Tasha", "Morgan", "sugar-house", "Patient Services Representative"),
    ("Mei", "Tanaka", "holladay", "Patient Services Representative"),
    ("Courtney", "Ward", "holladay", "Referral Coordinator"),
    ("Amber", "Christensen", "sandy", "Patient Services Representative"),
    ("Tyler", "Jacobsen", "sandy", "Patient Services Representative"),
    ("Miguel", "Ortega", "west-valley", "Bilingual Patient Services Representative"),
    ("Rosa", "Delgado", "west-valley", "Bilingual Patient Services Representative"),
    ("Devon", "Price", "virtual-care", "Virtual Care Coordinator"),
]

AI_ENGINEERS = [
    ("Nikhil", "Rao", "AI Platform Engineer"),
    ("Avery", "Collins", "AI Operations Analyst"),
]

# ---------------------------------------------------------------------------
# Clinical library
# ---------------------------------------------------------------------------

CONDITIONS = {
    "htn": {
        "description": "Essential hypertension", "icd10": "I10", "chronic": True,
        "meds": [("Lisinopril", "10 mg", "Once daily")],
        "labs": ["bmp"],
        "subjective": "Reports good adherence to blood pressure medication. Checks BP at home a few times a week, mostly 120s-130s/70s-80s. No headaches, chest pain, or shortness of breath.",
        "assessment": "Hypertension, controlled on current regimen.",
        "plan": "Continue lisinopril 10 mg daily. Limit sodium, continue regular exercise. Recheck BMP annually.",
    },
    "t2dm": {
        "description": "Type 2 diabetes mellitus without complications", "icd10": "E11.9", "chronic": True,
        "meds": [("Metformin", "1000 mg", "Twice daily with meals")],
        "labs": ["a1c", "bmp"],
        "subjective": "Taking metformin as prescribed with occasional GI upset. Home fasting glucose mostly 120-150. Walking 3-4 days per week.",
        "assessment": "Type 2 diabetes, fair control.",
        "plan": "Continue metformin. Reviewed diet and activity goals. Recheck A1c in 3 months. Annual diabetic eye exam and foot exam due.",
    },
    "hld": {
        "description": "Hyperlipidemia, unspecified", "icd10": "E78.5", "chronic": True,
        "meds": [("Atorvastatin", "20 mg", "Once daily at bedtime")],
        "labs": ["lipid"],
        "subjective": "Tolerating statin without muscle aches.",
        "assessment": "Hyperlipidemia on statin therapy.",
        "plan": "Continue atorvastatin 20 mg. Repeat lipid panel in 12 months.",
    },
    "asthma": {
        "description": "Mild intermittent asthma, uncomplicated", "icd10": "J45.20", "chronic": True,
        "meds": [("Albuterol HFA", "90 mcg/actuation", "2 puffs every 4-6 hours as needed for wheezing")],
        "labs": [],
        "subjective": "Uses rescue inhaler about once a week, more with exercise in cold weather. No nighttime symptoms or ED visits.",
        "assessment": "Mild intermittent asthma, well controlled.",
        "plan": "Continue albuterol as needed. Use 15 minutes before exercise. Reviewed asthma action plan.",
    },
    "hypothyroid": {
        "description": "Hypothyroidism, unspecified", "icd10": "E03.9", "chronic": True,
        "meds": [("Levothyroxine", "75 mcg", "Once daily on an empty stomach")],
        "labs": ["tsh"],
        "subjective": "Energy is good. Takes levothyroxine each morning before breakfast.",
        "assessment": "Hypothyroidism, euthyroid on replacement.",
        "plan": "Continue levothyroxine 75 mcg. Recheck TSH in 12 months or sooner with symptoms.",
    },
    "anxiety": {
        "description": "Generalized anxiety disorder", "icd10": "F41.1", "chronic": True,
        "meds": [("Sertraline", "50 mg", "Once daily")],
        "labs": [],
        "subjective": "Anxiety improved since starting sertraline. Sleeping better. Using breathing exercises at work.",
        "assessment": "Generalized anxiety disorder, improving.",
        "plan": "Continue sertraline 50 mg. Offered referral to counseling. Follow up in 3 months.",
    },
    "depression": {
        "description": "Major depressive disorder, single episode, unspecified", "icd10": "F32.9", "chronic": True,
        "meds": [("Escitalopram", "10 mg", "Once daily")],
        "labs": [],
        "subjective": "Mood steadier. PHQ-9 improved from prior visit. Denies thoughts of self-harm.",
        "assessment": "Depression, improving on SSRI.",
        "plan": "Continue escitalopram 10 mg. Continue counseling. Reviewed crisis resources including 988. Follow up in 6-8 weeks.",
    },
    "gerd": {
        "description": "Gastro-esophageal reflux disease without esophagitis", "icd10": "K21.9", "chronic": True,
        "meds": [("Omeprazole", "20 mg", "Once daily before breakfast")],
        "labs": [],
        "subjective": "Heartburn controlled on omeprazole. Avoiding late meals.",
        "assessment": "GERD, controlled.",
        "plan": "Continue omeprazole. Discussed trial of step-down dosing at next visit if symptoms remain controlled.",
    },
    "migraine": {
        "description": "Migraine, unspecified, not intractable", "icd10": "G43.909", "chronic": True,
        "meds": [("Sumatriptan", "50 mg", "At onset of migraine; may repeat once after 2 hours")],
        "labs": [],
        "subjective": "Two to three migraines per month, usually triggered by poor sleep. Sumatriptan effective.",
        "assessment": "Episodic migraine.",
        "plan": "Continue sumatriptan as needed. Headache diary. Discussed sleep hygiene and hydration.",
    },
    "eczema": {
        "description": "Atopic dermatitis, unspecified", "icd10": "L20.9", "chronic": True,
        "meds": [("Triamcinolone 0.1% cream", "Thin layer", "Twice daily to affected areas for up to 2 weeks")],
        "labs": [],
        "subjective": "Itchy patches on arms and behind knees, worse in winter.",
        "assessment": "Atopic dermatitis, mild flare.",
        "plan": "Triamcinolone cream for flares. Daily fragrance-free moisturizer. Lukewarm showers.",
    },
    "acne": {
        "description": "Acne vulgaris", "icd10": "L70.0", "chronic": True,
        "meds": [("Tretinoin 0.025% cream", "Pea-sized amount", "Nightly to face")],
        "labs": [],
        "subjective": "Breakouts on face and upper back for over a year. Over-the-counter products not helping.",
        "assessment": "Acne vulgaris, moderate.",
        "plan": "Start tretinoin nightly, gentle cleanser, daily sunscreen. Follow up in 8-12 weeks.",
    },
    "psoriasis": {
        "description": "Psoriasis vulgaris", "icd10": "L40.0", "chronic": True,
        "meds": [("Clobetasol 0.05% ointment", "Thin layer", "Twice daily to plaques, max 2 weeks at a time")],
        "labs": [],
        "subjective": "Scaly plaques on elbows and knees, occasionally scalp. Mild itch.",
        "assessment": "Plaque psoriasis, limited body surface area.",
        "plan": "Clobetasol ointment in pulses. Discussed systemic options if extent increases.",
    },
    "nevi": {
        "description": "Melanocytic nevi, unspecified", "icd10": "D22.9", "chronic": False,
        "meds": [],
        "labs": [],
        "subjective": "Requests full skin check. Family history of melanoma in a parent.",
        "assessment": "Multiple benign-appearing nevi. No suspicious lesions today.",
        "plan": "Annual skin exams. Monthly self-checks. Sun protection counseling.",
    },
    "knee_oa": {
        "description": "Osteoarthritis of knee, unspecified", "icd10": "M17.9", "chronic": True,
        "meds": [("Meloxicam", "7.5 mg", "Once daily with food as needed")],
        "labs": [],
        "subjective": "Knee pain with stairs and after long walks. Morning stiffness under 30 minutes.",
        "assessment": "Knee osteoarthritis.",
        "plan": "Meloxicam as needed, physical therapy referral, weight-bearing exercise as tolerated.",
    },
    "knee_pain": {
        "description": "Pain in right knee", "icd10": "M25.561", "chronic": False,
        "meds": [],
        "labs": [],
        "subjective": "Anterior right knee pain for 6 weeks after increasing running mileage.",
        "assessment": "Patellofemoral pain syndrome, right knee.",
        "plan": "Relative rest, quad and hip strengthening program, gradual return to running.",
    },
    "lbp": {
        "description": "Low back pain, unspecified", "icd10": "M54.50", "chronic": False,
        "meds": [("Cyclobenzaprine", "5 mg", "At bedtime as needed for muscle spasm")],
        "labs": [],
        "subjective": "Low back pain after yard work. No leg numbness, weakness, or bowel/bladder changes.",
        "assessment": "Acute mechanical low back pain without red flags.",
        "plan": "Stay active, heat, home exercises, cyclobenzaprine at night as needed. Return if not improving in 4-6 weeks.",
    },
    "ankle_sprain": {
        "description": "Sprain of unspecified ligament of right ankle, initial encounter", "icd10": "S93.401A", "chronic": False,
        "meds": [],
        "labs": [],
        "subjective": "Rolled right ankle playing basketball. Able to bear weight with pain.",
        "assessment": "Right lateral ankle sprain, grade I-II. Ottawa rules negative.",
        "plan": "Ankle brace, ice, elevation, early range-of-motion exercises. Return-to-sport progression reviewed.",
    },
    "plantar_fasciitis": {
        "description": "Plantar fascial fibromatosis", "icd10": "M72.2", "chronic": False,
        "meds": [],
        "labs": [],
        "subjective": "Heel pain with first steps in the morning for 2 months. Training for a half marathon.",
        "assessment": "Plantar fasciitis, left foot.",
        "plan": "Calf and plantar fascia stretching, supportive shoes, reduce mileage temporarily, night splint optional.",
    },
    "allergic_rhinitis": {
        "description": "Other seasonal allergic rhinitis", "icd10": "J30.2", "chronic": True,
        "meds": [("Cetirizine", "10 mg", "Once daily during allergy season")],
        "labs": [],
        "subjective": "Sneezing and congestion in spring and fall.",
        "assessment": "Seasonal allergic rhinitis.",
        "plan": "Cetirizine daily in season. Nasal saline rinses. Consider nasal steroid if not controlled.",
    },
    "prediabetes": {
        "description": "Prediabetes", "icd10": "R73.03", "chronic": True,
        "meds": [],
        "labs": ["a1c"],
        "subjective": "Working on reducing sugary drinks. Started walking at lunch.",
        "assessment": "Prediabetes.",
        "plan": "Lifestyle changes, goal of 150 minutes of activity per week. Repeat A1c in 6-12 months.",
    },
    "adhd": {
        "description": "Attention-deficit hyperactivity disorder, unspecified type", "icd10": "F90.9", "chronic": True,
        "meds": [("Methylphenidate ER", "18 mg", "Once daily in the morning")],
        "labs": [],
        "subjective": "Parent and teacher report improved focus at school. Appetite slightly decreased at lunch.",
        "assessment": "ADHD, responding to stimulant medication.",
        "plan": "Continue methylphenidate ER 18 mg. Monitor growth and blood pressure. Follow up in 3 months.",
    },
    "pcos": {
        "description": "Polycystic ovarian syndrome", "icd10": "E28.2", "chronic": True,
        "meds": [("Norgestimate-ethinyl estradiol", "0.25 mg/35 mcg", "One tablet daily")],
        "labs": ["a1c"],
        "subjective": "Cycles more regular on combined oral contraceptive.",
        "assessment": "PCOS, stable.",
        "plan": "Continue oral contraceptive. Annual A1c screening. Discussed exercise and nutrition.",
    },
    "osteoporosis": {
        "description": "Age-related osteoporosis without current pathological fracture", "icd10": "M81.0", "chronic": True,
        "meds": [("Alendronate", "70 mg", "Once weekly, upright with full glass of water")],
        "labs": ["vitd"],
        "subjective": "No falls or fractures. Taking calcium and vitamin D.",
        "assessment": "Osteoporosis on bisphosphonate therapy.",
        "plan": "Continue alendronate. Weight-bearing exercise, fall prevention. Repeat DEXA in 2 years.",
    },
    "prenatal": {
        "description": "Encounter for supervision of normal pregnancy, unspecified trimester", "icd10": "Z34.90", "chronic": False,
        "meds": [("Prenatal multivitamin", "1 tablet", "Once daily")],
        "labs": ["cbc"],
        "subjective": "Feeling well. Mild nausea improving. No bleeding or cramping.",
        "assessment": "Normal intrauterine pregnancy, progressing well.",
        "plan": "Continue prenatal vitamin. Routine prenatal labs reviewed. Next prenatal visit in 4 weeks.",
    },
}

DERMATOLOGY_CONDITIONS = {"eczema", "acne", "psoriasis", "nevi"}
SPORTS_CONDITIONS = {"knee_pain", "ankle_sprain", "plantar_fasciitis", "lbp", "knee_oa"}

ALLERGIES = {
    "penicillin": ("Penicillin", "Hives", "moderate"),
    "sulfa": ("Sulfamethoxazole (sulfa drugs)", "Rash", "mild"),
    "peanuts": ("Peanuts", "Anaphylaxis", "severe"),
    "latex": ("Latex", "Contact dermatitis", "mild"),
    "codeine": ("Codeine", "Nausea and vomiting", "mild"),
    "shellfish": ("Shellfish", "Facial swelling", "severe"),
}

LAB_PANELS = {
    # key: (panel name, [(test, unit, low, high, typical_low, typical_high, decimals, ref text)])
    "a1c": ("Hemoglobin A1c", [("Hemoglobin A1c", "%", 4.0, 5.6, 4.8, 5.5, 1, "4.0-5.6")]),
    "bmp": ("Basic metabolic panel", [
        ("Glucose", "mg/dL", 70, 99, 76, 98, 0, "70-99"),
        ("Creatinine", "mg/dL", 0.6, 1.3, 0.68, 1.24, 2, "0.60-1.30"),
        ("Potassium", "mmol/L", 3.5, 5.1, 3.8, 5.0, 1, "3.5-5.1"),
        ("Sodium", "mmol/L", 136, 145, 137, 143, 0, "136-145"),
    ]),
    "lipid": ("Lipid panel", [
        ("Total cholesterol", "mg/dL", 0, 199, 145, 196, 0, "<200"),
        ("LDL cholesterol", "mg/dL", 0, 99, 62, 98, 0, "<100"),
        ("HDL cholesterol", "mg/dL", 40, 200, 41, 72, 0, ">40"),
        ("Triglycerides", "mg/dL", 0, 149, 78, 146, 0, "<150"),
    ]),
    "tsh": ("Thyroid stimulating hormone", [("TSH", "mIU/L", 0.4, 4.0, 0.9, 3.6, 2, "0.40-4.00")]),
    "cbc": ("Complete blood count", [
        ("Hemoglobin", "g/dL", 12.0, 16.0, 11.4, 14.8, 1, "12.0-16.0"),
        ("White blood cell count", "K/uL", 4.0, 11.0, 4.8, 9.8, 1, "4.0-11.0"),
        ("Platelets", "K/uL", 150, 400, 180, 360, 0, "150-400"),
    ]),
    "vitd": ("Vitamin D", [("25-hydroxy vitamin D", "ng/mL", 30, 100, 22, 48, 0, "30-100")]),
}

LANGUAGES = {"en": "English", "es": "Spanish", "vi": "Vietnamese", "ar": "Arabic", "zh": "Mandarin"}

# Patient tuple fields:
# first, last, sex, date of birth, language, plan code, primary provider (last name),
# condition keys, allergy keys, specialist (last name) or None, preferred name
PATIENTS = [
    ("Michael", "Anderson", "M", "1968-04-12", "en", "silverpeak-ppo", "Whitaker", ["htn", "hld"], ["penicillin"], None, "Mike"),
    ("Jennifer", "Thompson", "F", "1979-09-23", "en", "canyon-mutual", "Kimball", ["anxiety", "migraine"], [], None, "Jen"),
    ("Luis", "Hernandez", "M", "1955-01-30", "es", "beehive-community", "Marquez", ["t2dm", "htn", "hld"], ["sulfa"], None, ""),
    ("Emily", "Carter", "F", "1992-06-14", "en", "silverpeak-hmo", "Desai", ["asthma", "allergic_rhinitis"], ["peanuts"], None, ""),
    ("Robert", "Mitchell", "M", "1949-11-02", "en", "redrock-advantage", "Chen", ["htn", "knee_oa", "gerd"], [], None, "Bob"),
    ("Aisha", "Rahman", "F", "1986-03-08", "ar", "lakeshore-epo", "Haddad", ["hypothyroid"], [], None, ""),
    ("Daniel", "Kim", "M", "2001-07-19", "en", "silverpeak-ppo", "Okafor", ["ankle_sprain"], [], "Larsen", "Danny"),
    ("Sophia", "Martinez", "F", "1995-12-01", "es", "beehive-community", "Fonoti", ["prenatal"], [], None, ""),
    ("William", "Clark", "M", "1972-08-27", "en", "silverpeak-ppo", "Petersen", ["t2dm", "hld"], ["codeine"], None, "Will"),
    ("Olivia", "Nguyen", "F", "2015-05-10", "en", "silverpeak-hmo", "Liu", ["asthma", "eczema"], [], None, "Liv"),
    ("Ethan", "Brown", "M", "2012-02-22", "en", "canyon-mutual", "Holloway", ["adhd", "allergic_rhinitis"], [], None, ""),
    ("Isabella", "Garcia", "F", "2018-09-03", "es", "beehive-community", "Tuilagi", ["eczema"], [], None, "Bella"),
    ("Noah", "Wilson", "M", "2019-11-15", "en", "silverpeak-ppo", "Castillo", [], [], None, ""),
    ("Mia", "Taylor", "F", "2010-06-30", "en", "lakeshore-epo", "Holloway", ["acne", "anxiety"], [], None, ""),
    ("Lucas", "Fifita", "M", "2016-01-25", "en", "beehive-community", "Tuilagi", ["asthma"], [], None, ""),
    ("Patricia", "Young", "F", "1958-10-05", "en", "redrock-advantage", "Wells", ["osteoporosis", "hypothyroid", "htn"], ["sulfa"], None, "Pat"),
    ("Christopher", "Lee", "M", "1983-04-17", "en", "silverpeak-ppo", "Nguyen", ["lbp", "gerd"], [], None, "Chris"),
    ("Amanda", "Walker", "F", "1990-02-11", "en", "lakeshore-epo", "Jensen", ["pcos"], [], None, ""),
    ("Joshua", "Hall", "M", "1976-07-07", "en", "canyon-mutual", "Sorensen", ["htn", "prediabetes"], [], None, "Josh"),
    ("Megan", "Allen", "F", "1988-05-29", "en", "silverpeak-hmo", "Kimball", ["depression", "migraine"], ["latex"], None, ""),
    ("Andrew", "Wright", "M", "1965-12-19", "en", "silverpeak-ppo", "Okafor", ["hld", "gerd"], [], None, "Andy"),
    ("Stephanie", "King", "F", "1981-08-15", "en", "canyon-mutual", "Kimball", ["psoriasis"], [], "Brooks", ""),
    ("Kevin", "Scott", "M", "1999-03-03", "en", "silverpeak-hmo", "Kimball", ["knee_pain"], [], "Patel", ""),
    ("Rebecca", "Green", "F", "1974-11-21", "en", "silverpeak-ppo", "Donovan", ["hypothyroid"], [], None, "Becca"),
    ("Brandon", "Adams", "M", "1994-09-09", "en", "self-pay", "Kimball", ["anxiety"], [], None, ""),
    ("Nicole", "Baker", "F", "1987-01-14", "en", "lakeshore-epo", "Desai", ["hypothyroid", "allergic_rhinitis"], [], None, "Nikki"),
    ("Jose", "Ramirez", "M", "1970-06-02", "es", "beehive-community", "Bennett", ["t2dm", "htn"], ["penicillin"], None, ""),
    ("Maria", "Gonzalez", "F", "1962-03-26", "es", "beehive-community", "Marquez", ["t2dm", "hld", "depression"], [], None, ""),
    ("Kenji", "Watanabe", "M", "1958-08-11", "en", "redrock-advantage", "Chen", ["htn", "hld"], [], None, ""),
    ("Fatima", "Ali", "F", "1996-04-04", "ar", "silverpeak-ppo", "Haddad", ["migraine"], [], None, ""),
    ("Tyler", "Robinson", "M", "2003-10-10", "en", "canyon-mutual", "Sorensen", ["plantar_fasciitis"], [], "Larsen", ""),
    ("Hannah", "Lewis", "F", "1998-07-25", "en", "silverpeak-hmo", "Sorensen", ["allergic_rhinitis", "anxiety"], [], None, ""),
    ("Benjamin", "Harris", "M", "1953-02-17", "en", "redrock-advantage", "Petersen", ["htn", "t2dm", "knee_oa"], ["codeine"], None, "Ben"),
    ("Chloe", "Turner", "F", "1993-11-30", "en", "lakeshore-epo", "Jensen", ["prenatal"], [], None, ""),
    ("Samuel", "Phillips", "M", "1980-05-05", "en", "silverpeak-ppo", "Nguyen", ["psoriasis"], [], "Moreno", "Sam"),
    ("Lucia", "Torres", "F", "1985-09-17", "es", "beehive-community", "Bennett", ["prediabetes", "depression"], [], None, ""),
    ("Matthew", "Campbell", "M", "1977-03-21", "en", "canyon-mutual", "Whitaker", ["lbp", "htn"], [], None, "Matt"),
    ("Emma", "Parker", "F", "2000-01-08", "en", "silverpeak-hmo", "Sorensen", ["acne"], [], "Grant", ""),
    ("Jacob", "Evans", "M", "1968-10-13", "en", "silverpeak-ppo", "Okafor", ["t2dm", "hld", "gerd"], ["shellfish"], None, "Jake"),
    ("Abigail", "Edwards", "F", "1991-12-24", "en", "lakeshore-epo", "Donovan", ["migraine"], [], None, "Abby"),
    ("Vinh", "Tran", "M", "1960-07-14", "vi", "redrock-advantage", "Nguyen", ["htn", "hld", "gerd"], [], None, ""),
    ("Sione", "Taufa", "M", "1984-02-28", "en", "beehive-community", "Bennett", ["t2dm", "htn"], [], None, ""),
    ("Elizabeth", "Collins", "F", "1946-06-06", "en", "redrock-advantage", "Wells", ["osteoporosis", "htn", "hld"], ["penicillin"], None, "Betty"),
    ("Ryan", "Murphy", "M", "1989-08-08", "en", "silverpeak-ppo", "Whitaker", ["lbp"], [], "Patel", ""),
    ("Ashley", "Cook", "F", "1997-04-19", "en", "canyon-mutual", "Kimball", ["asthma", "anxiety"], ["sulfa"], None, ""),
    ("Jonathan", "Rogers", "M", "1975-01-31", "en", "lakeshore-epo", "Desai", ["htn", "prediabetes"], [], None, "Jon"),
    ("Samantha", "Reed", "F", "1983-10-22", "en", "silverpeak-hmo", "Desai", ["nevi"], [], "Brooks", "Sam"),
    ("Alejandro", "Cruz", "M", "1999-05-16", "es", "self-pay", "Marquez", [], [], None, "Alex"),
    ("Lily", "Zhang", "F", "2014-08-19", "zh", "silverpeak-ppo", "Liu", ["allergic_rhinitis"], [], None, ""),
    ("Margaret", "Sullivan", "F", "1952-09-09", "en", "redrock-advantage", "Petersen", ["hypothyroid", "osteoporosis", "gerd"], [], None, "Peggy"),
]

STREETS = [
    "Maple Grove Lane", "Cottonwood Drive", "Sagebrush Court", "Highland Vista Way", "Pioneer Park Road",
    "Quail Hollow Drive", "Red Butte Lane", "Willow Creek Circle", "Granite Ridge Road", "Aspen Meadow Drive",
    "Canyon Breeze Way", "Larkspur Court", "Juniper Ridge Lane", "Old Mill Road", "Silver Sage Drive",
]
CITIES = [
    ("Salt Lake City", "84105"), ("Salt Lake City", "84106"), ("Holladay", "84117"), ("Sandy", "84070"),
    ("Sandy", "84092"), ("West Valley City", "84119"), ("West Valley City", "84120"), ("Murray", "84107"),
    ("Taylorsville", "84129"), ("Draper", "84020"), ("Midvale", "84047"), ("South Jordan", "84095"),
]
EMERGENCY_CONTACT_NAMES = [
    ("Karen", "Spouse"), ("David", "Spouse"), ("Linda", "Parent"), ("Mark", "Sibling"), ("Susan", "Spouse"),
    ("Paul", "Parent"), ("Angela", "Sibling"), ("Steven", "Spouse"), ("Teresa", "Friend"), ("Brian", "Spouse"),
]

# ---------------------------------------------------------------------------
# Front-office queue: appointment requests
# hours_ago, status, patient index or None, prospect details, specialty, provider last name,
# office slug, preferred times, reason, source
# ---------------------------------------------------------------------------

APPOINTMENT_REQUESTS = [
    # New prospective patients from the public website
    {"hours_ago": 2, "status": "submitted", "prospect": ("Rachel", "Oyelaran", "1990-04-18", "rachel.oyelaran@example.com", "(801) 555-0181", "silverpeak-ppo"),
     "specialty": "family-medicine", "provider": None, "office": "sugar-house", "times": "Weekday mornings before 10",
     "reason": "Just moved to Salt Lake from Denver and need to establish with a new primary care doctor. I take a daily thyroid medication and will need refills soon."},
    {"hours_ago": 5, "status": "submitted", "prospect": ("Marcos", "Villanueva", "1984-11-02", "mvillanueva@example.com", "(801) 555-0182", "beehive-community"),
     "specialty": "family-medicine", "provider": "Marquez", "office": "west-valley", "times": "Any afternoon",
     "reason": "Necesito un chequeo general y renovar mi receta de presion. Prefiero un doctor que hable espanol."},
    {"hours_ago": 9, "status": "submitted", "prospect": ("Kayla", "Thornton", "2021-03-14", "kthornton.family@example.com", "(801) 555-0183", "silverpeak-hmo"),
     "specialty": "pediatrics", "provider": None, "office": "sandy", "times": "Saturday mornings if possible",
     "reason": "Looking for a pediatrician for my 5-year-old daughter. She needs her kindergarten checkup and vaccines before school paperwork is due."},
    {"hours_ago": 20, "status": "submitted", "prospect": ("Derek", "Lindqvist", "1979-07-30", "dlindqvist@example.com", "(801) 555-0184", "canyon-mutual"),
     "specialty": "sports-medicine", "provider": "Larsen", "office": "holladay", "times": "Late afternoons",
     "reason": "Shoulder pain for about a month after pickleball. Hurts when I reach overhead. Would like to see a sports medicine doctor."},
    {"hours_ago": 27, "status": "submitted", "prospect": ("Priya", "Shah", "1996-01-09", "priya.shah@example.com", "(801) 555-0185", "lakeshore-epo"),
     "specialty": "dermatology", "provider": None, "office": None, "times": "Flexible",
     "reason": "Mole on my back that a friend said looks different than it used to. I'd like a skin check."},
    {"hours_ago": 31, "status": "submitted", "prospect": ("Harold", "Becker", "1950-05-22", "", "(801) 555-0186", "redrock-advantage"),
     "specialty": "internal-medicine", "provider": "Chen", "office": "holladay", "times": "Mornings",
     "reason": "My cardiologist retired and I need a new internist to manage my blood pressure and cholesterol. I have a pacemaker."},
    {"hours_ago": 44, "status": "submitted", "prospect": ("Tiana", "Mahe", "1999-08-12", "tiana.mahe@example.com", "(801) 555-0187", "silverpeak-ppo"),
     "specialty": "womens-health", "provider": "Fonoti", "office": "west-valley", "times": "Weekdays after 2 pm",
     "reason": "Just found out I'm pregnant (about 7 weeks) and would like to start prenatal care with a midwife."},
    {"hours_ago": 52, "status": "under_review", "prospect": ("Greg", "Halvorsen", "1972-12-03", "ghalvorsen@example.com", "(801) 555-0188", None),
     "insurance_other": "Pinnacle Federal Employee Plan", "specialty": "family-medicine", "provider": "Whitaker", "office": "sugar-house", "times": "Any",
     "reason": "Annual physical. My employer switched plans and I'm not sure if you take it.", "staff_notes": "Plan not on our contracted list. Called and left voicemail to discuss self-pay or out-of-network options. Dr. Whitaker is not accepting new patients - offer Rachel Kimball, PA-C."},
    {"hours_ago": 70, "status": "under_review", "prospect": ("Jasmine", "Ortiz", "2008-02-17", "ortiz.family@example.com", "(801) 555-0189", "beehive-community"),
     "specialty": "pediatrics", "provider": None, "office": "west-valley", "times": "After school (3:30 or later)",
     "reason": "My son's asthma inhaler ran out and his old pediatrician is in another state.", "staff_notes": "Mother is calling on behalf of 18-year-old? DOB shows age 18 - confirm whether patient will see pediatrics or family medicine."},
    {"hours_ago": 120, "status": "declined", "prospect": ("Victor", "Hale", "1966-09-25", "vhale@example.com", "(801) 555-0191", "silverpeak-ppo"),
     "specialty": "family-medicine", "provider": None, "office": None, "times": "",
     "reason": "Need a prescription for a controlled pain medication I used to get from my old doctor.", "decline_reason": "Alderwick does not prescribe controlled substances at a first visit without prior records. Patient was invited to schedule a new patient visit and send prior records."},
    {"hours_ago": 140, "status": "declined", "prospect": ("Lauren", "Pike", "1988-06-06", "lauren.pike@example.com", "(801) 555-0192", "silverpeak-ppo"),
     "specialty": "dermatology", "provider": "Moreno", "office": "holladay", "times": "",
     "reason": "Cosmetic Botox consultation.", "decline_reason": "Alderwick dermatology does not offer cosmetic procedures. Sent list of community resources."},
    {"hours_ago": 160, "status": "scheduled", "prospect": ("Owen", "Fairbanks", "1991-10-29", "owen.f@example.com", "(801) 555-0193", "canyon-mutual"),
     "specialty": "family-medicine", "provider": "Kimball", "office": "sugar-house", "times": "Mornings",
     "reason": "New to the area, need a primary care provider and a physical.", "appointment_type": "new-patient", "sex": "M"},
    # Existing patients through the portal
    {"hours_ago": 3, "status": "submitted", "patient": 0, "specialty": "family-medicine", "provider": "Whitaker", "office": "sugar-house", "times": "Early morning",
     "reason": "Blood pressure readings at home have been higher this week (150s/90s). Would like to come in.", "source": "portal"},
    {"hours_ago": 7, "status": "submitted", "patient": 19, "specialty": "family-medicine", "provider": "Kimball", "office": None, "times": "Video visit preferred",
     "reason": "Follow-up on my depression medication. I think the dose might need adjusting.", "source": "portal"},
    {"hours_ago": 15, "status": "submitted", "patient": 30, "specialty": "sports-medicine", "provider": "Larsen", "office": "sandy", "times": "Any",
     "reason": "Heel pain is back after I started running again.", "source": "portal"},
    {"hours_ago": 23, "status": "submitted", "patient": 36, "specialty": "family-medicine", "provider": None, "office": "sugar-house", "times": "Lunch hour",
     "reason": "Back pain flared up again after moving furniture.", "source": "portal"},
    {"hours_ago": 38, "status": "submitted", "patient": 9, "specialty": "pediatrics", "provider": "Liu", "office": "sugar-house", "times": "After 3 pm",
     "reason": "Mother called: Olivia has been wheezing at night for a week even with her inhaler.", "source": "phone"},
    {"hours_ago": 48, "status": "under_review", "patient": 42, "specialty": "internal-medicine", "provider": "Wells", "office": "virtual-care", "times": "Mornings",
     "reason": "Would like to review my bone density results and medications.", "source": "portal", "staff_notes": "Needs DEXA report from outside imaging center first. Requested records."},
    {"hours_ago": 60, "status": "submitted", "patient": 27, "specialty": "family-medicine", "provider": "Marquez", "office": "west-valley", "times": "Cualquier dia",
     "reason": "Control de diabetes y analisis de sangre.", "source": "portal"},
    {"hours_ago": 96, "status": "scheduled", "patient": 3, "specialty": "family-medicine", "provider": "Desai", "office": "holladay", "times": "Afternoons",
     "reason": "Allergies are bad this season and I need an asthma check.", "source": "portal", "appointment_type": "follow-up"},
    {"hours_ago": 110, "status": "scheduled", "patient": 23, "specialty": "womens-health", "provider": "Donovan", "office": "holladay", "times": "Any",
     "reason": "Annual well-woman exam.", "source": "portal", "appointment_type": "annual-physical"},
    # Phone requests logged by staff
    {"hours_ago": 4, "status": "submitted", "patient": 4, "specialty": "internal-medicine", "provider": "Chen", "office": "holladay", "times": "Mornings",
     "reason": "Called: knee pain worse, asking about injection.", "source": "phone"},
    {"hours_ago": 30, "status": "submitted", "patient": 45, "specialty": "family-medicine", "provider": "Desai", "office": "holladay", "times": "Fridays",
     "reason": "Called: wants to recheck A1c since last result was borderline.", "source": "phone"},
]

# ---------------------------------------------------------------------------
# Secure messages
# patient index, category, subject, conversation [(from_patient, hours_ago, body)], status
# ---------------------------------------------------------------------------

MESSAGE_THREADS = [
    (0, "prescription", "Lisinopril refill",
     [(True, 6, "Hi, I have 4 lisinopril pills left. Can you send a refill to the same pharmacy as last time? Thanks, Mike")], "open"),
    (2, "test_results", "Resultados de laboratorio",
     [(True, 20, "Buenos dias Dra. Marquez. Vi que mis resultados de A1c estan en el portal. Que significa 7.8? Necesito cambiar algo?")], "open"),
    (3, "appointments", "Need to reschedule",
     [(True, 26, "I have an appointment next week but I'll be traveling for work. Can I move it to the following week, ideally Thursday afternoon?")], "open"),
    (4, "billing", "Question about my bill",
     [(True, 30, "I got a statement for $85 for my last visit. I thought my Medicare Advantage plan covered office visits completely. Can someone explain?")], "open"),
    (5, "clinical", "Feeling tired",
     [(True, 14, "Dr. Haddad, I've been feeling more tired than usual for the last few weeks and my hair seems thinner. Could my thyroid dose be off?")], "open"),
    (7, "clinical", "Cramping",
     [(True, 3, "I'm 10 weeks pregnant and have had some mild cramping today, no bleeding. Is this normal or should I come in?")], "open"),
    (8, "test_results", "Cholesterol results",
     [(True, 40, "Saw my LDL went up. Should I be worried? I've been eating out a lot lately."),
      (False, 30, "Hi Will, thanks for reaching out. Your LDL is a bit above goal. I'd like to see you for a follow-up to talk about options. The front desk will call you to schedule. - Dr. Petersen"),
      (True, 28, "Sounds good, thank you.")], "closed"),
    (10, "records", "School medication form",
     [(True, 48, "Ethan's school needs the medication authorization form signed for his ADHD medicine. Can Dr. Holloway sign it? I uploaded it at the front desk last week.")], "open"),
    (12, "appointments", "Well-child visit",
     [(True, 72, "Noah is due for his 7-year checkup. What times does Ana Castillo have at the Holladay office?"),
      (False, 70, "Hi! Ana Castillo sees patients at our Holladay clinic on Wednesdays and Fridays. We have openings next Wednesday at 9:00 and 10:20. Would either work?"),
      (True, 66, "Wednesday at 9 works great."),
      (False, 65, "You're all set for Wednesday at 9:00 at our Holladay clinic. Please bring his immunization record.")], "closed"),
    (15, "prescription", "Alendronate question",
     [(True, 18, "My pharmacy says my alendronate refill needs a new prescription. Can Kathryn send one?")], "open"),
    (16, "billing", "Insurance card update",
     [(True, 22, "My employer changed my plan ID number. How do I update my insurance card on file?")], "open"),
    (19, "clinical", "Medication side effects",
     [(True, 9, "Since increasing escitalopram I feel jittery in the mornings and I'm having trouble sleeping. Should I go back to the old dose?")], "open"),
    (21, "clinical", "Rash on elbows",
     [(True, 55, "The psoriasis on my elbows is spreading even with the ointment. Should I see Dr. Brooks again?"),
      (False, 50, "Hi Stephanie, Rachel Kimball here. Thanks for the update. I'd recommend a follow-up with Dr. Brooks - I've let the front desk know to help you schedule.")], "closed"),
    (24, "billing", "Self-pay pricing",
     [(True, 33, "I don't have insurance right now. How much does a follow-up visit cost if I pay myself?")], "open"),
    (26, "prescription", "Metformin refill",
     [(True, 12, "Necesito mas metformina por favor. Me quedan 3 dias.")], "open"),
    (28, "appointments", "Cancel appointment",
     [(True, 5, "I need to cancel my appointment tomorrow morning with Dr. Chen. Something came up at work. Will there be a fee?")], "open"),
    (29, "clinical", "Migraine frequency",
     [(True, 46, "My migraines have increased to about once a week. The sumatriptan still works but I'm using it a lot. Is there a preventive medication I could try?")], "open"),
    (31, "records", "Records request",
     [(True, 60, "I'm applying for graduate school and need a copy of my immunization records. How can I get them?"),
      (False, 58, "Hi Hannah, you can download your immunization record from the Health Record page of the portal, or we can mail or fax a copy. Just let us know where to send it.")], "closed"),
    (32, "test_results", "Kidney function",
     [(True, 15, "My creatinine was flagged. Does that mean my kidneys are failing? I'm worried.")], "open"),
    (33, "appointments", "Prenatal visit timing",
     [(True, 27, "How often should I be scheduling prenatal visits right now? I'm 16 weeks.")], "open"),
    (35, "billing", "Payment plan",
     [(True, 80, "I have a balance of $340 from my last few visits. Can I set up a payment plan?"),
      (False, 76, "Hi Lucia, yes - balances over $200 qualify for an interest-free payment plan of up to 12 months. Our billing office at (801) 555-0199 can set it up with you.")], "closed"),
    (36, "clinical", "Back pain again",
     [(True, 8, "My back pain is back after moving furniture. Should I take the cyclobenzaprine again? It's been about 6 months since my last prescription.")], "open"),
    (38, "prescription", "Omeprazole refill",
     [(True, 36, "Please refill omeprazole 20 mg. Thank you.")], "open"),
    (40, "test_results", "Lipid results",
     [(True, 52, "Toi muon biet ket qua xet nghiem mo mau cua toi. Cam on bac si.")], "open"),
    (42, "appointments", "Transportation",
     [(True, 19, "I don't drive anymore. Is my appointment next week available as a video visit instead?")], "open"),
    (44, "clinical", "Inhaler use",
     [(True, 11, "I've been using my albuterol inhaler almost every day this week because of the wildfire smoke. Is that okay?")], "open"),
    (45, "records", "FMLA paperwork",
     [(True, 64, "I need FMLA paperwork completed for my upcoming surgery recovery. Who should I send it to?")], "open"),
    (47, "billing", "Cost of new patient visit",
     [(True, 90, "What would a new patient visit cost for self-pay?"),
      (False, 88, "Hi Alex, a self-pay new patient visit is $210 before the 30% prompt-pay discount, so $147 if paid at the time of service. Labs are billed separately.")], "closed"),
    (49, "clinical", "Dizziness",
     [(True, 2, "I felt dizzy this morning when I stood up and almost fell. I'm okay now. Should I be seen?")], "open"),
    (1, "appointments", "Video visit option",
     [(True, 16, "Can I do my anxiety follow-up as a video visit? I work downtown.")], "open"),
    (6, "records", "Sports clearance form",
     [(True, 84, "I need a sports physical form signed for my rec league. Can Dr. Larsen sign the one from my ankle visit?"),
      (False, 80, "Hi Danny, sports clearance forms require a visit. We can schedule a 20-minute visit with Dr. Larsen - would next week work?")], "closed"),
    (17, "clinical", "Cycle questions",
     [(True, 42, "My cycles have been irregular again for two months even on the pill. Should I come in?")], "open"),
    (25, "test_results", "TSH result",
     [(True, 24, "Saw my TSH result in the portal. Is it normal?")], "open"),
]

# ---------------------------------------------------------------------------
# Patient resources (policy documents)
# ---------------------------------------------------------------------------

POLICY_DOCUMENTS = [
    {
        "slug": "new-patients",
        "title": "New Patient Policy",
        "category": "patient_policy",
        "summary": "How to become an Alderwick patient, what to bring to your first visit, and how we transfer records.",
        "body": """Welcome to Alderwick Family Health. We are glad you are considering us for your care.

## Becoming a patient
- Request a new patient appointment online, through our main line at (801) 555-0100, or by visiting any clinic.
- New patient visits are 40 minutes so your provider has time to review your history.
- Some providers are not currently accepting new patients. The Find a Provider page shows each provider's status, and our staff can suggest a provider with openings.
- Patients under 18 must be accompanied by a parent or legal guardian at their first visit.

## What to bring
- A photo ID and your current insurance card.
- A list of all medications, vitamins, and supplements, including doses.
- Contact information for your previous doctors and any specialists.
- Immunization records, especially for children.
- Your copay or payment for self-pay visits.

## Before your visit
Please arrive 15 minutes early to complete check-in. New patient forms can be completed in advance through the patient portal once your account is activated. If you arrive more than 15 minutes late, we may need to reschedule your visit.

## Transferring records
Sign a records release form at your first visit or download one from the portal. We request records from your previous providers at no charge. Records usually arrive within 2-3 weeks.

## Controlled substances
Alderwick providers do not prescribe controlled substances, such as opioids or stimulants, at a first visit without reviewing prior records. Ongoing prescriptions require regular follow-up visits.
""",
    },
    {
        "slug": "cancellation-no-show",
        "title": "Appointment Cancellation and No-Show Policy",
        "category": "patient_policy",
        "summary": "Please give us at least 24 hours' notice to cancel or reschedule. Fees apply for late cancellations and missed visits.",
        "body": """When an appointment is missed, another patient loses the chance to be seen. This policy helps us keep appointments available for everyone.

## Cancelling or rescheduling
- Cancel or reschedule at least 24 hours before your appointment.
- You can cancel online in the patient portal up to 24 hours before your visit.
- Within 24 hours, please call your clinic directly.

## Fees
- Late cancellation (less than 24 hours' notice): $35.
- No-show (missed visit without notice): $50.
- Procedure visits and new patient visits: $75 for a late cancellation or no-show.
- Fees are not billed to insurance and are the patient's responsibility.

## Exceptions
We waive fees for emergencies, hospitalization, severe weather when the clinic is open but travel is unsafe, and other circumstances reviewed by the office manager. Call your clinic to request a waiver.

## Late arrivals
If you arrive more than 15 minutes late, we may ask you to reschedule so other patients are not delayed. Late arrivals that require rescheduling are not charged a fee the first time.

## Repeated missed visits
Three no-shows within 12 months may lead to a review by the practice manager, which can include a requirement to book only same-day appointments.
""",
    },
    {
        "slug": "insurance-billing",
        "title": "Insurance and Billing FAQ",
        "category": "billing",
        "summary": "Accepted insurance plans, copays, self-pay pricing, payment plans, and how to reach our billing office.",
        "body": """## Which insurance plans do you accept?
Alderwick is contracted with the following plans. Not every provider accepts every plan; the Find a Provider page shows each provider's accepted plans.
- SilverPeak PPO
- SilverPeak HMO Select (referral from your primary care provider required for specialists)
- Canyon Mutual Choice PPO
- Lakeshore Employers Health EPO
- Beehive Community Health Plan (Medicaid managed care) - family medicine, pediatrics, and women's health
- Redrock Medicare Advantage - family medicine, internal medicine, dermatology, and sports medicine

If your plan is not listed, you may still be seen as a self-pay patient or using out-of-network benefits. Check with your insurer first.

## When do I pay?
Copays are collected at check-in. Coinsurance and deductible amounts are billed after your insurance processes the claim. Statements are mailed and posted to the portal monthly.

## Self-pay pricing
- New patient visit: $210
- Established patient follow-up or sick visit: $135
- Annual physical: $225
- Video visit: $95
Self-pay patients receive a 30% prompt-pay discount when paying in full at the time of service. Lab tests are billed separately by our reference laboratory. Self-pay patients can request a Good Faith Estimate of expected charges before scheduling.

## Payment plans
Balances over $200 can be set up on an interest-free payment plan of up to 12 months. Call our billing office to set one up.

## Billing office
Phone: (801) 555-0199, Monday through Friday, 8:00 a.m. to 4:30 p.m.
Questions about a statement can also be sent through the portal using the Billing and insurance message category.

## Updating your insurance
Update your insurance at check-in or send a photo of the front and back of your new card through a portal message. Bring your new card to your next visit.

## Financial assistance
Patients with household income under 200% of the federal poverty level may qualify for a sliding-fee discount. Ask the front desk for an application.
""",
    },
    {
        "slug": "preparing-for-your-visit",
        "title": "Preparing for Your Visit",
        "category": "visit_preparation",
        "summary": "What to do before annual physicals, lab visits, skin checks, sports medicine visits, well-child visits, and prenatal care.",
        "body": """A little preparation helps you get the most from your appointment.

## For every visit
- Arrive 15 minutes early and bring your photo ID and insurance card.
- Bring your current medication list or the bottles themselves.
- Write down your top two or three questions.

## Annual physical
- If your provider ordered fasting labs, do not eat or drink anything except water and your usual medications for 8 to 10 hours before your blood draw.
- Bring records of any recent screenings done elsewhere, such as mammograms or colonoscopies.

## Lab-only visits
Lab draw stations at Sugar House, Holladay, Sandy, and West Valley are open on weekdays from 7:30 a.m. to 4:00 p.m. No appointment is needed. Results are released to the patient portal after your provider reviews them, usually within 3 business days.

## Skin checks
- Remove nail polish and makeup so your clinician can examine your skin and nails.
- Note any spots that are new, changing, bleeding, or itching.

## Sports medicine visits
Wear or bring shorts and athletic shoes. Bring any braces or orthotics you use, and imaging reports from other facilities.

## Well-child visits
Bring your child's immunization record and any school, sports, or daycare forms that need to be completed. Well-child visits are 40 minutes.

## Prenatal visits
Your first prenatal visit includes lab work and a longer conversation about your health history. Bring a list of any medications or supplements you are taking. Routine prenatal visits are every 4 weeks until 28 weeks, every 2 weeks until 36 weeks, and weekly after that.

## Video visits
See the Video Visits guide for technology requirements and how to join.
""",
    },
    {
        "slug": "video-visits",
        "title": "Video Visits",
        "category": "visit_preparation",
        "summary": "Which concerns are a good fit for a video visit, how to join, and what to do if your connection drops.",
        "body": """Alderwick Virtual Care offers secure video visits with many of our providers.

## Good uses for a video visit
- Follow-up on a stable chronic condition such as blood pressure, thyroid, or anxiety.
- Medication checks and dose adjustments.
- Reviewing lab or imaging results.
- Minor illnesses such as cold symptoms, pink eye, or urinary symptoms.

## When to come in person
Physical exams, procedures, injuries that may need an X-ray, new patient visits, well-child visits, and prenatal visits must be in person.

## Requirements
- You must be physically located in Utah at the time of your video visit.
- A smartphone, tablet, or computer with a camera, microphone, and internet connection.
- A private, well-lit space.

## Joining your visit
Open the link in your appointment reminder 15 minutes before your visit to test your camera and microphone. Your clinician will join at your appointment time.

## If your connection drops
Your clinician will try to reconnect and then call the phone number on file. If the visit cannot be completed by video, it may be finished by phone or rescheduled at no charge.

## Cost
Video visits are billed like office visits. Your usual copay applies. The self-pay price is $95.
""",
    },
    {
        "slug": "prescription-refills",
        "title": "Prescription Refills",
        "category": "patient_policy",
        "summary": "How to request refills, how long they take, and when a visit is needed.",
        "body": """## Requesting a refill
- The fastest way is to ask your pharmacy to send us a refill request.
- You can also send a portal message using the Prescription refill category.
- Please request refills at least 3 business days before you run out.

## How long refills take
Most refill requests are completed within 2 business days. Requests received after 3:00 p.m. on Friday are handled the next business day.

## When a visit is required
- Most ongoing prescriptions require at least one visit with your provider every 12 months.
- Blood pressure, diabetes, and thyroid medications may require recent lab work before a refill.
- Controlled substances, including stimulants for ADHD, require a visit at least every 3 months and cannot be refilled early.

## After hours
Refill requests are not handled after hours or on weekends. If you are out of a critical medication, call the after-hours nurse line at (801) 555-0190.
""",
    },
    {
        "slug": "patient-portal-and-messaging",
        "title": "Patient Portal and Secure Messaging",
        "category": "patient_policy",
        "summary": "What the portal is for, how quickly we respond to messages, and what not to send through the portal.",
        "body": """The patient portal lets you view your health record and appointments, request appointments, and send secure messages to your care team.

## Response times
We respond to portal messages within 2 business days. Messages sent on weekends or holidays are answered the next business day.

## Messages are not for emergencies
Never use the portal for urgent or emergency concerns. If you think you are having a medical emergency, call 911 or go to the nearest emergency department. For urgent questions after hours, call our nurse line at (801) 555-0190.

## Choosing a message category
- Appointments and scheduling, Billing and insurance, and Records and forms messages go to our front office team.
- Prescription refill, Test results, and Medical question messages go to your primary care provider's care team.

## Test results
Most results are released to the portal automatically after your provider reviews them, usually within 3 business days. Your provider will add a comment or contact you if any follow-up is needed.

## Portal access for minors
Parents and guardians can request proxy access to a child's portal account. Patients ages 13 to 17 have confidential access to some parts of their record under Utah law.

## Forms
Forms such as FMLA paperwork, school forms, and disability forms usually take 5 to 7 business days to complete. Some forms require a visit.
""",
    },
    {
        "slug": "after-hours-and-emergencies",
        "title": "After-Hours Care and Emergencies",
        "category": "patient_policy",
        "summary": "When to call 911, when to use the after-hours nurse line, and where to go for urgent care.",
        "body": """## Call 911 or go to the nearest emergency department for:
- Chest pain or pressure, or pain spreading to the arm, jaw, or back.
- Trouble breathing or severe shortness of breath.
- Signs of stroke: face drooping, arm weakness, or slurred speech.
- Severe bleeding, a serious injury, or loss of consciousness.
- Thoughts of harming yourself or others. You can also call or text 988, the Suicide and Crisis Lifeline.
- In pregnancy: heavy bleeding, severe abdominal pain, or decreased fetal movement after 28 weeks.

## After-hours nurse line
For urgent questions when clinics are closed, call (801) 555-0190. A registered nurse is available 24 hours a day and can help you decide whether you need care right away.

## Same-day care
Call your clinic in the morning for same-day sick visits. Video visits are often available the same day for minor illnesses.

## Urgent care
For non-life-threatening problems after hours, such as a sprain, minor cut, or fever, you may visit any in-network urgent care clinic. Please send us any urgent care records so we can follow up.
""",
    },
    {
        "slug": "privacy-notice",
        "title": "Notice of Privacy Practices (Summary)",
        "category": "privacy",
        "summary": "A plain-language summary of how Alderwick uses and protects your health information.",
        "body": """This is a summary. The full notice is available at any clinic front desk.

## How we use your information
We use and share your health information to treat you, to bill for your care, and to run our practice, such as for quality reviews. We do not sell your information.

## Your rights
- See and get a copy of your health record.
- Ask us to correct your record.
- Ask us to limit what we share in some cases.
- Get a list of those with whom we have shared your information.
- Choose someone to act for you.

## Who can see your record
Alderwick staff can access your record only when needed for their job. Every access to your chart is logged and regularly reviewed.

## Questions or complaints
Contact our privacy officer at (801) 555-0198. You will not be penalized for filing a complaint.
""",
    },
]


# Condition-specific typical ranges: condition -> {test name: (typical low, typical high)}.
LAB_CONDITION_RANGES = {
    "t2dm": {"Hemoglobin A1c": (6.6, 8.6), "Glucose": (112, 178)},
    "prediabetes": {"Hemoglobin A1c": (5.7, 6.3), "Glucose": (96, 118)},
    "pcos": {"Hemoglobin A1c": (5.2, 5.9)},
    "hld": {"LDL cholesterol": (92, 162), "Total cholesterol": (178, 246), "Triglycerides": (120, 230)},
    "hypothyroid": {"TSH": (1.1, 5.6)},
    "htn": {"Creatinine": (0.8, 1.42), "Potassium": (3.9, 5.3)},
    "osteoporosis": {"25-hydroxy vitamin D": (21, 44)},
    "prenatal": {"Hemoglobin": (10.9, 13.2)},
}


def parse_date(value):
    return datetime.date.fromisoformat(value)


# ---------------------------------------------------------------------------
# Additional patients
# The 50 hand-written patients above anchor the scenarios in the messages and
# request queue. The generator below adds a deterministic panel of extra
# patients so every clinician has a realistic daily schedule.
# ---------------------------------------------------------------------------

EXTRA_PATIENT_COUNT = 50

_FEMALE_NAMES = ["Ava", "Charlotte", "Harper", "Evelyn", "Natalie", "Grace", "Zoe", "Leah", "Audrey", "Claire",
                 "Lauren", "Rachel", "Julia", "Naomi", "Ruth", "Diane", "Carmen", "Rosa", "Mei", "Priya",
                 "Hana", "Leilani", "Elena", "Brooke", "Kendra"]
_MALE_NAMES = ["Liam", "Mason", "Logan", "Elijah", "Aiden", "Caleb", "Owen", "Isaac", "Nathan", "Gavin",
               "Spencer", "Derek", "Gordon", "Russell", "Hector", "Marco", "Tevita", "Arjun", "Wei", "Omar",
               "Dallin", "Tanner", "Brigham", "Felipe", "Grant"]
_LAST_NAMES = ["Larkin", "Hadley", "Pratt", "Okonkwo", "Bingham", "Romero", "Castillo-Ruiz", "Tuiasosopo",
               "Nakamura", "Petrov", "Sandoval", "Whitmore", "Ashby", "Kowalski", "Delacruz", "Fonua",
               "Morales", "Haskell", "Ivanova", "Lindgren", "Bautista", "Merrill", "Quintana", "Sato",
               "Abernathy", "Faleolo", "Osei", "Valdez", "Harlow", "Engstrom"]
_ADULT_CONDITION_POOL = ["htn", "hld", "t2dm", "prediabetes", "hypothyroid", "anxiety", "depression", "gerd",
                         "migraine", "asthma", "allergic_rhinitis", "knee_oa", "osteoporosis"]
_CHILD_CONDITION_POOL = ["asthma", "eczema", "allergic_rhinitis", "adhd"]
_PCP_BY_GROUP = {
    "adult": ["Marquez", "Desai", "Nguyen", "Kimball", "Bennett", "Sorensen", "Chen", "Haddad", "Petersen", "Wells",
              "Whitaker", "Okafor"],
    "child": ["Liu", "Tuilagi", "Holloway", "Castillo", "Marquez", "Sorensen"],
}
_PROVIDER_SPECIALTY = {row[1]: row[3] for row in PROVIDERS}


def _accepts(provider_last, plan_code):
    return plan_code in SPECIALTY_PLAN_RULES[_PROVIDER_SPECIALTY[provider_last]] or plan_code in PROVIDER_EXTRA_PLANS.get(
        f"{[r for r in PROVIDERS if r[1] == provider_last][0][0]}-{provider_last}".lower(), []
    )


def generate_additional_patients(count=EXTRA_PATIENT_COUNT):
    import random

    rng = random.Random(20261)
    taken = {(p[0], p[1]) for p in PATIENTS} | {(r[0], r[1]) for r in PROVIDERS}
    taken |= {(s[0], s[1]) for s in FRONT_OFFICE_STAFF} | {(a[0], a[1]) for a in AI_ENGINEERS}
    plan_codes = [code for code, *_ in INSURANCE_PLANS]
    plan_weights = [30, 14, 18, 14, 12, 10, 4]
    patients = []
    while len(patients) < count:
        sex = rng.choice("FM")
        first = rng.choice(_FEMALE_NAMES if sex == "F" else _MALE_NAMES)
        last = rng.choice(_LAST_NAMES)
        if (first, last) in taken:
            continue
        child = rng.random() < 0.22
        if child:
            dob = datetime.date(rng.randint(2011, 2022), rng.randint(1, 12), rng.randint(1, 28))
        else:
            dob = datetime.date(rng.randint(1942, 2006), rng.randint(1, 12), rng.randint(1, 28))
        plan = rng.choices(plan_codes, weights=plan_weights)[0]
        if plan == "redrock-advantage" and dob.year > 1961:
            plan = "silverpeak-ppo"
        candidates = [p for p in _PCP_BY_GROUP["child" if child else "adult"] if _accepts(p, plan)]
        if not candidates:
            continue
        pcp = rng.choice(candidates)
        if child:
            conditions = rng.sample(_CHILD_CONDITION_POOL, rng.choice([0, 1, 1, 2]))
        else:
            age = 2026 - dob.year
            pool = [c for c in _ADULT_CONDITION_POOL if not (c == "osteoporosis" and (sex == "M" or age < 55))]
            conditions = rng.sample(pool, rng.choice([0, 1, 1, 2, 2, 3]))
        specialist = None
        if not child and rng.random() < 0.2:
            specialist, extra = rng.choice([("Brooks", "nevi"), ("Grant", "acne"), ("Larsen", "knee_pain"),
                                             ("Patel", "plantar_fasciitis")])
            if _accepts(specialist, plan):
                conditions.append(extra)
            else:
                specialist = None
        allergies = [rng.choice(list(ALLERGIES))] if rng.random() < 0.25 else []
        language = "es" if pcp in ("Marquez", "Bennett", "Castillo") and rng.random() < 0.5 else "en"
        taken.add((first, last))
        patients.append((first, last, sex, dob.isoformat(), language, plan, pcp, conditions, allergies, specialist, ""))
    return patients


ALL_PATIENTS = PATIENTS + generate_additional_patients()
