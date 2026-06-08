import zipfile
import os

# Create test directory and files
os.makedirs('batch_test', exist_ok=True)

# Question file
with open('batch_test/question.txt', 'w', encoding='utf-8') as f:
    f.write('What is photosynthesis? Explain the process and its importance.')

# Student answers
student_answers = {
    'student1_answer.txt': 'Photosynthesis is how plants make food. They use sunlight, water and CO2 to make glucose and oxygen. This happens in chloroplasts.',
    'student2_answer.txt': 'Plants convert light energy to chemical energy through photosynthesis. The process requires chlorophyll, sunlight, carbon dioxide and water.',
    'student3_answer.txt': 'Photosynthesis is the biochemical process where green plants use sunlight to synthesize foods from CO2 and water, releasing oxygen as byproduct.',
    'student4_answer.txt': 'In photosynthesis, plants absorb light energy using chlorophyll pigments. This energy drives the conversion of carbon dioxide and water into glucose molecules while releasing oxygen gas.',
    'student5_answer.txt': 'Photosynthesis occurs in two stages: light-dependent reactions and Calvin cycle. Plants capture solar energy to produce ATP and NADPH, then use these to fix carbon dioxide into sugars.'
}

for filename, content in student_answers.items():
    with open(f'batch_test/{filename}', 'w', encoding='utf-8') as f:
        f.write(content)

# Create ZIP file
with zipfile.ZipFile('batch_test.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk('batch_test'):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, 'batch_test')
            zipf.write(file_path, arcname)

print("✅ Created batch_test.zip successfully!")
print("\nContents:")
with zipfile.ZipFile('batch_test.zip', 'r') as zipf:
    for name in zipf.namelist():
        print(f"  - {name}")
