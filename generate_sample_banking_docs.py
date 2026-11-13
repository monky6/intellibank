"""
Generate official-looking sample banking PDF documents for IntelliBank.
Uses ReportLab to create formatted PDFs with headers, tables, policies, and terms.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def create_sample_docs(output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )
    
    h2_style = ParagraphStyle(
        'DocH2',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E40AF'),
        spaceBefore=14,
        spaceAfter=6
    )

    h3_style = ParagraphStyle(
        'DocH3',
        parent=styles['Heading3'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4B5563'),
        leftIndent=15,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'DocCallout',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#1E3A8A'),
        backColor=colors.HexColor('#EFF6FF'),
        borderColor=colors.HexColor('#3B82F6'),
        borderWidth=1,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=8
    )

    # -------------------------------------------------------------
    # Document 1: Personal Banking Policies and Fee Schedule
    # -------------------------------------------------------------
    doc1_path = os.path.join(output_dir, "Personal_Banking_Policies_and_Fees.pdf")
    doc1 = SimpleDocTemplate(doc1_path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story1 = []

    story1.append(Paragraph("IntelliBank Commercial & Retail Division", h3_style))
    story1.append(Paragraph("Official Personal Banking Policies & Fee Schedule (2026 Edition)", title_style))
    story1.append(Paragraph("Document Reference: POL-PB-2026-V3 | Effective Date: January 1, 2026", callout_style))
    story1.append(Spacer(1, 10))

    story1.append(Paragraph("1. Account Types and Minimum Balance Requirements", h2_style))
    story1.append(Paragraph("IntelliBank provides tailored personal banking accounts designed for individuals and households. Below are the mandatory balance minimums and recurring maintenance terms:", body_style))
    
    table_data_1 = [
        ["Account Tier", "Min. Opening Deposit", "Min. Average Daily Balance", "Monthly Fee", "Fee Waiver Condition"],
        ["Basic Student Checking", "$25", "$0", "$0", "Always waived for enrolled students under age 25"],
        ["Classic Everyday Checking", "$50", "$500", "$12", "Waived with >=$500 daily balance OR >=$1,000 monthly direct deposits"],
        ["Elite Premier Checking", "$500", "$10,000", "$25", "Waived with >=$10,000 combined deposit balance across IntelliBank accounts"],
        ["High-Yield Growth Savings", "$100", "$1,000", "$5", "Waived with >=$1,000 daily balance or recurring auto-transfer of >=$100/mo"]
    ]
    t1 = Table(table_data_1, colWidths=[1.4*inch, 1.3*inch, 1.5*inch, 0.8*inch, 2.0*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story1.append(t1)
    story1.append(Spacer(1, 12))

    story1.append(Paragraph("2. Overdraft Protection and NSF Policy", h2_style))
    story1.append(Paragraph("Standard Overdraft Privilege covers everyday debit card transactions, checks, and scheduled ACH bill payments at the bank's discretion. The standard overdraft fee is $35 per paid item. Maximum fee limit is capped at three (3) overdraft charges ($105 total) in any single calendar day.", body_style))
    story1.append(Paragraph("Grace Period Policy: Customers have until 8:00 PM Eastern Standard Time on the date of occurrence to deposit sufficient funds to bring the ledger balance to >=$0, completely eliminating the $35 overdraft fee.", bullet_style))
    story1.append(Paragraph("De-Minimis Exemption: Overdraft fees will NOT be assessed if the total ending negative balance is less than or equal to -$15.00.", bullet_style))

    story1.append(Paragraph("3. Electronic Funds Transfers and Wire Schedules", h2_style))
    story1.append(Paragraph("Domestic and international transfer fees apply according to channel execution:", body_style))
    story1.append(Paragraph("• Standard ACH Transfers (Online/Mobile): Free ($0.00) with 1-2 business day settlement.", bullet_style))
    story1.append(Paragraph("• Instant Real-Time Payments (RTP): $1.00 per transaction up to $2,500 daily limit.", bullet_style))
    story1.append(Paragraph("• Domestic Outgoing Wire Transfer: $25.00 flat fee per transfer (complimentary for Elite Premier tier).", bullet_style))
    story1.append(Paragraph("• International Outgoing Wire Transfer: $45.00 flat fee plus applicable currency conversion spread (0.85%).", bullet_style))
    story1.append(Paragraph("• All Incoming Wires (Domestic and Foreign): $0.00 (No fee assessed to recipient).", bullet_style))

    story1.append(PageBreak())
    story1.append(Paragraph("4. ATM Limits and Out-of-Network Surcharges", h2_style))
    story1.append(Paragraph("IntelliBank cardholders enjoy surcharge-free access at over 55,000 AllPoint and IntelliBank branded ATMs nationwide.", body_style))
    story1.append(Paragraph("• Daily Cash Withdrawal Limit: $800 per 24-hour cycle for Classic Checking; $2,500 per cycle for Elite Premier.", bullet_style))
    story1.append(Paragraph("• Out-of-Network ATM Fee: $2.50 charged by IntelliBank plus any third-party operator surcharge.", bullet_style))
    story1.append(Paragraph("• Elite Premier ATM Fee Rebate: IntelliBank rebates up to $15.00 per statement cycle for out-of-network third-party operator surcharges.", bullet_style))

    story1.append(Paragraph("5. Inactive and Dormant Account Protocols", h2_style))
    story1.append(Paragraph("An account is categorized as 'Inactive' after 12 consecutive months of zero customer-initiated transactions. Inactive accounts receive formal postal and email notifications.", body_style))
    story1.append(Paragraph("After 24 consecutive months of inactivity, the account transitions to 'Dormant' status. Dormant accounts incur a monthly dormancy maintenance fee of $15.00. Funds remaining dormant for 36 months are remitted to state unclaimed property divisions under statutory escheatment laws.", body_style))

    doc1.build(story1)

    # -------------------------------------------------------------
    # Document 2: Home and Auto Loan Guidelines
    # -------------------------------------------------------------
    doc2_path = os.path.join(output_dir, "Home_and_Auto_Loan_Guidelines.pdf")
    doc2 = SimpleDocTemplate(doc2_path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story2 = []

    story2.append(Paragraph("IntelliBank Lending & Credit Division", h3_style))
    story2.append(Paragraph("Consumer Lending Guidelines: Mortgages & Auto Financing (2026)", title_style))
    story2.append(Paragraph("Document Reference: GUID-LEND-2026-M4 | Underwriting Standards", callout_style))
    story2.append(Spacer(1, 10))

    story2.append(Paragraph("1. Residential Real Estate Mortgages", h2_style))
    story2.append(Paragraph("IntelliBank originates prime residential mortgages for single-family residences, condominiums, and primary 2-4 unit dwellings. All mortgages conform to fair lending guidelines and rigorous credit risk metrics.", body_style))

    table_data_2 = [
        ["Loan Product", "Term (Years)", "Benchmark APR", "Min. FICO Score", "Max LTV (No PMI)", "Max Loan Limit"],
        ["30-Year Fixed Conforming", "30", "6.25%", "680", "80.0%", "$766,550"],
        ["15-Year Fixed Conforming", "15", "5.75%", "660", "80.0%", "$766,550"],
        ["5/1 Hybrid ARM", "30 (5 fixed)", "5.40%", "700", "85.0%", "$1,000,000"],
        ["Jumbo Fixed Loan", "30", "6.65%", "720", "75.0%", "$2,500,000"]
    ]
    t2 = Table(table_data_2, colWidths=[1.6*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.1*inch, 1.3*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story2.append(t2)
    story2.append(Spacer(1, 10))

    story2.append(Paragraph("Private Mortgage Insurance (PMI):", h3_style))
    story2.append(Paragraph("Borrowers putting down less than 20% equity (LTV > 80%) are required to maintain private mortgage insurance. PMI automatically terminates when principal balance amortizes to 78% of the original purchase value.", body_style))

    story2.append(Paragraph("Prepayment Policy Guarantee:", h3_style))
    story2.append(Paragraph("IntelliBank charges ZERO prepayment penalties on all standard conforming and non-conforming residential mortgages. Borrowers may execute partial principal curtailments or total payoff at any time without fees.", callout_style))

    story2.append(Paragraph("2. New and Pre-Owned Automobile Loans", h2_style))
    story2.append(Paragraph("Vehicle financing provides competitive rates for new vehicles (current model year or previous year with under 5,000 miles) and certified pre-owned vehicles (up to 7 years old):", body_style))
    story2.append(Paragraph("• New Auto APR: Starting at 4.99% for 36-60 months; 5.49% for 72 months (requires 720+ credit score).", bullet_style))
    story2.append(Paragraph("• Used Auto APR: Starting at 5.79% for 36-48 months; 6.29% for 60 months.", bullet_style))
    story2.append(Paragraph("• Financing Cap: Up to 100% of Kelley Blue Book / NADA dealer retail value plus applicable sales tax and registration.", bullet_style))
    story2.append(Paragraph("• Automatic Payment Discount: Borrowers enrolled in automated debit from an IntelliBank Checking Account receive a 0.25% APR rate discount.", bullet_style))

    story2.append(Paragraph("3. Mandatory Underwriting Documentation", h2_style))
    story2.append(Paragraph("Loan applicants must submit the following verification checklist:", body_style))
    story2.append(Paragraph("1. Income Verification: W-2 wage statements for the prior two (2) calendar years, plus thirty (30) days of consecutive recent pay stubs.", bullet_style))
    story2.append(Paragraph("2. Self-Employed Applicants: Two (2) years of federal business and personal tax returns with all K-1 schedules.", bullet_style))
    story2.append(Paragraph("3. Asset Verification: Two (2) full months of bank, brokerage, and retirement account statements.", bullet_style))
    story2.append(Paragraph("4. Identification: Valid government-issued photo ID (Driver's License, Passport, or State ID) and Social Security verification.", bullet_style))

    doc2.build(story2)

    # -------------------------------------------------------------
    # Document 3: Credit Card Terms and Fraud Protection
    # -------------------------------------------------------------
    doc3_path = os.path.join(output_dir, "Credit_Card_Terms_and_Fraud_Protection.pdf")
    doc3 = SimpleDocTemplate(doc3_path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story3 = []

    story3.append(Paragraph("IntelliBank Card Services & Risk Mitigation", h3_style))
    story3.append(Paragraph("Credit Card Cardmember Agreement & Fraud Protection Protocols", title_style))
    story3.append(Paragraph("Document Reference: CRD-SEC-2026-F1 | Consumer Rights & Terms", callout_style))
    story3.append(Spacer(1, 10))

    story3.append(Paragraph("1. Card Products and Fee Structures", h2_style))
    
    table_data_3 = [
        ["Card Portfolio", "Annual Fee", "Purchase APR", "Rewards Structure", "Foreign Transaction Fee"],
        ["IntelliBank Platinum Cash", "$0", "18.24% - 26.24% Var.", "1.5% unlimited cash back, 3% on dining/groceries", "None (0.0%)"],
        ["IntelliBank Signature Travel", "$95", "19.49% - 27.49% Var.", "2x points on travel/transit, 50,000 bonus signup pts", "None (0.0%)"],
        ["IntelliBank Black Reserve", "$495", "17.99% - 24.99% Var.", "$300 annual travel credit, Priority Pass Lounge, 5x flights", "None (0.0%)"],
        ["IntelliBank Secured Builder", "$0", "24.99% Fixed", "Credit building with $200-$2,500 security deposit", "3.0% per transaction"]
    ]
    t3 = Table(table_data_3, colWidths=[1.5*inch, 0.8*inch, 1.4*inch, 2.0*inch, 1.3*inch])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story3.append(t3)
    story3.append(Spacer(1, 10))

    story3.append(Paragraph("2. Zero Liability Fraud Protection Guarantee", h2_style))
    story3.append(Paragraph("Under IntelliBank's Zero Liability Policy, cardholders are not held liable for unauthorized charges made online, in-store, or over the phone provided the cardholder has exercised reasonable care in safeguarding their account.", body_style))
    story3.append(Paragraph("Notification Window: Cardholders must report suspected fraudulent transactions within sixty (60) calendar days from the date the billing statement showing the unauthorized activity was dispatched.", callout_style))

    story3.append(Paragraph("3. Dispute Investigation and Provisional Credit", h2_style))
    story3.append(Paragraph("When an unauthorized charge or merchant dispute is filed:", body_style))
    story3.append(Paragraph("• Filing Channels: Via the IntelliBank Mobile App (Security Center > Dispute Transaction), online portal, or 24/7 hotline at 1-800-555-4683.", bullet_style))
    story3.append(Paragraph("• Provisional Credit: Issued to cardholder account within five (5) business days while investigation is underway.", bullet_style))
    story3.append(Paragraph("• Investigation Timeline: Standard merchant disputes are resolved within 30 to 45 calendar days under Visa/Mastercard operating rules.", bullet_style))
    story3.append(Paragraph("• Card Replacement: Suspected compromised cards are immediately deactivated and replacement cards dispatched via expedited courier (2 business days) at no charge.", bullet_style))

    story3.append(Paragraph("4. Late Payment and Penalty APR Policy", h2_style))
    story3.append(Paragraph("Late Payment Fee: $29 for the first occurrence within a 6-month cycle; $40 for subsequent occurrences.", body_style))
    story3.append(Paragraph("Penalty APR: If minimum payment is more than 60 days past due, a Penalty APR of 29.99% variable may apply. The Penalty APR remains in effect until the cardholder makes six (6) consecutive on-time monthly minimum payments.", body_style))

    doc3.build(story3)

    # -------------------------------------------------------------
    # Document 4: Investment and Deposit Services
    # -------------------------------------------------------------
    doc4_path = os.path.join(output_dir, "Investment_and_Deposit_Services.pdf")
    doc4 = SimpleDocTemplate(doc4_path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=0.75*inch, bottomMargin=0.75*inch)
    story4 = []

    story4.append(Paragraph("IntelliBank Wealth Management & Treasury Services", h3_style))
    story4.append(Paragraph("Certificate of Deposit (CD), High Yield Savings & Security Disclosure", title_style))
    story4.append(Paragraph("Document Reference: DEP-SEC-2026-T2 | Disclosures & Policy Scope", callout_style))
    story4.append(Spacer(1, 10))

    story4.append(Paragraph("1. Certificates of Deposit (CD) Term Rates & Penalties", h2_style))
    story4.append(Paragraph("Certificates of Deposit lock funds for fixed tenors with guaranteed annual percentage yields (APY). Minimum opening balance is $1,000 for standard retail CDs.", body_style))

    table_data_4 = [
        ["CD Tenor", "APY Rate", "Compounding Frequency", "Early Withdrawal Penalty"],
        ["6-Month Fixed CD", "4.75% APY", "Daily, credited monthly", "90 days of simple interest"],
        ["12-Month High-Yield CD", "5.10% APY", "Daily, credited monthly", "90 days of simple interest"],
        ["24-Month Builder CD", "4.60% APY", "Daily, credited monthly", "180 days of simple interest"],
        ["36-Month Capital CD", "4.35% APY", "Daily, credited monthly", "270 days of simple interest"],
        ["60-Month Long-Term CD", "4.15% APY", "Daily, credited monthly", "365 days of simple interest"]
    ]
    t4 = Table(table_data_4, colWidths=[1.8*inch, 1.2*inch, 1.8*inch, 2.2*inch])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story4.append(t4)
    story4.append(Spacer(1, 10))

    story4.append(Paragraph("Maturity Grace Period:", h3_style))
    story4.append(Paragraph("At maturity, CDs enter a ten (10) calendar day grace period. Customers may withdraw principal and accrued interest, deposit additional funds, or change the renewal tenor without penalty. If no action is taken, the CD automatically rolls over into the same tenor at the prevailing rate.", body_style))

    story4.append(Paragraph("2. FDIC Insurance Coverage", h2_style))
    story4.append(Paragraph("IntelliBank is an FDIC-insured institution (FDIC Certificate #48921). Deposits are insured up to $250,000 per depositor, per insured bank, for each account ownership category (Single Accounts, Joint Accounts, Revocable Trusts, and IRAs).", body_style))

    story4.append(Paragraph("3. Digital Banking Multi-Factor Authentication (MFA) & Encryption", h2_style))
    story4.append(Paragraph("Customer security protocols mandate:", body_style))
    story4.append(Paragraph("• 256-bit AES encryption for all data in transit and at rest.", bullet_style))
    story4.append(Paragraph("• Multi-Factor Authentication (MFA) enforced on logins from unrecognized devices and all external wire/transfer amounts exceeding $1,000.", bullet_style))
    story4.append(Paragraph("• Biometric authentication (FaceID / Fingerprint) supported via IntelliBank iOS and Android apps.", bullet_style))

    story4.append(Paragraph("4. Scope Boundary & Policy Disclaimers (Out-of-Scope Items)", h2_style))
    story4.append(Paragraph("To ensure customer asset safety and regulatory compliance:", body_style))
    story4.append(Paragraph("• Cryptocurrency & Virtual Assets: IntelliBank does NOT offer direct cryptocurrency brokerage, crypto custody, or speculative digital token trading. Any inquiries regarding crypto transfers are strictly non-operational.", callout_style))
    story4.append(Paragraph("• Independent Financial & Tax Advice: Materials provided in banking brochures do not constitute personal legal, tax, or investment counseling. Customers must consult licensed tax advisors or certified financial planners.", body_style))
    story4.append(Paragraph("• Third-Party Peer Lending: IntelliBank does not underwrite or endorse unverified peer-to-peer (P2P) lending syndicates.", body_style))

    doc4.build(story4)

    print(f"Successfully generated 4 official banking PDFs in {output_dir}")

if __name__ == "__main__":
    target_dir = os.path.join(os.path.dirname(__file__), "sample_docs")
    create_sample_docs(target_dir)
