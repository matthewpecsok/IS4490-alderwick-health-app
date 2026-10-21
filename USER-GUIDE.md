# Alderwick Family Health: User Guide

This guide explains how to sign in to the Alderwick Family Health web application and what each type of user can do. **Every person, record, and account in this application is fictional.** Never enter real personal or health information.

## Signing in

1. Start the application (see `README.md`). In GitHub Codespaces, open the forwarded port 8000.
2. Click **Sign in** in the top-right corner, or go to `/accounts/login/`.
3. Enter a username and password from the tables below.

You land on the right workspace for the account type automatically. Use **Sign out** before switching to a different account, or use a private browser window to stay signed in as two users at once.

## Passwords

Every account of the same type shares one password.

| Account type | Password | Lands on |
|---|---|---|
| Patient | `Patient2026!` | Patient portal (`/portal/`) |
| Front office | `FrontDesk2026!` | Front-office workspace (`/staff/front-office/`) |
| Doctor | `Doctor2026!` | Clinician workspace (`/staff/clinician/`) |
| AI engineer | `AIEngineer2026!` | AI operations workspace (`/staff/ai-operations/`) |
| Administrator | `Admin2026!` | Django admin (`/admin/`) |

## Quick start: one account of each type

| Type | Username | Why this account is a good place to start |
|---|---|---|
| Patient | `michael.anderson` | Has blood pressure and cholesterol history, a penicillin allergy, lab results, visit notes, an open appointment request, and a message thread |
| Patient | `luis.hernandez` | Spanish-speaking patient with diabetes, high blood pressure, and a question about his A1c results |
| Front office | `brittany.hale` | Front Office Supervisor at the Sugar House clinic |
| Doctor | `james.whitaker` | Family medicine physician with a full schedule today, unsigned notes, and patient messages |
| AI engineer | `nikhil.rao` | Access to the (currently empty) AI operations dashboard |

## What each user type can do

### Visitors (not signed in)

- Search for providers by specialty, location, insurance, language, gender, new-patient status, and video visits
- View provider profiles with availability, location pages with hours, accepted insurance, and patient resources (practice policies)
- Submit an appointment request

### Patients

- See upcoming and past appointments, and cancel online up to 24 hours before a visit
- Request appointments
- View their own health summary (allergies, conditions, medications), test results, and signed visit notes
- Send and reply to secure messages. Scheduling, billing, and records messages go to the front office. Prescription, test result, and medical questions go to the patient's primary care provider.

Patients can only ever see their own records.

### Front office

- Work the appointment request queue: review, add notes, decline, link to an existing patient, or schedule into an open slot (which registers new patients)
- View each location's daily schedule and check patients in, mark no-shows, or cancel
- Answer front-office patient messages
- Look up patients and book appointments by phone

Front-office staff see demographics, insurance, and appointments, but **not** clinical records.

### Doctors

- See today's schedule, unsigned notes, patient messages, and recent abnormal results
- Open the charts of patients they have a care relationship with (primary care patients, and anyone they have seen or scheduled)
- Write, save, and sign visit notes. Signing locks the note and releases the after-visit summary to the patient portal.
- Answer clinical messages assigned to them

Doctors cannot open charts of patients outside their care relationships. Every attempt is recorded in the audit log.

### AI engineers

- Access the AI operations workspace. It has no data yet, because the application has no AI features.

AI engineers cannot open the patient portal, front-office, or clinician workspaces.

## Accounts

### AI engineers

| Name | Username | Title |
|---|---|---|
| Nikhil Rao | `nikhil.rao` | AI Platform Engineer |
| Avery Collins | `avery.collins` | AI Operations Analyst |

### Front office

| Name | Username | Office | Title |
|---|---|---|---|
| Mei Tanaka | `mei.tanaka` | Alderwick Holladay Clinic | Patient Services Representative |
| Courtney Ward | `courtney.ward` | Alderwick Holladay Clinic | Referral Coordinator |
| Amber Christensen | `amber.christensen` | Alderwick Sandy Clinic | Patient Services Representative |
| Tyler Jacobsen | `tyler.jacobsen` | Alderwick Sandy Clinic | Patient Services Representative |
| Jordan Ellis | `jordan.ellis` | Alderwick Sugar House Clinic | Patient Services Representative |
| Brittany Hale | `brittany.hale` | Alderwick Sugar House Clinic | Front Office Supervisor |
| Tasha Morgan | `tasha.morgan` | Alderwick Sugar House Clinic | Patient Services Representative |
| Devon Price | `devon.price` | Alderwick Virtual Care | Virtual Care Coordinator |
| Rosa Delgado | `rosa.delgado` | Alderwick West Valley Clinic | Bilingual Patient Services Representative |
| Miguel Ortega | `miguel.ortega` | Alderwick West Valley Clinic | Bilingual Patient Services Representative |

