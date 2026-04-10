"""Generate synthetic CSUN-like university data with known biases baked in."""
import csv
import random
import os

random.seed(42)

# ---------------------------------------------------------------------------
# DATA SOURCES — where each number comes from
# ---------------------------------------------------------------------------
DATA_SOURCES = {
    'demographics': {
        'race_weights': 'CSUN Institutional Research — csun.edu/counts/demographic.php (Fall 2024)',
        'gender_weights': 'CSUN Fact Sheet — csun.edu/about/facts',
        'pell_eligible': 'US Dept of Education College Scorecard — collegescorecard.ed.gov (CSUN entry)',
        'first_generation': 'CSUN Fact Sheet — csun.edu/about/facts (47% first-gen)',
        'disability': 'IPEDS/NCES — nces.ed.gov/ipeds/ (national average ~12%)',
    },
    'outcomes': {
        'financial_aid': 'College Scorecard + CSUN Financial Aid Office',
        'stem_rec': 'Simulated bias based on STEM equity literature',
        'plagiarism': 'Simulated bias based on academic integrity disparity research',
        'admissions': 'Simulated bias; base rates from CSUN Institutional Research',
        'at_risk_flag': 'Simulated bias; retention data from CSU System Data Center — calstate.edu/data-center',
        'scholarship': 'Simulated bias; merit-aid patterns from College Scorecard',
        'competitive_program_rec': 'Simulated bias; advising quality disparities from IPEDS/NCES',
    },
}

# CSUN demographics (updated to match real CSUN data)
RACES = ['Hispanic/Latino', 'White', 'Asian', 'Black/African American', 'Two or More', 'Other']
RACE_WEIGHTS = [0.562, 0.178, 0.105, 0.053, 0.042, 0.060]

GENDERS = ['Female', 'Male', 'Non-binary']
GENDER_WEIGHTS = [0.55, 0.43, 0.02]

# Zip codes with racial correlation baked in
ZIP_PROFILES = {
    'high_hispanic': ['91331', '91343', '91340', '91402', '91605'],
    'mixed': ['91324', '91325', '91326', '91344', '91406'],
    'low_hispanic': ['91302', '91361', '91362', '91436', '91364'],
}

NUM_STUDENTS = 5000


def pick_zip(race):
    if race == 'Hispanic/Latino':
        pool = random.choices(
            ['high_hispanic', 'mixed', 'low_hispanic'],
            weights=[0.6, 0.3, 0.1]
        )[0]
    elif race == 'White':
        pool = random.choices(
            ['high_hispanic', 'mixed', 'low_hispanic'],
            weights=[0.15, 0.35, 0.5]
        )[0]
    else:
        pool = random.choices(
            ['high_hispanic', 'mixed', 'low_hispanic'],
            weights=[0.3, 0.4, 0.3]
        )[0]
    return random.choice(ZIP_PROFILES[pool])


