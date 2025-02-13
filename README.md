# NPTEL Assignment Automation

This project automates the process of completing NPTEL assignments by using Selenium for web automation and an AI-powered answer generation system.

## Description

This tool automates the following workflow:
1. Logs into your NPTEL account
2. Extracts questions from assignments
3. Generates answers using AI (via Groq LLM)
4. Automatically submits the answers

## Prerequisites

- Python 3.8+
- Chrome browser installed
- Groq API key (FREE)
- NPTEL account credentials

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd nptel-automation
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

4. Update the `config.json` with your NPTEL credentials:
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

## Usage

1. Run the main script with the assignment number:
```bash
python main.py --base_url <assignment_url> --assign_num <assignment_number>
```

For example:
```bash
python main.py  --base_url "https://onlinecourses.nptel.ac.in/noc25_bt15/unit?unit=37&assessment=167" --assign_num 4
```

## How It Works

1. **Login Process**: The script uses Selenium to automate the login process through NPTEL's Azure B2C authentication system.

2. **Question Extraction**: Once logged in, it extracts all questions and options from the assignment page and saves them in both JSON and text formats.

3. **Answer Generation**: Using the Groq LLM through LangChain, the system generates answers for each question based on the context and available options.

4. **Answer Submission**: Finally, the script automatically selects and submits the generated answers.

## File Structure

- `main.py`: Main script handling web automation and coordination
- `answer_generator.py`: Handles AI-powered answer generation
- `config.json`: Configuration file for credentials
- `requirements.txt`: Project dependencies
- Generated files:
  - `questions_{assignment_number}.json`: JSON format of extracted questions
  - `questions_{assignment_number}.txt`: Human-readable format of questions
  - `answers_{assignment_number}.txt`: Generated answers

## Important Notes

- Make sure you have a stable internet connection
- The Chrome browser will open during execution (not headless by default)
- Keep your credentials secure and never commit them to version control
- Review generated answers before submission
- Use responsibly and in accordance with NPTEL's terms of service

## Disclaimer

**USE AT YOUR OWN RISK**: This tool is provided for educational and experimental purposes only. Please note:

- The AI-generated answers are not guaranteed to be correct
- The author(s) of this tool cannot be held responsible for:
  - Any incorrect answers or failed assignments
  - Academic penalties or disciplinary actions
  - Account-related issues or blocks
  - Any other consequences resulting from the use of this tool
- Users are solely responsible for verifying answers and maintaining academic integrity
- This tool should not be used to violate any academic policies or terms of service

## Troubleshooting

- If login fails, check your credentials in `config.json`
- For timeout errors, ensure stable internet connection
- Screenshots are saved as `login_error.png` when errors occur
- Check Chrome browser and ChromeDriver compatibility