### Doctors and other clinicians

All clinicians use the **Doctor** account type and password, including physician assistants (PA-C) and nurse practitioners.

| Name | Username | Specialty | New patients | Weekly schedule |
|---|---|---|---|---|
| Dr. Natalie Brooks, MD | `natalie.brooks` | Dermatology | Yes | Mon Sugar House, Wed Sandy, Thu Sugar House, Fri Sandy |
| Olivia Grant, PA-C | `olivia.grant` | Dermatology | Yes | Mon Sandy, Tue Virtual Care, Wed Sandy, Fri Virtual Care, Sat Sandy |
| Dr. Daniel Moreno, MD | `daniel.moreno` | Dermatology | No | Mon Holladay, Tue West Valley, Thu Holladay, Fri West Valley |
| Marcus Bennett, FNP-C | `marcus.bennett` | Family Medicine | Yes | Tue West Valley, Wed West Valley, Thu West Valley, Fri West Valley |
| Dr. Priyanka Desai, DO | `priyanka.desai` | Family Medicine | Yes | Mon Holladay, Tue Virtual Care, Thu Holladay, Fri Virtual Care |
| Rachel Kimball, PA-C | `rachel.kimball` | Family Medicine | Yes | Mon Sugar House, Tue Virtual Care, Wed Sugar House, Thu Virtual Care, Sat Sugar House |
| Dr. Elena Marquez, MD | `elena.marquez` | Family Medicine | Yes | Tue West Valley, Wed Virtual Care, Thu West Valley, Fri Virtual Care |
| Dr. Thomas Nguyen, MD | `thomas.nguyen` | Family Medicine | Yes | Mon Sandy, Tue Sandy, Wed Sandy, Fri Sandy |
| Dr. David Okafor, MD | `david.okafor` | Family Medicine | No | Mon Holladay, Tue Holladay, Thu Holladay, Fri Holladay |
| Dr. Hannah Sorensen, MD | `hannah.sorensen` | Family Medicine | Yes | Mon Sandy, Wed Sandy, Thu Sandy, Fri Sandy |
| Dr. James Whitaker, MD | `james.whitaker` | Family Medicine | No | Mon Sugar House, Wed Sugar House, Thu Sugar House, Fri Sugar House |
| Dr. Robert Chen, MD | `robert.chen` | Internal Medicine | Yes | Mon Holladay, Tue Holladay, Thu Holladay, Fri Holladay |
| Dr. Ibrahim Haddad, MD | `ibrahim.haddad` | Internal Medicine | Yes | Mon Sandy, Tue Sandy, Wed Sandy, Thu Sandy |
| Dr. Laura Petersen, MD | `laura.petersen` | Internal Medicine | Yes | Mon Sugar House, Tue Virtual Care, Wed Sugar House, Fri Virtual Care |
| Kathryn Wells, AGNP-C | `kathryn.wells` | Internal Medicine | Yes | Tue West Valley, Wed Virtual Care, Thu West Valley, Fri Virtual Care |
| Ana Castillo, CPNP | `ana.castillo` | Pediatrics | Yes | Mon West Valley, Wed Holladay, Thu West Valley, Fri Holladay |
| Dr. Megan Holloway, DO | `megan.holloway` | Pediatrics | Yes | Tue Sandy, Wed Sandy, Thu Sandy, Fri Sandy, Sat Sandy |
| Dr. Grace Liu, MD | `grace.liu` | Pediatrics | Yes | Mon Sugar House, Tue Sugar House, Wed Sugar House, Fri Sugar House |
| Dr. Samuel Tuilagi, MD | `samuel.tuilagi` | Pediatrics | Yes | Mon West Valley, Tue West Valley, Wed West Valley, Thu West Valley |
| Dr. Kevin Larsen, MD | `kevin.larsen` | Sports Medicine | Yes | Mon Holladay, Tue Sandy, Wed Holladay, Thu Sandy |
| Dr. Jasmine Patel, DO | `jasmine.patel` | Sports Medicine | Yes | Tue Sugar House, Wed Sugar House, Thu Sugar House, Fri Sugar House |
| Claire Donovan, WHNP-BC | `claire.donovan` | Women's Health | Yes | Mon Holladay, Tue Virtual Care, Wed Holladay, Fri Virtual Care |
| Leilani Fonoti, CNM | `leilani.fonoti` | Women's Health | Yes | Mon West Valley, Tue West Valley, Thu West Valley, Fri West Valley |
| Dr. Sarah Jensen, MD | `sarah.jensen` | Women's Health | Yes | Mon Sugar House, Wed Sugar House, Thu Sugar House, Fri Sugar House |

