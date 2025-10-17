def input_marks(n): 
    marks = [] 
    for i in range(n): 
        mark = int(input(f"Enter mark {i+1}: ")) 
        marks.append(mark) 
    return marks 
 
def calculate_average(marks): 
    total = sum(marks) 
    average = total / len(marks) 
    return average 
 
def find_extremes(marks): 
    highest = max(marks) 
    lowest = min(marks) 
    return highest, lowest 
 
print("Student Marks Analysis") 
num_subjects = int(input("Enter number of subjects: ")) 
student_marks = input_marks(num_subjects) 
avg = calculate_average(student_marks) 
print(f"\nAverage Marks: {avg:.2f}") 
high, low = find_extremes(student_marks) 
print(f"Highest Mark: {high}") 
print(f"Lowest Mark: {low}") 