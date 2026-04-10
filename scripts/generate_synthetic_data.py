"""Generate synthetic CSUN-like university data with known biases baked in."""
import csv
import random
import os

random.seed(42)

# CSUN-like demographics
RACES = ['Hispanic/Latino', 'White', 'Asian', 'Black/African American', 'Two or More', 'Other']
RACE_WEIGHTS = [0.61, 0.15, 0.10, 0.06, 0.05, 0.03]

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
    first_gen = random.random() < (0.55 if race == 'Hispanic/Latino' else 0.35)
    pell_eligible = random.random() < (0.65 if race == 'Hispanic/Latino' else 0.40)
    disability = random.random() < 0.12
    zip_code = pick_zip(race)

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
    }


def main():
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)

    filepath = os.path.join(data_dir, 'csun_synthetic_students.csv')
    students = [generate_student(i) for i in range(1, NUM_STUDENTS + 1)]

    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=students[0].keys())
        writer.writeheader()
        writer.writerows(students)

    print(f"Generated {NUM_STUDENTS} synthetic student records → {filepath}")

    # Quick stats
    hispanic = [s for s in students if s['race_ethnicity'] == 'Hispanic/Latino']
    white = [s for s in students if s['race_ethnicity'] == 'White']
    h_aid = sum(1 for s in hispanic if s['financial_aid_approved']) / len(hispanic)
    w_aid = sum(1 for s in white if s['financial_aid_approved']) / len(white)
    print(f"\nBias check — Aid approval rates:")
    print(f"  Hispanic/Latino: {h_aid:.1%}")
    print(f"  White:           {w_aid:.1%}")
    print(f"  Disparity ratio: {h_aid/w_aid:.2f}")


if __name__ == '__main__':
    main()
