import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_insurance_policy():
    """Create a comprehensive sample insurance policy PDF for testing"""
    
    # Create pdfs directory if it doesn't exist
    os.makedirs("pdfs", exist_ok=True)
    
    filename = "pdfs/sample_health_insurance_policy.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page 1 - Policy Overview
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 80, "COMPREHENSIVE HEALTH INSURANCE POLICY")
    
    c.setFont("Helvetica", 12)
    y_position = height - 130
    
    policy_overview = [
        "Policy Number: CHP-2024-12345",
        "Policy Holder: Sample Policy Holder",
        "Effective Date: January 1, 2024",
        "Expiry Date: December 31, 2024",
        "Sum Insured: ₹5,00,000",
        "",
        "COVERAGE SUMMARY:",
        "",
        "This comprehensive health insurance policy provides coverage for:",
        "• Hospitalization expenses",
        "• Surgical procedures",
        "• Pre and post hospitalization",
        "• Day care treatments",
        "• Emergency ambulance services",
        "",
        "IMPORTANT POLICY TERMS:",
        "",
        "1. WAITING PERIODS",
        "   • General treatments: No waiting period",
        "   • Specific diseases: 30 days waiting period",
        "   • Surgical procedures: 90 days waiting period",
        "   • Pre-existing conditions: 24 months waiting period",
        "",
        "2. GEOGRAPHIC COVERAGE",
        "   • All treatments within India are covered",
        "   • Network hospitals available in major cities",
        "   • Cashless treatment at network hospitals",
        "   • Pune, Mumbai, Delhi, Bangalore have extensive network"
    ]
    
    for line in policy_overview:
        if y_position < 100:
            c.showPage()
            y_position = height - 80
        c.drawString(100, y_position, line)
        y_position -= 18
    
    # Page 2 - Surgical Coverage Details
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 80, "SURGICAL PROCEDURES COVERAGE")
    
    c.setFont("Helvetica", 12)
    y_position = height - 120
    
    surgical_coverage = [
        "ORTHOPEDIC SURGERIES:",
        "",
        "1. KNEE SURGERIES",
        "   • Knee replacement surgery: Covered up to ₹2,50,000",
        "   • Arthroscopic knee surgery: Covered up to ₹75,000",
        "   • Meniscus repair: Covered up to ₹50,000",
        "   • Waiting period: 90 days from policy inception",
        "   • Pre-authorization required for all knee surgeries",
        "",
        "2. HIP SURGERIES",
        "   • Hip replacement: Covered up to ₹3,00,000",
        "   • Hip fracture treatment: Covered up to ₹1,50,000",
        "   • Waiting period: 90 days from policy inception",
        "",
        "3. CARDIAC SURGERIES",
        "   • Heart bypass surgery: Covered up to ₹4,00,000",
        "   • Angioplasty: Covered up to ₹2,00,000",
        "   • Pacemaker implantation: Covered up to ₹1,50,000",
        "   • Waiting period: 180 days from policy inception",
        "",
        "GENERAL SURGERY COVERAGE:",
        "• Appendectomy: Up to ₹40,000",
        "• Gallbladder surgery: Up to ₹60,000",
        "• Hernia repair: Up to ₹35,000",
        "• Cataract surgery: Up to ₹25,000 per eye",
        "",
        "Note: All surgical procedures require pre-authorization",
        "from the insurance company before treatment."
    ]
    
    for line in surgical_coverage:
        if y_position < 100:
            c.showPage()
            y_position = height - 80
        c.drawString(100, y_position, line)
        y_position -= 18
    
    # Page 3 - Claims and Exclusions
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 80, "CLAIMS PROCEDURE & EXCLUSIONS")
    
    c.setFont("Helvetica", 12)
    y_position = height - 120
    
    claims_info = [
        "CLAIMS SUBMISSION PROCESS:",
        "",
        "1. CASHLESS CLAIMS (Network Hospitals)",
        "   • Present insurance card at admission",
        "   • Hospital will seek pre-authorization",
        "   • Approval typically within 2-4 hours",
        "   • No upfront payment required for covered expenses",
        "",
        "2. REIMBURSEMENT CLAIMS (Non-Network)",
        "   • Submit claim within 30 days of discharge",
        "   • Required documents: Bills, discharge summary, reports",
        "   • Claims processed within 15 working days",
        "   • Payment via NEFT to registered bank account",
        "",
        "POLICY EXCLUSIONS:",
        "",
        "1. GENERAL EXCLUSIONS",
        "   • Cosmetic and plastic surgery (unless medically necessary)",
        "   • Dental treatment (unless due to accident)",
        "   • Pregnancy and maternity expenses",
        "   • Infertility and assisted reproduction",
        "   • Mental illness and psychiatric disorders",
        "",
        "2. WAITING PERIOD EXCLUSIONS",
        "   • Claims in first 30 days reviewed for exclusions",
        "   • Pre-existing conditions not covered for 24 months",
        "   • Specific diseases have 30-day waiting period",
        "",
        "3. AGE-RELATED CONSIDERATIONS",
        "   • Coverage available from 18 to 65 years",
        "   • Premium increases with age at renewal",
        "   • Senior citizen plans available for 60+ years"
    ]
    
    for line in claims_info:
        if y_position < 100:
            c.showPage()
            y_position = height - 80
        c.drawString(100, y_position, line)
        y_position -= 18
    
    # Page 4 - Contact Information
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 80, "CONTACT INFORMATION & SUPPORT")
    
    c.setFont("Helvetica", 12)
    y_position = height - 120
    
    contact_info = [
        "CUSTOMER SUPPORT:",
        "",
        "24/7 Helpline: 1800-123-4567",
        "Email: support@healthinsurance.com",
        "Website: www.healthinsurance.com",
        "",
        "CLAIMS SUPPORT:",
        "Claims Helpline: 1800-987-6543",
        "Email: claims@healthinsurance.com",
        "",
        "NETWORK HOSPITALS:",
        "",
        "PUNE:",
        "• Ruby Hall Clinic",
        "• Jehangir Hospital",
        "• Deenanath Mangeshkar Hospital",
        "• Sahyadri Hospital",
        "",
        "MUMBAI:",
        "• Lilavati Hospital",
        "• Hinduja Hospital",
        "• Breach Candy Hospital",
        "• Kokilaben Dhirubhai Ambani Hospital",
        "",
        "DELHI:",
        "• All India Institute of Medical Sciences (AIIMS)",
        "• Apollo Hospital",
        "• Max Healthcare",
        "• Fortis Healthcare",
        "",
        "For complete network hospital list, visit our website",
        "or call customer support.",
        "",
        "IMPORTANT REMINDERS:",
        "• Keep your policy document safe",
        "• Inform us of any changes in contact details",
        "• Renew your policy before expiry date",
        "• Use network hospitals for cashless treatment"
    ]
    
    for line in contact_info:
        if y_position < 100:
            c.showPage()
            y_position = height - 80
        c.drawString(100, y_position, line)
        y_position -= 18
    
    c.save()
    print(f"✅ Created comprehensive sample insurance policy: {filename}")

if __name__ == "__main__":
    try:
        create_sample_insurance_policy()
        print("\n📄 Sample PDF created successfully!")
        print("You can now test the RAG system with this document.")
    except ImportError:
        print("❌ reportlab not installed.")
        print("Install it with: pip install reportlab")
        print("Or manually add any PDF file to the pdfs/ folder")
    except Exception as e:
        print(f"❌ Error creating sample PDF: {e}")
