# 🔐 PassCheck — Password Strength Checker

A lightweight, privacy-first web application that analyses password strength in real time — directly in your browser. No data is ever sent to a server.

---

## 📌 Project Description

**PassCheck** is a single-file Flask web application that helps users create stronger, more secure passwords. It evaluates passwords instantly as you type, providing:

- A live **entropy-based strength score** (Weak / Fair / Good / Strong)
- A **5-rule checklist** that lights up as each requirement is met
- A **smart improvement tip** telling you the next step to a stronger password
- Detection of **commonly known weak passwords**
- A built-in **strong password generator**
- **Copy to clipboard** with one click
- **Dark mode / Light mode** toggle that remembers your preference

Everything runs in the browser — no passwords are stored, logged, or transmitted.

---

## 🚀 Features

| Feature | Description |
|---|---|
| ⚡ Real-time analysis | Results update on every keystroke — no submit button needed |
| 📊 Entropy scoring | Calculates bits of entropy using `H = L × log₂(N)` |
| ✅ Rule checklist | 5 interactive cards: length, uppercase, lowercase, number, symbol |
| 💡 Improvement tip | Contextual hint showing the single best next step |
| ⚠️ Common password check | Warns if the password is on a known weak-password list |
| ⚙️ Password generator | Generates a random 16-character strong password |
| 📋 Copy to clipboard | One-click copy with visual confirmation toast |
| 👁️ Show / Hide toggle | Eye icon to reveal or mask the password |
| 🌙 Dark / Light mode | Theme toggle saved in localStorage |
| 📱 Responsive layout | Two-column desktop grid, single-column on mobile |

---

## 🛠️ Technologies Used

| Layer | Technology |
|---|---|
| Backend | Python 3 + Flask |
| Templating | Jinja2 (`render_template_string`) |
| Frontend | Vanilla JavaScript (ES6) |
| Styling | Custom CSS with CSS Variables (dark/light theming) |
| Standard Library | `re` (regex), `math` (log2 entropy) |

---

## 📁 Project Structure

```
password_strength_checker/
├── Sakshi_password_checker.py   ← entire app: Flask routes + logic + HTML template
├── requirements.txt             ← Python dependencies
├── ProjectReport.docx           ← full project report
└── README.md                    ← this file
```

---

## ⚙️ How to Run

### Step 1 — Install Flask

```bash
pip install flask
```

### Step 2 — Run the application

```bash
python Sakshi_password_checker.py
```

### Step 3 — Open in your browser

```
http://127.0.0.1:5000
```

Press **Ctrl + C** in the terminal to stop the server.

---

## 🔑 Password Strength Algorithm

Entropy is calculated as:

```
H = L × log₂(N)
```

Where:
- **L** = password length
- **N** = character pool size based on which classes are present

| Character Class | Pool Size |
|---|---|
| Lowercase (a–z) | 26 |
| Uppercase (A–Z) | 26 |
| Digits (0–9) | 10 |
| Special symbols | 32 |

| Strength | Entropy Range | Bar Colour |
|---|---|---|
| Weak | < 28 bits | 🔴 Red |
| Fair | 28–35 bits | 🟠 Orange |
| Good | 36–59 bits | 🟡 Yellow |
| Strong | 60+ bits | 🟢 Green |

---

## 🔒 Privacy

- ✅ All password analysis runs **100% in the browser**
- ✅ No password data is sent to the Flask server
- ✅ No database, no sessions, no cookies
- ✅ Theme preference stored only in `localStorage` on your device

---

## 🌱 Future Scope

- 🔎 **Have I Been Pwned** — check if the password appeared in a real breach
- ⏱️ **Crack time estimate** — show how long it would take to brute-force
- 💬 **Passphrase suggester** — offer memorable 4-word passphrases
- 📖 **Expanded dictionary** — larger common-password list from a server file
- 🧪 **Unit tests** — pytest suite for Python entropy and scoring functions

---

## 👩‍💻 Author

**Sakshi**  
Project: Password Strength Checker  
Technology: Python (Flask) + HTML / CSS / JavaScript
