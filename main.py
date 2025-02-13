from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from answer_generator import main as generate_answers
import time
import json
import argparse

class NPTELLogin:
    def __init__(self, username, password, base_url, assign_num):
        self.username = username
        self.password = password
        self.driver = None
        self.base_url = base_url
        self.assign_num = assign_num

    def setup_driver(self):
        try:
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.maximize_window()
            return True
        except Exception as e:
            print(f"Driver setup failed: {str(e)}")
            return False

    def wait_for_azure_login_page(self, timeout=20):
        """Wait for Azure B2C login page to load"""
        try:
            print("Waiting for Azure B2C login page...")
            WebDriverWait(self.driver, timeout).until(
                lambda driver: "swayamopenid.b2clogin.com" in driver.current_url
            )
            print("Azure B2C login page loaded")
            return True
        except TimeoutException:
            print("Timed out waiting for Azure B2C login page")
            return False

    def get_questions(self):
        try:
            print("Waiting for assessment content to load...")
            # Wait for the main assessment container
            assessment_content = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "gcb-assessment-contents"))
            )

            # Find all question containers
            question_containers = self.driver.find_elements(By.CLASS_NAME, "qt-mc-question")
            
            # Initialize list to store all question data
            all_questions = []
            
            # Process each question
            for i, container in enumerate(question_containers, 1):
                question_text = container.find_element(By.CLASS_NAME, "qt-question").text.strip()
                
                # Find the MCQ choices within this specific container
                choices = container.find_elements(By.CLASS_NAME, "gcb-mcq-choice")
                
                # Extract options and their input IDs
                options = []
                for choice in choices:
                    try:
                        label = choice.find_element(By.TAG_NAME, "label")
                        input_element = choice.find_element(By.TAG_NAME, "input")
                        input_id = input_element.get_attribute("id")
                        
                        options.append({
                            "text": label.text.strip(),
                            "input_id": input_id
                        })
                    except NoSuchElementException:
                        continue
                
                # Create question dictionary
                question_data = {
                    "question_number": i,
                    "question_text": question_text,
                    "options": options
                }
                
                all_questions.append(question_data)

            # Save to JSON file with assignment number
            json_filename = f"questions_{self.assign_num}.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump(all_questions, f, indent=4)

            # Save to text file for human reading
            txt_filename = f"questions_{self.assign_num}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f:
                for q in all_questions:
                    f.write(f"Question {q['question_number']}:\n")
                    f.write(f"{q['question_text']}\n\n")
                    f.write("Options:\n")
                    for idx, option in enumerate(q['options'], 1):
                        f.write(f"{idx}. {option['text']} (ID: {option['input_id']})\n")
                    f.write("\n" + "="*50 + "\n\n")

            print(f"Successfully extracted {len(all_questions)} questions and saved to {json_filename} and {txt_filename}")
            return all_questions

        except TimeoutException:
            print("Timed out waiting for assessment content")
            return False
        except Exception as e:
            print(f"Error extracting questions: {str(e)}")
            return False

    def login(self):
        try:
            print(f"Navigating to NPTEL: {self.base_url}")
            self.driver.get(self.base_url)
            
            # Wait for redirect to Azure B2C
            if not self.wait_for_azure_login_page():
                return False
            
            # Give the login form time to fully initialize
            time.sleep(2)
            
            print("Looking for username field...")
            username_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "logonIdentifier"))
            )
            
            # Store the current URL to verify login success
            login_url = self.driver.current_url
            
            # Clear and enter username
            username_input.clear()
            username_input.send_keys(self.username)
            print("Username entered")
            
            # Find and fill password field
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.clear()
            password_input.send_keys(self.password)
            print("Password entered")
            
            # Find and click the submit button
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "next"))
            )
            
            # Scroll button into view and click using JavaScript
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("Login button clicked")
            
            # Wait for successful login (URL should change)
            try:
                # First, wait for Azure login page to disappear
                WebDriverWait(self.driver, 30).until(
                    lambda driver: "swayamopenid.b2clogin.com" not in driver.current_url
                )
                print("Successfully redirected after Azure login")
                
                # Wait for any NPTEL redirect page to load
                WebDriverWait(self.driver, 30).until(
                    lambda driver: "onlinecourses.nptel.ac.in" in driver.current_url
                )
                print("Successfully reached NPTEL domain")
                
                # Now explicitly navigate to the base URL
                print(f"Redirecting to base URL: {self.base_url}")
                self.driver.get(self.base_url)
                
                # Wait for base URL page to fully load
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Verify we're on the correct page
                current_url = self.driver.current_url
                if self.base_url in current_url:
                    print(f"Successfully loaded base URL: {current_url}")
                    return True
                else:
                    print(f"Failed to load base URL. Current URL: {current_url}")
                    return False
                    
            except TimeoutException:
                print("Login might have failed - no redirect after login")
                return False
            
        except TimeoutException as e:
            print(f"Timeout error: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            return False
        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            return False 

    def submit_answers(self, assignment_number):
        """Select the correct answers and submit the assignment"""
        try:
            print("Reading answers from file...")
            answers_file = f"answers_{assignment_number}.txt"
            with open(answers_file, 'r') as f:
                answer_ids = [line.strip() for line in f.readlines()]

            print("Selecting answers...")
            for input_id in answer_ids:
                try:
                    # Wait for element and click it
                    option = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, input_id))
                    )
                    self.driver.execute_script("arguments[0].click();", option)
                    print(f"Selected answer with ID: {input_id}")
                except TimeoutException:
                    print(f"Could not find or click option with ID: {input_id}")
                    continue

            # Find and click the submit button
            print("Clicking submit button...")
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "submitbutton"))
            )
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("Assignment submitted successfully")
            return True

        except Exception as e:
            print(f"Error submitting answers: {str(e)}")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()

# Usage example
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='NPTEL Login and Question Extractor')
    parser.add_argument('--base_url', required=True, help='The base URL for the NPTEL assignment')
    parser.add_argument('--assign_num', required=True, help='Assignment number')
    args = parser.parse_args()

    # Load credentials from config file
    with open("config.json") as f:
        config = json.load(f)
    
    nptel = NPTELLogin(config["username"], config["password"], args.base_url, args.assign_num)
    nptel.setup_driver()
    
    if nptel.login():
        print("Successfully logged in")
        questions = nptel.get_questions()
        if questions:
            print("Questions successfully extracted")
            # Generate answers
            generate_answers(int(args.assign_num))
            # Submit the answers
            if nptel.submit_answers(args.assign_num):
                print("Assignment completed successfully")
    nptel.close()
