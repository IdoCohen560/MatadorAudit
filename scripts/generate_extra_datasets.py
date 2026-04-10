"""Generate high-bias and fair CSUN datasets for demo comparison."""
import csv
import random
import os

random.seed(99)

RACES = ['Hispanic/Latino', 'White', 'Asian', 'Black/African American', 'Two or More', 'Other']
RACE_WEIGHTS = [0.562, 0.178, 0.105, 0.053, 0.042, 0.060]

GENDERS = ['Female', 'Male', 'Non-binary']
GENDER_WEIGHTS = [0.55, 0.43, 0.02]

ZIP_PROFILES = {
    'high_hispanic': ['91331', '91343', '91340', '91402', '91605'],
    'mixed': ['91324', '91325', '91326', '91344', '91406'],
    'low_hispanic': ['91302', '91361', '91362', '91436', '91364'],
}

NUM_STUDENTS = 5000


def pick_zip(race):
    if race == 'Hispanic/Latino':
        pool = random.choices(['high_hispanic', 'mixed', 'low_hispanic'], weights=[0.6, 0.3, 0.1])[0]
    elif race == 'White':
        pool = random.choices(['high_hispanic', 'mixed', 'low_hispanic'], weights=[0.15, 0.35, 0.5])[0]
    else:
        pool = random.choices(['high_hispanic', 'mixed', 'low_hispanic'], weights=[0.3, 0.4, 0.3])[0]
    return random.choice(ZIP_PROFILES[pool])


def generate_high_bias(student_id):
    """Generate a student record with SEVERE biases."""
    race = random.choices(RACES, weights=RACE_WEIGHTS)[0]
    gender = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
    first_gen = random.random() < 0.47
    pell_eligible = random.random() < 0.58
    disability = random.random() < 0.12
    zip_code = pick_zip(race)

    if race == 'Hispanic/Latino':
        if not first_gen:
            first_gen = random.random() < 0.15
        if not pell_eligible:
            pell_eligible = random.random() < 0.12

    base_gpa = random.gauss(2.95, 0.55)
    if first_gen:
        base_gpa -= 0.1
    if pell_eligible:
        base_gpa -= 0.05
    gpa = max(0.0, min(4.0, round(base_gpa, 2)))

    persistence = 0.5 + gpa * 0.1
    if zip_code in ZIP_PROFILES['high_hispanic']:
        persistence -= 0.18
    if first_gen:
        persistence -= 0.12
    persistence = max(0, min(1, round(persistence + random.gauss(0, 0.08), 3)))

    # Financial aid: Hispanic approval 20% lower than white
    aid_base = 0.70
    if race == 'Hispanic/Latino':
        aid_base -= 0.20
    elif race == 'Black/African American':
        aid_base -= 0.10
    financial_aid_approved = random.random() < aid_base

    # STEM recs: Hispanic -0.15, Female -0.10
    stem_rec_quality = random.gauss(0.80, 0.10)
    if race == 'Hispanic/Latino':
        stem_rec_quality -= 0.15
    if gender == 'Female':
        stem_rec_quality -= 0.10
    stem_rec_quality = max(0, min(1, round(stem_rec_quality, 3)))

    # Plagiarism: Hispanic/Asian flagged at 3x the rate
    flag_rate = 0.05
    if race in ['Hispanic/Latino', 'Asian']:
        flag_rate *= 3.0
    plagiarism_flagged = random.random() < flag_rate

    # Admissions: first-gen 15% lower, Pell 10% lower
    admit_prob = 0.72
    if first_gen:
        admit_prob -= 0.15
    if pell_eligible:
        admit_prob -= 0.10
    admitted = random.random() < max(0, admit_prob)

    # At-risk: Hispanic flagged 25% more
    at_risk_base = 0.20
    if race == 'Hispanic/Latino':
        at_risk_base += 0.25
    elif race == 'Black/African American':
        at_risk_base += 0.15
    if first_gen:
        at_risk_base += 0.08
    at_risk_flag = random.random() < min(1, at_risk_base)

    # Scholarships: high-Hispanic zips penalized -0.20
    scholarship_prob = 0.25
    if gpa >= 3.5:
        scholarship_prob += 0.20
    if zip_code in ZIP_PROFILES['high_hispanic']:
        scholarship_prob -= 0.20
    elif zip_code in ZIP_PROFILES['low_hispanic']:
        scholarship_prob += 0.15
    scholarship_awarded = random.random() < max(0, min(1, scholarship_prob))

    # Advising: Hispanic -0.12, Black -0.08
    comp_rec = random.gauss(0.72, 0.12)
    if race == 'Hispanic/Latino':
        comp_rec -= 0.12
    elif race == 'Black/African American':
        comp_rec -= 0.08
    if gender == 'Female':
        comp_rec -= 0.05
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
        'financial_aid_approved': financial_aid_approved,
        'stem_rec_quality': stem_rec_quality,
        'plagiarism_flagged': plagiarism_flagged,
        'admitted': admitted,
        'at_risk_flag': at_risk_flag,
        'scholarship_awarded': scholarship_awarded,
        'competitive_program_rec': competitive_program_rec,
    }


def generate_fair(student_id):
    """Generate a student record with NO systematic bias."""
    race = random.choices(RACES, weights=RACE_WEIGHTS)[0]
    gender = random.choices(GENDERS, weights=GENDER_WEIGHTS)[0]
    first_gen = random.random() < 0.47
    pell_eligible = random.random() < 0.58
    disability = random.random() < 0.12
    zip_code = pick_zip(race)

    base_gpa = random.gauss(2.95, 0.55)
    gpa = max(0.0, min(4.0, round(base_gpa, 2)))

    # Persistence — no demographic bias
    persistence = 0.5 + gpa * 0.1
    persistence = max(0, min(1, round(persistence + random.gauss(0, 0.08), 3)))

    # Financial aid — equal for all
    financial_aid_approved = persistence >= 0.55

    # STEM recs — equal for all
    stem_rec_quality = max(0, min(1, round(random.gauss(0.80, 0.10), 3)))

    # Plagiarism — equal base rate
    plagiarism_flagged = random.random() < 0.05

    # Admissions — equal for all
    admitted = random.random() < 0.72

    # At-risk — equal for all
    at_risk_flag = random.random() < 0.20

    # Scholarships — GPA-based only, no zip bias
    scholarship_prob = 0.25
    if gpa >= 3.5:
        scholarship_prob += 0.20
    scholarship_awarded = random.random() < scholarship_prob

    # Advising — equal for all
    competitive_program_rec = max(0, min(1, round(random.gauss(0.72, 0.12), 3)))

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
        'financial_aid_approved': financial_aid_approved,
        'stem_rec_quality': stem_rec_quality,
        'plagiarism_flagged': plagiarism_flagged,
        'admitted': admitted,
        'at_risk_flag': at_risk_flag,
        'scholarship_awarded': scholarship_awarded,
        'competitive_program_rec': competitive_program_rec,
    }


def write_dataset(students, filepath):
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=students[0].keys())
        writer.writeheader()
        writer.writerows(students)
    print(f"Generated {len(students)} records -> {filepath}")


def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    # High bias dataset
    random.seed(99)
    high_bias = [generate_high_bias(i) for i in range(1, NUM_STUDENTS + 1)]
    write_dataset(high_bias, os.path.join(data_dir, 'csun_high_bias.csv'))

    # Fair dataset
    random.seed(77)
    fair = [generate_fair(i) for i in range(1, NUM_STUDENTS + 1)]
    write_dataset(fair, os.path.join(data_dir, 'csun_fair.csv'))


if __name__ == '__main__':
    main()