def generate_student(student_id):
    race = random.choices(RACES, weights=RACE_WEIGHTS)[0]
    gender = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
    first_gen = random.random() < 0.47
    pell_eligible = random.random() < 0.58
    disability = random.random() < 0.12
    zip_code = pick_zip(race)

    # Correlate first-gen / pell with race (systemic factor)
    if race == 'Hispanic/Latino':
        if not first_gen:
            first_gen = random.random() < 0.15  # bump up
        if not pell_eligible:
            pell_eligible = random.random() < 0.12

    # GPA with slight demographic variation (simulating systemic factors)
    base_gpa = random.gauss(2.95, 0.55)
    if first_gen:
        base_gpa -= 0.1
    if pell_eligible:
        base_gpa -= 0.05
    gpa = max(0.0, min(4.0, round(base_gpa, 2)))

    # "Predicted persistence" — intentionally biased proxy
    persistence = 0.5 + gpa * 0.1
    if zip_code in ZIP_PROFILES['high_hispanic']:
        persistence -= 0.12  # <-- THIS IS THE BIAS
    if first_gen:
        persistence -= 0.08
    persistence = max(0, min(1, round(persistence + random.gauss(0, 0.08), 3)))

    # Financial aid decision — based on biased persistence score
    threshold = 0.55
    aid_approved = persistence >= threshold

    # Course recommendation quality — slight bias in STEM recs
    stem_rec_quality = random.gauss(0.80, 0.10)
    if race == 'Hispanic/Latino':
        stem_rec_quality -= 0.07  # <-- BIAS: worse STEM recs for Hispanic students
    if gender == 'Female':
        stem_rec_quality -= 0.04  # <-- BIAS: gender gap in STEM recs
    stem_rec_quality = max(0, min(1, round(stem_rec_quality, 3)))

    # Plagiarism flag rate
    flag_rate = random.gauss(0.05, 0.02)
    if race in ['Hispanic/Latino', 'Asian']:
        flag_rate += 0.03  # <-- BIAS: higher flag rate for non-native English speakers
    plagiarism_flagged = random.random() < max(0, flag_rate)

    # --- NEW OUTCOME: Admissions screening ---
    # Bias: first-gen students 8% lower, Pell-eligible 5% lower
    admit_prob = 0.72
    if first_gen:
        admit_prob -= 0.08  # <-- BIAS
    if pell_eligible:
        admit_prob -= 0.05  # <-- BIAS
    admitted = random.random() < admit_prob

    # --- NEW OUTCOME: At-risk flag (course completion prediction) ---
    # Bias: Hispanic students flagged 15% more often than white students
    at_risk_base = 0.20
    if race == 'Hispanic/Latino':
        at_risk_base += 0.15  # <-- BIAS
    elif race == 'Black/African American':
        at_risk_base += 0.08
    if first_gen:
        at_risk_base += 0.05
    at_risk_flag = random.random() < at_risk_base

    # --- NEW OUTCOME: Scholarship awarded ---
    # Bias: merit-based favors higher-income zip codes
    scholarship_prob = 0.25
    if gpa >= 3.5:
        scholarship_prob += 0.20
    if zip_code in ZIP_PROFILES['low_hispanic']:
        scholarship_prob += 0.12  # <-- BIAS: high-income zips favored
    elif zip_code in ZIP_PROFILES['high_hispanic']:
        scholarship_prob -= 0.08  # <-- BIAS: low-income zips penalized
    scholarship_awarded = random.random() < max(0, min(1, scholarship_prob))

    # --- NEW OUTCOME: Competitive program recommendation quality ---
    # Bias: Hispanic -0.06, Black -0.04, Female -0.03
    comp_rec = random.gauss(0.72, 0.12)
    if race == 'Hispanic/Latino':
        comp_rec -= 0.06  # <-- BIAS
    elif race == 'Black/African American':
        comp_rec -= 0.04  # <-- BIAS
    if gender == 'Female':
        comp_rec -= 0.03  # <-- BIAS
    competitive_program_rec = max(0, min(1, round(comp_rec, 3)))

    return {
        'student_id': f'CSUN{student_id:05d}',
        'race_ethnicity': race,
        'gender': gender,
        'first_generation': first_gen,
        'pell_eligible': pell_eligible,
        'disability_status': disability,
        'zip_code': zip_code,
        'gpa': gpa,
        'predicted_persistence': persistence,
        'financial_aid_approved': aid_approved,
        'stem_rec_quality': stem_rec_quality,
        'plagiarism_flagged': plagiarism_flagged,
        'admitted': admitted,
        'at_risk_flag': at_risk_flag,
        'scholarship_awarded': scholarship_awarded,
        'competitive_program_rec': competitive_program_rec,
    }


def print_bias_summary(students):
    """Print bias summary for ALL outcome columns."""
    races = {}
    for s in students:
        r = s['race_ethnicity']
        if r not in races:
            races[r] = []
        races[r].append(s)

    genders = {}
    for s in students:
        g = s['gender']
        if g not in genders:
            genders[g] = []
        genders[g].append(s)

    def rate(group, key):
        return sum(1 for s in group if s[key]) / len(group) if group else 0

    def avg(group, key):
        vals = [s[key] for s in group]
        return sum(vals) / len(vals) if vals else 0

    print("\n=== BIAS SUMMARY (by race/ethnicity) ===\n")

    outcomes_bool = [
        ('financial_aid_approved', 'Financial Aid Approved'),
        ('admitted', 'Admitted'),
        ('at_risk_flag', 'At-Risk Flagged'),
        ('scholarship_awarded', 'Scholarship Awarded'),
        ('plagiarism_flagged', 'Plagiarism Flagged'),
    ]
    outcomes_cont = [
        ('stem_rec_quality', 'STEM Rec Quality'),
        ('competitive_program_rec', 'Competitive Program Rec'),
    ]

    for key, label in outcomes_bool:
        print(f"  {label}:")
        for r in RACES:
            if r in races:
                print(f"    {r:30s} {rate(races[r], key):.1%}")
        if 'Hispanic/Latino' in races and 'White' in races:
            h = rate(races['Hispanic/Latino'], key)
            w = rate(races['White'], key)
            ratio = h / w if w > 0 else float('inf')
            print(f"    {'Disparity ratio (H/W)':30s} {ratio:.3f}")
        print()

    for key, label in outcomes_cont:
        print(f"  {label} (mean):")
        for r in RACES:
            if r in races:
                print(f"    {r:30s} {avg(races[r], key):.3f}")
        print()

    print("=== BIAS SUMMARY (by gender) ===\n")
    for key, label in outcomes_bool:
        print(f"  {label}:")
        for g in GENDERS:
            if g in genders:
                print(f"    {g:15s} {rate(genders[g], key):.1%}")
        print()

    for key, label in outcomes_cont:
        print(f"  {label} (mean):")
        for g in GENDERS:
            if g in genders:
                print(f"    {g:15s} {avg(genders[g], key):.3f}")
        print()


def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    filepath = os.path.join(data_dir, 'csun_synthetic_students.csv')
    students = [generate_student(i) for i in range(1, NUM_STUDENTS + 1)]

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=students[0].keys())
        writer.writeheader()
        writer.writerows(students)

    print(f"Generated {NUM_STUDENTS} synthetic student records -> {filepath}")
    print_bias_summary(students)


if __name__ == '__main__':
    main()