### Patients

| Patient | Username | Date of birth | Primary care | Insurance | Active conditions | Allergies |
|---|---|---|---|---|---|---|
| Brandon Adams | `brandon.adams` | 1994-09-09 | Rachel Kimball, PA-C | Self-pay | Anxiety | None |
| Fatima Ali (Arabic) | `fatima.ali` | 1996-04-04 | Dr. Haddad | SilverPeak PPO | Migraine | None |
| Megan Allen | `megan.allen` | 1988-05-29 | Rachel Kimball, PA-C | SilverPeak HMO Select | Depression, Migraine | Latex |
| Michael Anderson | `michael.anderson` | 1968-04-12 | Dr. Whitaker | SilverPeak PPO | Hypertension, High cholesterol | Penicillin |
| Elena Ashby | `elena.ashby` | 2006-03-26 | Kathryn Wells, AGNP-C | Lakeshore Employers Health EPO | Acne, GERD | None |
| Nicole Baker | `nicole.baker` | 1987-01-14 | Dr. Desai | Lakeshore Employers Health EPO | Hypothyroidism, Seasonal allergies | None |
| Brooke Bautista | `brooke.bautista` | 1946-05-13 | Dr. Haddad | SilverPeak PPO | Hypertension, Moles (skin checks), Seasonal allergies, Prediabetes | Shellfish |
| Julia Bautista | `julia.bautista` | 1964-08-01 | Rachel Kimball, PA-C | SilverPeak PPO | None | Peanuts |
| Kendra Bautista | `kendra.bautista` | 1951-11-23 | Dr. Okafor | Lakeshore Employers Health EPO | High cholesterol | None |
| Charlotte Bingham | `charlotte.bingham` | 1954-07-02 | Rachel Kimball, PA-C | Lakeshore Employers Health EPO | Migraine, Asthma, Knee pain, Prediabetes | None |
| Matthew Campbell | `matthew.campbell` | 1977-03-21 | Dr. Whitaker | Canyon Mutual Choice PPO | Hypertension | None |
| Emily Carter | `emily.carter` | 1992-06-14 | Dr. Desai | SilverPeak HMO Select | Asthma, Seasonal allergies | Peanuts |
| Hana Castillo-Ruiz (Spanish) | `hana.castillo-ruiz` | 1977-09-21 | Marcus Bennett, FNP-C | Canyon Mutual Choice PPO | Hypothyroidism, Type 2 diabetes | Latex |
| Zoe Castillo-Ruiz (Spanish) | `zoe.castillo-ruiz` | 1982-08-27 | Marcus Bennett, FNP-C | SilverPeak HMO Select | Prediabetes | Penicillin |
| William Clark | `william.clark` | 1972-08-27 | Dr. Petersen | SilverPeak PPO | High cholesterol, Type 2 diabetes | Codeine |
| Elizabeth Collins | `elizabeth.collins` | 1946-06-06 | Kathryn Wells, AGNP-C | Redrock Medicare Advantage | Osteoporosis, Hypertension, High cholesterol | Penicillin |
| Ashley Cook | `ashley.cook` | 1997-04-19 | Rachel Kimball, PA-C | Canyon Mutual Choice PPO | Anxiety, Asthma | Sulfamethoxazole |
| Alejandro Cruz (Spanish) | `alejandro.cruz` | 1999-05-16 | Dr. Marquez | Self-pay | None | None |
| Ruth Delacruz | `ruth.delacruz` | 1966-03-16 | Dr. Whitaker | Canyon Mutual Choice PPO | None | None |
| Abigail Edwards | `abigail.edwards` | 1991-12-24 | Claire Donovan, WHNP-BC | Lakeshore Employers Health EPO | Migraine | None |
| Dallin Engstrom | `dallin.engstrom` | 1988-07-27 | Dr. Whitaker | SilverPeak PPO | None | None |
| Evelyn Engstrom | `evelyn.engstrom` | 1958-09-21 | Dr. Whitaker | SilverPeak PPO | Asthma | None |
| Jacob Evans | `jacob.evans` | 1968-10-13 | Dr. Okafor | SilverPeak PPO | GERD, High cholesterol, Type 2 diabetes | Shellfish |
| Diane Fonua | `diane.fonua` | 1972-09-08 | Rachel Kimball, PA-C | SilverPeak PPO | Hypertension, Hypothyroidism | None |
| Gavin Fonua | `gavin.fonua` | 1995-10-12 | Dr. Desai | Beehive Community Health Plan | High cholesterol | None |
| Lauren Fonua | `lauren.fonua` | 1948-12-03 | Dr. Sorensen | Canyon Mutual Choice PPO | Type 2 diabetes | None |
| Spencer Fonua | `spencer.fonua` | 1977-08-06 | Dr. Okafor | SilverPeak PPO | Hypertension, Plantar fasciitis | None |
| Maria Gonzalez (Spanish) | `maria.gonzalez` | 1962-03-26 | Dr. Marquez | Beehive Community Health Plan | High cholesterol, Depression, Type 2 diabetes | None |
| Rebecca Green | `rebecca.green` | 1974-11-21 | Claire Donovan, WHNP-BC | SilverPeak PPO | Hypothyroidism | None |
| Joshua Hall | `joshua.hall` | 1976-07-07 | Dr. Sorensen | Canyon Mutual Choice PPO | Hypertension, Prediabetes | None |
| Elijah Harlow | `elijah.harlow` | 1968-07-21 | Marcus Bennett, FNP-C | Lakeshore Employers Health EPO | Migraine, Knee osteoarthritis | None |
| Harper Harlow | `harper.harlow` | 1983-11-26 | Dr. Whitaker | SilverPeak PPO | Anxiety, High cholesterol | None |
| Benjamin Harris | `benjamin.harris` | 1953-02-17 | Dr. Petersen | Redrock Medicare Advantage | Hypertension, Knee osteoarthritis, Type 2 diabetes | Codeine |
| Hana Haskell | `hana.haskell` | 1962-07-22 | Dr. Sorensen | Canyon Mutual Choice PPO | None | None |
| Naomi Haskell | `naomi.haskell` | 2001-10-23 | Dr. Nguyen | SilverPeak PPO | High cholesterol, Depression, Seasonal allergies | Codeine |
| Luis Hernandez (Spanish) | `luis.hernandez` | 1955-01-30 | Dr. Marquez | Beehive Community Health Plan | Hypertension, High cholesterol, Type 2 diabetes | Sulfamethoxazole |
| Hana Ivanova | `hana.ivanova` | 1995-03-04 | Dr. Petersen | SilverPeak HMO Select | Seasonal allergies | None |
| Daniel Kim | `daniel.kim` | 2001-07-19 | Dr. Okafor | SilverPeak PPO | None | None |
| Stephanie King | `stephanie.king` | 1981-08-15 | Rachel Kimball, PA-C | Canyon Mutual Choice PPO | Psoriasis | None |
| Christopher Lee | `christopher.lee` | 1983-04-17 | Dr. Nguyen | SilverPeak PPO | GERD | None |
| Hannah Lewis | `hannah.lewis` | 1998-07-25 | Dr. Sorensen | SilverPeak HMO Select | Anxiety, Seasonal allergies | None |
| Brigham Lindgren | `brigham.lindgren` | 1992-11-09 | Dr. Desai | Canyon Mutual Choice PPO | None | Shellfish |
| Sophia Martinez (Spanish) | `sophia.martinez` | 1995-12-01 | Leilani Fonoti, CNM | Beehive Community Health Plan | Pregnancy (prenatal care) | None |
| Robert Mitchell | `robert.mitchell` | 1949-11-02 | Dr. Chen | Redrock Medicare Advantage | Hypertension, GERD, Knee osteoarthritis | None |
| Mason Morales | `mason.morales` | 2006-03-18 | Dr. Haddad | SilverPeak PPO | Anxiety, Knee pain | None |
| Ryan Murphy | `ryan.murphy` | 1989-08-08 | Dr. Whitaker | SilverPeak PPO | None | None |
| Elena Nakamura | `elena.nakamura` | 1952-05-26 | Dr. Desai | Beehive Community Health Plan | Migraine | None |
| Leilani Nakamura | `leilani.nakamura` | 2005-11-03 | Dr. Okafor | Beehive Community Health Plan | None | None |
| Mason Nakamura | `mason.nakamura` | 1942-11-10 | Dr. Marquez | Self-pay | Knee osteoarthritis | Shellfish |
| Nathan Nakamura | `nathan.nakamura` | 2000-03-24 | Dr. Desai | SilverPeak PPO | Depression, Asthma | None |
| Hana Okonkwo | `hana.okonkwo` | 1973-09-21 | Dr. Haddad | SilverPeak PPO | Type 2 diabetes | None |
| Felipe Osei | `felipe.osei` | 1993-09-19 | Dr. Desai | SilverPeak HMO Select | Hypertension, Seasonal allergies, Prediabetes | None |
| Logan Osei | `logan.osei` | 2002-10-11 | Rachel Kimball, PA-C | SilverPeak HMO Select | High cholesterol | None |
| Emma Parker | `emma.parker` | 2000-01-08 | Dr. Sorensen | SilverPeak HMO Select | Acne | None |
| Samuel Phillips | `samuel.phillips` | 1980-05-05 | Dr. Nguyen | SilverPeak PPO | Psoriasis | None |
| Harper Pratt | `harper.pratt` | 2002-04-18 | Rachel Kimball, PA-C | SilverPeak PPO | Depression | None |
| Leah Pratt (Spanish) | `leah.pratt` | 1987-12-12 | Marcus Bennett, FNP-C | SilverPeak PPO | Asthma, Prediabetes | None |
| Gordon Quintana | `gordon.quintana` | 1955-01-08 | Dr. Okafor | SilverPeak PPO | Hypertension, Asthma, Plantar fasciitis | Codeine |
| Aisha Rahman (Arabic) | `aisha.rahman` | 1986-03-08 | Dr. Haddad | Lakeshore Employers Health EPO | Hypothyroidism | None |
| Jose Ramirez (Spanish) | `jose.ramirez` | 1970-06-02 | Marcus Bennett, FNP-C | Beehive Community Health Plan | Hypertension, Type 2 diabetes | Penicillin |
| Samantha Reed | `samantha.reed` | 1983-10-22 | Dr. Desai | SilverPeak HMO Select | Moles (skin checks) | None |
| Tyler Robinson | `tyler.robinson` | 2003-10-10 | Dr. Sorensen | Canyon Mutual Choice PPO | Plantar fasciitis | None |
| Jonathan Rogers | `jonathan.rogers` | 1975-01-31 | Dr. Desai | Lakeshore Employers Health EPO | Hypertension, Prediabetes | None |
| Elijah Sandoval | `elijah.sandoval` | 2003-03-28 | Dr. Desai | SilverPeak PPO | Depression, Moles (skin checks), Knee osteoarthritis | Shellfish |
| Kevin Scott | `kevin.scott` | 1999-03-03 | Rachel Kimball, PA-C | SilverPeak HMO Select | Knee pain | None |
| Margaret Sullivan | `margaret.sullivan` | 1952-09-09 | Dr. Petersen | Redrock Medicare Advantage | Osteoporosis, GERD, Hypothyroidism | None |
| Sione Taufa | `sione.taufa` | 1984-02-28 | Marcus Bennett, FNP-C | Beehive Community Health Plan | Hypertension, Type 2 diabetes | None |
| Jennifer Thompson | `jennifer.thompson` | 1979-09-23 | Rachel Kimball, PA-C | Canyon Mutual Choice PPO | Anxiety, Migraine | None |
| Lucia Torres (Spanish) | `lucia.torres` | 1985-09-17 | Marcus Bennett, FNP-C | Beehive Community Health Plan | Depression, Prediabetes | None |
| Vinh Tran (Vietnamese) | `vinh.tran` | 1960-07-14 | Dr. Nguyen | Redrock Medicare Advantage | Hypertension, GERD, High cholesterol | None |
| Dallin Tuiasosopo | `dallin.tuiasosopo` | 1951-12-28 | Dr. Okafor | SilverPeak PPO | Asthma, Knee osteoarthritis, Seasonal allergies | None |
| Chloe Turner | `chloe.turner` | 1993-11-30 | Dr. Jensen | Lakeshore Employers Health EPO | Pregnancy (prenatal care) | None |
| Rachel Valdez | `rachel.valdez` | 1954-12-10 | Dr. Desai | SilverPeak HMO Select | None | None |
| Amanda Walker | `amanda.walker` | 1990-02-11 | Dr. Jensen | Lakeshore Employers Health EPO | PCOS | None |
| Kenji Watanabe | `kenji.watanabe` | 1958-08-11 | Dr. Chen | Redrock Medicare Advantage | Hypertension, High cholesterol | None |
| Gordon Whitmore | `gordon.whitmore` | 1951-08-07 | Dr. Nguyen | Beehive Community Health Plan | Hypothyroidism, Seasonal allergies, Prediabetes | None |
| Leilani Whitmore | `leilani.whitmore` | 1965-04-06 | Dr. Chen | SilverPeak PPO | Hypertension, Knee osteoarthritis, Type 2 diabetes | None |
| Rosa Whitmore | `rosa.whitmore` | 1982-11-19 | Dr. Haddad | SilverPeak PPO | High cholesterol, Depression | Penicillin |
| Andrew Wright | `andrew.wright` | 1965-12-19 | Dr. Okafor | SilverPeak PPO | GERD, High cholesterol | None |
| Patricia Young | `patricia.young` | 1958-10-05 | Kathryn Wells, AGNP-C | Redrock Medicare Advantage | Osteoporosis, Hypertension, Hypothyroidism | Sulfamethoxazole |

