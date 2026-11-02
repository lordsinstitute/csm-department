import pandas as pd

students = pd.read_csv("data/students.csv")
subjects = pd.read_csv("data/subjects.csv")
registrations = pd.read_csv("data/registrations.csv")

print("Students:", len(students))
print("Subjects:", len(subjects))
print("Registrations:", len(registrations))