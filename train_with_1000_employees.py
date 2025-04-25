"""
Script to generate 1000 employees and train the recommendation model.
"""
import os
import sys
import subprocess

def run_command(command):
    """Run a command and print its output"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(f"Error: {result.stderr}")
        
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result.returncode == 0

def main():
    print("=" * 80)
    print("TRAINING THE RECOMMENDATION MODEL WITH 1000 EMPLOYEE INSTANCES")
    print("=" * 80)
    
    # Step 1: Generate 1000 employees
    print("\nStep 1: Generating 1000 employee instances...")
    run_command("python src/scripts/generate_1000_employees.py")
    
    # Step 2: Train the model with the generated employees
    print("\nStep 2: Training the recommendation model...")
    run_command("python src/scripts/train_employee_model.py")
    
    # Step 3: Test the model with your custom skills
    print("\nStep 3: Testing the model with custom skills...")
    run_command("python test_with_skills.py")
    
    print("\n" + "=" * 80)
    print("TRAINING AND TESTING COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    main() 