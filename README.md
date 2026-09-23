
# 💧 AI-Based Smart Water Tank Refill Advisor

### Smart household water refill recommendations using LangChain and Fuzzy Logic

An AI-based college mini project that helps households determine how urgently their water tank needs to be refilled.

The system accepts both natural-language and manual inputs. Natural-language input is processed using **LangChain and OpenAI**, while the actual refill urgency is calculated using a genuine **Mamdani Fuzzy Logic** inference system.

The fuzzy logic engine produces the authoritative numeric urgency score, while LangChain is used for natural-language extraction and explanation.

---

## 🚀 Main Features

### 🗣️ Natural Language Input

- Describe the household water situation in plain English.
- LangChain extracts:
  - Tank capacity
  - Current tank level
  - Household size
  - Water usage
- Extracted information is validated before being sent to the fuzzy engine.

### 🎛️ Manual Input Mode

- Enter tank information manually.
- Input fields include:
  - Tank capacity
  - Current tank level
  - Household size
  - Water usage
- Works without an OpenAI API key.

### 🧮 Mamdani Fuzzy Logic

The project implements a genuine five-stage Mamdani fuzzy inference process:

1. Fuzzification
2. Rule Evaluation
3. Implication
4. Aggregation
5. Centroid Defuzzification

### 📊 Refill Urgency Score

The system calculates a refill urgency score from **0–100**.

The result is categorized as:

- Very Low
- Low
- Medium
- High
- Very High

### 🔍 Fuzzy Analysis

The application displays:

- Membership degrees
- Activated fuzzy rules
- Rule firing strengths
- Fuzzy output analysis

### 📈 Membership Function Visualizations

The project provides graphical visualizations of the membership functions for:

- Tank Level
- Water Usage
- Household Size
- Refill Urgency

### 🤖 AI-Generated Recommendation

LangChain generates a simple natural-language explanation of the fuzzy result.

The LLM does not change or override the numeric fuzzy result.

### 🛡️ Input Validation

- Validates user inputs.
- Handles missing information.
- Handles invalid values gracefully.

### 📱 Mobile-Friendly UI

The application is built using Streamlit and provides a simple interface suitable for desktop and mobile browsers.

---

## 🛠️ Technologies / Tech Stack

| Category | Technology |
|---|---|
| Programming Language | Python 3.10+ |
| Web Framework | Streamlit |
| AI / LLM Orchestration | LangChain |
| LLM Provider | OpenAI |
| LLM Model | GPT-4o-mini |
| Fuzzy Logic | scikit-fuzzy |
| Data Validation | Pydantic |
| Visualization | Matplotlib |
| Data Handling | Pandas, NumPy |
| Deployment | Streamlit Community Cloud |
| Version Control | Git & GitHub |

---

## 📁 Project Structure

```text
smart-water-tank-refill-advisor/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
│
├── fuzzy/
│   ├── membership.py
│   ├── rules.py
│   └── inference.py
│
├── ai/
│   ├── extractor.py
│   ├── prompts.py
│   └── explainer.py
│
├── utils/
│   ├── validation.py
│   └── helpers.py
│
├── ui/
│   ├── components.py
│   └── charts.py
│
├── docs/
│   ├── project_report.md
│   ├── fuzzy_rules.md
│   └── viva_questions.md
│
└── assets/
    ├── FUZZYANALYSIS.png
    ├── FUZZYOUTPUT.png
    ├── MANUALINPUT.png
    ├── MFV.png
    ├── NLI(AI).png
    └── RESULTS.png
````

---

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/smart-water-tank-refill-advisor.git
```

### 2. Open the Project Folder

```bash
cd smart-water-tank-refill-advisor
```

### 3. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

The project uses an OpenAI API key for the natural-language extraction and AI explanation features.

### Local Development

Create a `.env` file using `.env.example`.

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Important:** Never upload your real API key to GitHub.

The `.env` file should remain inside `.gitignore`.

### Streamlit Community Cloud