### Pediatric patients (no portal account)

These patients are minors. Their records are visible to their care team and front office, but they do not have portal accounts.

| Patient | Date of birth | Parent or guardian | Primary care | Active conditions |
|---|---|---|---|---|
| Arjun Abernathy | 2019-01-14 | Brian Abernathy | Dr. Liu | ADHD |
| Leah Ashby | 2016-11-27 | David Ashby | Ana Castillo, CPNP | Seasonal allergies |
| Ethan Brown | 2012-02-22 | Teresa Brown | Dr. Holloway | ADHD, Seasonal allergies |
| Kendra Castillo-Ruiz | 2015-06-03 | Angela Castillo-Ruiz | Dr. Holloway | Seasonal allergies |
| Lucas Fifita | 2016-01-25 | Brian Fifita | Dr. Tuilagi | Asthma |
| Derek Fonua | 2014-03-08 | Teresa Fonua | Ana Castillo, CPNP | ADHD |
| Isabella Garcia | 2018-09-03 | Mark Garcia | Dr. Tuilagi | Eczema |
| Mei Hadley | 2016-08-10 | Karen Hadley | Dr. Holloway | Seasonal allergies |
| Grant Harlow | 2011-05-23 | Karen Harlow | Ana Castillo, CPNP | None |
| Natalie Harlow | 2017-01-05 | Karen Harlow | Dr. Holloway | ADHD |
| Elena Haskell | 2012-03-07 | Steven Haskell | Dr. Sorensen | None |
| Carmen Lindgren | 2020-06-08 | David Lindgren | Ana Castillo, CPNP | Eczema, Asthma |
| Diane Lindgren | 2018-11-26 | Mark Lindgren | Dr. Tuilagi | Eczema |
| Olivia Nguyen | 2015-05-10 | Brian Nguyen | Dr. Liu | Eczema, Asthma |
| Elena Quintana | 2014-08-12 | Angela Quintana | Dr. Tuilagi | ADHD |
| Mia Taylor | 2010-06-30 | Steven Taylor | Dr. Holloway | Acne, Anxiety |
| Leilani Valdez | 2016-08-28 | Brian Valdez | Dr. Holloway | Eczema, Asthma |
| Marco Whitmore | 2012-09-05 | Susan Whitmore | Dr. Liu | Asthma |
| Noah Wilson | 2019-11-15 | Brian Wilson | Ana Castillo, CPNP | None |
| Lily Zhang | 2014-08-19 | Paul Zhang | Dr. Liu | Seasonal allergies |

### Administrator

| Username | Password | Purpose |
|---|---|---|
| `admin` | `Admin2026!` | Django admin at `/admin/`, for inspecting or correcting data, including the read-only audit log |

## About the data

- **Dates move with you.** When the database is loaded, appointments, visits, messages, and requests are generated relative to that moment. "Today's schedule" always has patients in it. Reload the data (see `README.md`) to refresh the dates.
- **Names and accounts never change.** Reloading the data recreates the same people, usernames, and medical record numbers.
- **Logs.** Application requests are written to `logs/alderwick.log`. Security and patient-data access events are written to `logs/audit.log` and stored in the database.
