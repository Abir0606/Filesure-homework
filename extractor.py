import fitz
import json
import re

pdf_path = "Form ADT-1-29092023_signed.pdf"
doc = fitz.open(pdf_path)

all_text = ""
for page_num in range(len(doc)):
    all_text += doc[page_num].get_text() + "\n"

lines = [line.strip() for line in all_text.splitlines() if line.strip()]

extracted = {}

# 1. CIN
for line in lines:
    if re.match(r"^[A-Z][0-9A-Z]{4,}", line) and any(c.isdigit() for c in line) and any(c.isalpha() for c in line):
        extracted["cin"] = line
        break

# 2. Company Name
company_name_idx = -1
company_pattern = re.compile(r".*\b(LIMITED|LTD|LLP|PLC|PVT|PRIVATE LIMITED)\b$", re.IGNORECASE)
for i, line in enumerate(lines):
    if company_pattern.search(line):
        extracted["company_name"] = line
        company_name_idx = i
        break

# 3. Registered Office (from after company name, up to pin/email)
address_lines = []
pin_code_pattern = re.compile(r"\b\d{6}\b")
for j in range(company_name_idx + 1, min(company_name_idx + 10, len(lines))):
    l = lines[j]
    if pin_code_pattern.search(l):
        address_lines.append(l)
        break
    elif '@' in l:
        break
    else:
        address_lines.append(l)
extracted["registered_office"] = " ".join(address_lines)

# 4. Company Email (first @)
emails = [line for line in lines if "@" in line and "." in line]
extracted["company_email"] = emails[0] if emails else ""

# 5. Nature of Appointment (first "appointment" at start)
for line in lines:
    if line.lower().startswith("appointment"):
        extracted["appointment_type"] = line
        break

# 6. Auditor PAN (first 10-char, all uppercase alphanumeric, not already used as CIN)
auditor_pan_pattern = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
for line in lines:
    if auditor_pan_pattern.match(line):
        extracted["auditor_pan"] = line
        break

# 7. Auditor Name (all caps, after PAN, often & or "ASSOCIATES")
auditor_name = ""
pan_idx = -1
if "auditor_pan" in extracted:
    for idx, line in enumerate(lines):
        if extracted["auditor_pan"] == line:
            pan_idx = idx
            break
if pan_idx != -1:
    # Next non-empty, mostly uppercase line
    for j in range(pan_idx+1, min(pan_idx+4, len(lines))):
        l = lines[j]
        if l.isupper() and len(l) > 4:
            auditor_name = l
            break
        # fallback: first long non-empty
        if len(l) > 4:
            auditor_name = l
            break
extracted["auditor_name"] = auditor_name

# 8. Auditor FRN/Membership (alphanumeric or digits, after name)
frn_idx = -1
if auditor_name:
    for idx, line in enumerate(lines):
        if auditor_name == line:
            frn_idx = idx
            break
if frn_idx != -1:
    for j in range(frn_idx+1, min(frn_idx+3, len(lines))):
        l = lines[j]
        if re.match(r"^[A-Z0-9]{5,}$", l):
            extracted["auditor_frn_or_membership"] = l
            break

# 9. Auditor Address (block after FRN, up to state/country/pin/email)
aud_address = []
if "auditor_frn_or_membership" in extracted:
    frn_val = extracted["auditor_frn_or_membership"]
    frn_idx = lines.index(frn_val)
    for k in range(frn_idx+1, min(frn_idx+7, len(lines))):
        l = lines[k]
        # Stop at "IN", country, pin, or email
        if re.match(r"^(IN|[A-Z][a-z]+(-[A-Z]+)?|\d{6}|.*@.*)$", l):
            break
        aud_address.append(l)
extracted["auditor_address"] = " ".join(aud_address)

# 10. Auditor Email (last or 2nd-last email)
if emails:
    extracted["auditor_email"] = emails[-1] if len(emails) > 1 else emails[0]

# 11. Appointment Period (first two lines matching date pattern dd/mm/yyyy)
date_pattern = re.compile(r"\d{2}/\d{2}/\d{4}")
dates_found = []
for line in lines:
    if date_pattern.search(line):
        dates_found.append(line)
if len(dates_found) >= 2:
    extracted["appointment_period_from"] = dates_found[0]
    extracted["appointment_period_to"] = dates_found[1]

# 12. Number of Years (small int after appointment period)
years_idx = -1
if "appointment_period_to" in extracted:
    for idx, line in enumerate(lines):
        if extracted["appointment_period_to"] == line:
            years_idx = idx
            break
if years_idx != -1:
    for l in lines[years_idx+1:years_idx+4]:
        if l.isdigit() and int(l) < 10:
            extracted["number_of_years"] = l
            break

        break

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(extracted, f, indent=2, ensure_ascii=False)

print("Extracted fields:")
for k, v in extracted.items():
    print(f"{k}: {v}")


summary = (
    f"{extracted.get('company_name', 'The company')} has appointed "
    f"{extracted.get('auditor_name', 'its statutory auditor')} "
    f"as its statutory auditor for the period {extracted.get('appointment_period_from', '[start date not found]')} "
    f"to {extracted.get('appointment_period_to', '[end date not found]')}, "
    f"effective from {extracted.get('appointment_date', '[appointment date not found]')}. "
    f"The appointment has been disclosed via Form ADT-1."
)

if extracted.get("company_email"):
    summary += f" The company's contact email is {extracted['company_email']}."
if extracted.get("auditor_email"):
    summary += f" The auditor's email is {extracted['auditor_email']}."

summary = summary.strip()

with open("summary.txt", "w", encoding="utf-8") as f:
    f.write(summary)

print("\nSummary written to summary.txt:\n")
print(summary)