Add the following secret in the Streamlit application settings:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
```

Replace the placeholder only inside the secure Streamlit Secrets settings.

---

## ▶️ How to Run the Project

After completing the installation, run:

```bash
streamlit run app.py
```

Streamlit will provide a local URL, normally:

```text
http://localhost:8501
```

Open this URL in your web browser.

---

## 🧑‍💻 How to Use the Project

### Option 1 — Manual Input

1. Open the application.
2. Select **Manual Input**.
3. Enter the required information:

   * Tank capacity
   * Current tank level
   * Household size
   * Water usage
4. Submit the information.
5. The fuzzy inference engine processes the inputs.
6. The application calculates the **Refill Urgency Score**.
7. View the urgency category.
8. Open the fuzzy analysis section to inspect membership values and activated rules.
9. View the membership function charts.
10. Read the recommendation.

Manual input mode works without an OpenAI API key.

---

### Option 2 — Natural Language Input

1. Select **Natural Language Input**.
2. Describe the household water situation.

Example:

```text
There are 5 people in my house.
The tank capacity is 1000 litres and it is around 30% full.
We use a lot of water for bathing, washing clothes and cleaning.
```

3. LangChain extracts the required information.
4. The extracted information is validated.
5. The fuzzy inference engine calculates the urgency score.
6. LangChain generates a plain-language explanation.
7. The final result is displayed in the application.

---

## 🧠 How the System Works

```text
                         USER INPUT
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     Natural Language                  Manual Input
              │                             │
              ▼                             │
       LangChain Extraction                 │
              │                             │
              ▼                             │
       Structured Data                      │
              │                             │
              └──────────────┬──────────────┘
                             ▼
                     Input Validation
                             │
                             ▼
                 Mamdani Fuzzy Inference
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        Fuzzification   Rule Evaluation   Implication
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                        Aggregation
                             │
                             ▼
                  Centroid Defuzzification
                             │
                             ▼
                  Refill Urgency Score
                         0 – 100
                             │
                             ▼
                    Urgency Category
                             │
                             ▼
                  LangChain Explanation
                             │
                             ▼
                       FINAL RESULT
```

### Important Architecture Principle

The **fuzzy logic engine is responsible for the actual numeric decision**.

LangChain is used for:

* Natural-language information extraction
* Natural-language explanation

The LLM does not modify the fuzzy engine's numeric score or urgency category.

---

# 📸 Screenshots

## 1. Manual Input

The manual input interface allows the user to enter tank capacity, tank level, household size, and water usage.

![Manual Input](assets/MANUALINPUT.png)

---

## 2. Natural Language Input

The Natural Language Input interface allows the user to describe their household water situation in plain English.

![Natural Language Input](assets/NLI\(AI\).png)

---

## 3. Fuzzy Analysis

The Fuzzy Analysis section displays the membership values and activated fuzzy rules used by the inference engine.

![Fuzzy Analysis](assets/FUZZYANALYSIS.png)

---

## 4. Fuzzy Output

The fuzzy output visualization shows the aggregated fuzzy output and the defuzzified result.

![Fuzzy Output](assets/FUZZYOUTPUT.png)

---

## 5. Membership Function Visualization

The application provides graphical membership-function visualizations used by the fuzzy inference system.

![Membership Function Visualization](assets/MFV.png)

---

## 6. Final Results

The Results section displays the calculated refill urgency score, urgency category, and recommendation.

![Final Results](assets/RESULTS.png)

---

## 🌐 Live Deployment

### 🚀 Live Application

**[Open Live Project](https://smart-water-tank-refill-advisor-jjq84sm7torpoayc7huetm.streamlit.app/)**

The application is deployed using **Streamlit Community Cloud**.

---

## 📌 Project Objectives

* Build a genuine Mamdani fuzzy inference system.
* Use fuzzy logic instead of simple fixed percentage thresholds.
* Use LangChain for natural-language information extraction.
* Generate understandable AI-based recommendations.
* Support both manual and natural-language input.
* Provide a simple and mobile-friendly Streamlit interface.
* Demonstrate the practical combination of:

  * Artificial Intelligence
  * Natural Language Processing
  * Fuzzy Logic

---

## 🔄 System Workflow

```text
User
 │
 ├── Manual Input
 │
 └── Natural Language Input
          │
          ▼
      LangChain
          │
          ▼
  Structured Information
          │
          ▼
   Input Validation
          │
          ▼
   Fuzzy Inference
          │
          ▼
  Urgency Score (0–100)
          │
          ▼
  Urgency Category
          │
          ▼
  AI Explanation
          │
          ▼
     Final Result
```

---

## 🔮 Future Scope

* Integration with IoT-based ultrasonic water-level sensors.
* Automatic real-time tank-level monitoring.
* Water consumption prediction using historical data.
* Multi-tank and multi-household support.
* Database integration for historical records.
* Support for additional LLM providers through LangChain.
* Mobile application integration.
* Historical water usage analysis.
* Automatic refill notifications.

---

## ⚠️ Limitations

* Water usage is currently represented as Low, Medium, or High rather than exact litres/day.
* The application does not currently maintain historical usage data.
* Natural-language mode requires an internet connection and a valid OpenAI API key.
* Manual mode works without an API key.
* The system currently provides recommendations rather than directly controlling a physical water pump.

---

## 👨‍🎓 Student Details

| Field         | Details                                      |
| ------------- | -------------------------------------------- |
| Student Name  | **RAJESH GAIKWAD**                           |
| Roll Number   | **19011**                                    |
| Course        | **B.Sc. Information Technology**             |
| Project Type  | **College Mini Project**                     |
| Project Title | **AI-Based Smart Water Tank Refill Advisor** |

---

## 👤 Author

**RAJESH GAIKWAD**

**Roll Number:** 19011

**Course:** B.Sc. Information Technology

**Project:** AI-Based Smart Water Tank Refill Advisor

---

## 📄 License

This project was developed as a **college mini project** for educational purposes.
