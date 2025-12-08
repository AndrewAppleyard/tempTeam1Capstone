import re
from flask import Blueprint, jsonify, request
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import traceback, os, sys, json
from datetime import datetime
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from functools import wraps
from Advising.APIs import URL
from UserClasses import DegreePlan, User
from openai import OpenAI
from dotenv import load_dotenv
import fitz
import requests
import logging

bp = Blueprint("DegreePlanAPI", __name__, url_prefix="/DegreePlan")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, "..")
sys.path.append(parent_dir)

path = os.path.abspath(__file__)
directory = os.path.dirname(path)
databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")
engine = create_engine(databaseURL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logging.basicConfig(level=logging.DEBUG)

sys.stdout.flush()

def role_required(*required_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            token = get_jwt()
            if token.get("Role") not in required_roles:
                return jsonify({"message": "Access denied!"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator







@bp.route("/View", methods=["GET"])
@role_required("UAFS_ADMINS", "UAFS_ADVISORS", "UAFS_STUDENTS")
def view_degree_plans():
    try:
        with Session(engine) as session:
            degrees = session.query(DegreePlan.DegreePlanMap).all()
            result = []
            for d in degrees:
                print("degree: " + d.degree)
                result.append({
                    "degree": d.degree,
                    "institution": d.institution,
                    "majorcode": d.majorcode,
                    "credithourstotal": d.credithourstotal,
                    "notes": d.notes,
                    "corecourses": d.corecourses,
                    "concentrations": d.concentrations
                })

            return jsonify({
                "count": len(result),
                "degrees": result
            }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to fetch degree plans.", "error": str(e)}), 500

@bp.route("/View/ByDegree", methods=["POST"])
@role_required("UAFS_ADMINS", "UAFS_ADVISORS", "UAFS_STUDENTS")
def view_degree_plans_by_degree():
    try:
        plan = DegreePlan.DegreePlan()
        degree = request.form.get("major")
        if not degree:
            return jsonify({"message": "Missing 'major' in data"}), 400

        with Session(engine) as session:
            # Get the first matching degree plan
            d = session.query(DegreePlan.DegreePlanMap).filter(
                DegreePlan.DegreePlanMap.degree == degree
            ).first()

            if not d:
                return jsonify({"message": "Degree plan not found"}), 404

            # Build the result object
            
            plan.degree = d.degree
            plan.institution = d.institution
            plan.majorcode = d.majorcode
            plan.credithourstotal = d.credithourstotal
            plan.notes = d.notes
            plan.corecourses = d.corecourses
            plan.concentrations = d.concentrations

        return jsonify(plan.__dict__), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "message": "Failed to fetch degree plans.",
            "error": str(e)
        }), 500





load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))




degree_list = {
    "B.S. in Computer Science": "https://uafs.edu/programs/degree-plans/_documents/current/bs-computer-science.pdf",
    "B.A. in English": "https://uafs.edu/programs/degree-plans/_documents/current/ba-english.pdf",
    
    # "M.Ed. in Curriculum and Instruction": "",
    # "M.Ed. in English": "",
    # "M.S. in Healthcare Administration": "",
    # "B.A. in History": "",
    # "B.A. in Media Communication": "",
    # "B.A. in Music": "",
    # "B.A. in Psychology": "",
    # "B.A. in Studio Art": "",
    # "B.B.A. in Business Administration": "",
    # "B.B.A. in Business Administration - Online Completion": "",
    # "B.G.S. in Bachelor of General Studies": "",
    # "B.M.E. in Music Education - Instrumental Music K-12": "",
    # "B.M.E. in Music Education - Vocal Music K-12": "",
    # "B.S. in Advanced Manufacturing Engineering": "",
    # "B.S. in Biology": "",
    # "B.S. in Biology With Life Science Teacher Licensure 7-12": "",
    # "B.S. in Chemistry": "",
    # "B.S. in Chemistry with Concentration in Biochemistry": "",
    # "B.S. in Criminal Justice": "",
    # "B.S. in Dental Hygiene": "",
    # "B.S. in Dental Hygiene-AAS to BS Dental Hygiene Online Completion": "",
    # "B.S. in Early Childhood Education Non-Licensure": "",
    # "B.S. in Electrical Engineering Technology": "",
    # "B.S. in Elementary Education K-6": "",
    # "B.S. in English with Teacher Licensure 7-12": "",
    # "B.S. in Geoscience": "",
    # "B.S. in Graphic Design": "",
    # "B.S. in History with Social Studies Teacher Licensure 7-12": "",
    # "B.S. in Imaging Sciences-Diagnostic Medical Sonography": "",
    # "B.S. in Mathematics": "",
    # "B.S. in Mathematics with Teacher Licensure 7-12": "",
    # "B.S. in Middle Level Education 4-8": "",
    # "B.S. in Organizational Leadership": "",
    # "B.S.N in Nursing": "",
    # "B.S.N in Nursing - Accelerated": "",
    # "B.S.W in Social Work": "",
    # "A.A.S. in Early Childhood Education": "",
    # "A.A.S. in Electronics Technology": "",
    # "A.A.S. in General Technology": "",
    # "A.A.S. in Nursing (ADN)": "",
    # "A.A.S. in Nursing (LPN to ADN)": "",
    # "A.A.S. in Radiography": "",
    # "A.A.S. in Surgical Technology": "",
    # "A.A.S. in Welding": "",
    # "A.A in Associate of Arts": "",
    # "A.G.S in Associate of General Studies": "",
    # "A.S. in Electrical Engineering": "",
    # "A.S. in Mechanical Engineering": "",
    # "Minor in Applied Statistics": "",
    # "Minor in Art History": "",
    # "Minor in Biology": "",
    # "Minor in Business Administration": "",
    # "Minor in Chemistry": "",
    # "Minor in Computer Science": "",
    # "Minor in Creative Writing": "",
    # "Minor in Criminal Justice": "",
    # "Minor in Diversity Studies": "",
    # "Minor in Geographic Information Systems": "",
    # "Minor in Geoscience": "",
    # "Minor in History": "",
    # "Minor in Literary and Cultural Studies": "",
    # "Minor in Mathematics": "",
    # "Minor in Media Communication": "",
    # "Minor in Music": "",
    # "Minor in Philosophy": "",
    # "Minor in Physics": "",
    # "Minor in Political Science": "",
    # "Minor in Professional Writing": "",
    # "Minor in Psychology": "",
    # "Minor in Social Work": "",
    # "Minor in Sociology": "",
    # "Minor in Spanish": "",
    # "Minor in Speech": "",
    # "Minor in Studio Art": "",
    # "Minor in Teaching English as a Second Language": "",
    # "Minor in Theatre": "",
    # "Technical Certificate in Early Childhood Education": "",
    # "Technical Certificate in Industrial Electronics and Electrical Maintenance": "",
    # "Technical Certificate in Welding": "",
    # "Certificate of Proficiency in Accounting Fundamentals": "",
    # "Certificate of Proficiency in Arc Welding": "",
    # "Certificate of Proficiency in Consumer Marketing": "",
    # "Certificate of Proficiency in Content Creation, Editing, and Publishing": "",
    # "Certificate of Proficiency in Corporate Finance": "",
    # "Certificate of Proficiency in Cyber Systems": "",
    # "Certificate of Proficiency in Data Analytics": "",
    # "Certificate of Proficiency in Digital Marketing": "",
    # "Certificate of Proficiency in Early Childhood Education": "",
    # "Certificate of Proficiency in Economic Analysis": "",
    # "Certificate of Proficiency in Emergency Medical Technology": "",
    # "Certificate of Proficiency in Entrepreneurship": "",
    # "Certificate of Proficiency in Grant and Non-Profit Writing": "",
    # "Certificate of Proficiency in Human Resource Management": "",
    # "Certificate of Proficiency in Industrial Electronics and Electrical Maintenance": "",
    # "Certificate of Proficiency in International Business": "",
    # "Certificate of Proficiency in International Financial Economics": "",
    # "Certificate of Proficiency in Investment Securities": "",
    # "Certificate of Proficiency in Leadership": "",
    # "Certificate of Proficiency in MIG Welding": "",
    # "Certificate of Proficiency in Pre-Law Studies": "",
    # "Certificate of Proficiency in Public Accounting Standards and Practices": "",
    # "Certificate of Proficiency in Robotics": "",
    # "Certificate of Proficiency in Spanish for the Helping Professions": "",
    # "Certificate of Proficiency in Supply Chain Management": "",
    # "Certificate of Proficiency in Sustainable Energy Technologies": "",
    # "Certificate of Proficiency in Teaching English As A Second Language": "",
    # "Certificate of Proficiency in TIG Welding": "",
    # "Certificate of Proficiency in User Experience (UX)": "",
    # "Certificate of Proficiency in Welding Layout and Fabrication": ""
}

def extract_pdf(url):
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.content


def extract_text_from_pdf(pdf):
    doc = fitz.open(stream=pdf, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()



def generateDegreePlan(name, text):
    prompt = """
        Extract real degree plan data only from the text provided.

        DO NOT HALLUCINATE.
        If something is missing, use "" or [] or 0.
                
        Schema:
        {
            "degree": string,
            "institution": "University of Arkansas - Fort Smith",
            "majorcode": string,
            "credithourstotal": int,
            "notes": list,
            "corecourses": dict,
            "concentrations": dict
        }

        This is the format I want for the corecourses:
        {
        "Freshman Fall":    [ course, course, ... ],
        "Freshman Spring":  [ course, course, ... ],
        "Sophomore Fall":   [ ... ],
        "Sophomore Spring": [ ... ],
        "Junior Fall":      [ ... ],
        "Junior Spring":    [ ... ],
        "Senior Fall":      [ ... ],
        "Senior Spring":    [ ... ]
        }

        Each course object must be:
        {
        "code": string,
        "title": string,
        "hours": int
        }

        Include the electives as the name they are listed in the degree plan as if that was the name of the course and follow the same schema as above.

        Follow the same format for the concentrations as well make the key the concentration name and the value the courses and include the concentration code in the schema of the dict as well, 
        if there are no concentrations just return an empty dict.

        Output MUST be strictly valid JSON.
        Double-check that:
        - Every string begins and ends with "
        - No string contains an unescaped " inside it
        - All \ characters are escaped properly
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        response_format={"type": "json_object"},
        max_tokens=4000,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Degree Name: {name}"},
            {"role": "user", "content": text}
        ],
    )

    try:
        content = completion.choices[0].message.content
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("Raw Output On Error:")
        print(content)
        raise e


""" We uncomment this when we are ready
@bp.route("/UpdateDegreePlans", methods=["POST"])
@role_required("UAFS_ADMINS")
def update_degree_plans():
    try:
        async def run_async():

            degreeListArray = degreeList()

            insertedDegrees = []

            with Session(engine) as session:
                for degree in degreeListArray:
                    generatedDegree = generateDegreePlan(degree)

                    existing = session.query(DegreePlan.DegreePlanMap).filter(DegreePlan.DegreePlanMap.degree == generatedDegree["degree"]).first()

                    if existing:
                        existing.institution = generatedDegree["institution"]
                        existing.majorcode = generatedDegree["major_code"]
                        existing.credithourstotal = generatedDegree["credit_hours_total"]
                        existing.notes = generatedDegree["notes"]
                        existing.corecourses = generatedDegree["core_courses"]
                        existing.concentrations = generatedDegree["concentrations"]
                    else:
                        newDegree = DegreePlan.DegreePlanMap(
                            degree=generatedDegree["degree"],
                            institution=generatedDegree["institution"],
                            majorcode=generatedDegree["major_code"],
                            credithourstotal=generatedDegree["credit_hours_total"],
                            notes=generatedDegree["notes"],
                            corecourses=generatedDegree["core_courses"],
                            concentrations=generatedDegree["concentrations"],
                        )
                        session.add(newDegree)

                    insertedDegrees.append(generatedDegree["degree"])
                
                session.commit()
                
            return jsonify({
                "message": "All degree plans updated successfully.",
                "count": len(insertedDegrees),
                "programs": insertedDegrees
            })
        
        results = asyncio.run(run_async())
        return jsonify(results), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to insert or update degree plan.", "error": str(e)}), 500
"""






#Altered route for testing
@bp.route("/UpdateDegreePlans/<int:count>", methods=["POST"])
@role_required("UAFS_ADMINS")
def update_degree_plans(count):
    try:
        inserted = []
        failed = []
        limited_list = list(degree_list.items())[:count]

        with Session(engine) as session:
            for degree_name, url in limited_list:

                if not url:
                    failed.append({"degree": degree_name, "error": "URL does not exist or URL not assigned"})
                    continue

                try:

                    pdf = extract_pdf(url)
                    text = extract_text_from_pdf(pdf)

                    generatedDegree = generateDegreePlan(degree_name, text)

                    existing = session.query(DegreePlan.DegreePlanMap).filter(DegreePlan.DegreePlanMap.degree == generatedDegree["degree"]).first()

                    if existing:
                        existing.institution = generatedDegree["institution"]
                        existing.majorcode = generatedDegree["majorcode"]
                        existing.credithourstotal = generatedDegree["credithourstotal"]
                        existing.notes = generatedDegree["notes"]
                        existing.corecourses = generatedDegree["corecourses"]
                        existing.concentrations = generatedDegree["concentrations"]
                    else:
                        newDegree = DegreePlan.DegreePlanMap(
                            degree=generatedDegree["degree"],
                            institution=generatedDegree["institution"],
                            majorcode=generatedDegree["majorcode"],
                            credithourstotal=generatedDegree["credithourstotal"],
                            notes=generatedDegree["notes"],
                            corecourses=generatedDegree["corecourses"],
                            concentrations=generatedDegree["concentrations"],
                        )
                        session.add(newDegree)
                    
                    inserted.append(generatedDegree["degree"])

                except Exception as e:
                    print(f"Error: Failed to process {degree_name}: {e}")
                    failed.append({"degree": degree_name, "error": str(e)})
                    session.rollback()

            session.commit()

        return jsonify({
            "message": f"Generated {len(inserted)} sample degree plans.",
            "programs": inserted,
            "failed inserts": failed
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to insert or update degree plan.", "error": str(e)}), 500