import re
from flask import Blueprint, jsonify
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

bp = Blueprint("DegreePlanAPI", __name__, url_prefix="/DegreePlan")

current_dir = os.path.dirname(__file__)
parent_dir = os.path.join(current_dir, "..")
sys.path.append(parent_dir)

path = os.path.abspath(__file__)
directory = os.path.dirname(path)
databaseURL = URL.decrypt(directory + "/config/config.txt", directory + "/config/.gitignore.key")
engine = create_engine(databaseURL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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



load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def normalize_degrees(name):
    if not name or not isinstance(name, str):
        return "UNKNOWN"

    name = name.strip()
    name = name.replace(".", "")
    name = name.replace("-", " ")
    name = re.sub(r"\s+", " ", name)

    lower = name.lower()

    #not very dynamic T_T
    DEGREE_MAP = {
        r"bachelor of science": "BS",
        r"bachelor of arts": "BA",
        r"bachelor of applied science": "BAS",
        r"bachelor of business administration": "BBA",
        r"bachelor of fine arts": "BFA",
        r"bachelor of music": "BM",
        r"bachelor of general studies": "BGS",

        r"master of science": "MS",
        r"master of arts": "MA",
        r"master of science in education": "MSE",
        r"master of healthcare administration": "MHA",
        r"master of business administration": "MBA",

        r"associate of applied science": "AAS",
        r"associate of science": "AS",
        r"associate of arts": "AA",

        r"certificate of proficiency": "CP",
        r"technical certificate": "TC",
        r"graduate certificate": "GC",
        r"minor in": "MIN",
    }

    degree = None
    for pattern, abbr in DEGREE_MAP.items():
        if re.search(pattern, lower):
            degree = abbr
            break

    if not degree:
        match = re.search(
            r"\b(bs|ba|bas|bba|bfa|bm|bgs|ms|ma|mse|mha|mba|aas|as|aa|cp|tc|gc|min)\b",
            lower
        )
        if match:
            degree = match.group(1).upper()

    major = None

    if " in " in lower:
        major = lower.split(" in ")[1]

    if not major and "," in lower:
        parts = [p.strip() for p in lower.split(",")]
        for part in parts:
            if not re.match(r"\b(bs|ba|bas|bba|bfa|bm|bgs|ms|ma|mse|mha|mba|aas|as|aa|cp|tc|gc|min)\b", part.lower()):
                major = part
                break

    if not major and "(" in lower and ")" in lower:
        major = re.sub(r"\(.*?\)", "", lower).strip()

    if not major:
        if degree:
            major = re.sub(r"^(ba|bs|bas|bba|bfa|bm|bgs|ms|ma|mse|mha|mba|aas|as|aa|min|tc|cp|gc)\s*", "", lower)
        else:
            major = lower

    major = major.strip()
    major = re.sub(r"\s+", " ", major)

    JUNK = ["program", "degree", "major", "track"]
    for word in JUNK:
        major = re.sub(rf"\b{word}\b", "", major, flags=re.I)

    major = major.strip()
    major = major.title()

    if degree:
        return f"{degree} {major}".strip()

    return major

def degreeList():
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        max_tokens=900,
        messages=[
            {"role": "system", "content": """Output only valid JSON. No intro, no explanation. If unsure about any information, use placeholders rather than expanding.
                        Never invent nested or recursive structures. Total output must not exceed 1800 tokens."""},
            {"role": "user",
             "content": "List all majors, minors, certificates, and academic programs offered at the University of Arkansas - Fort Smith. Return only a JSON array of program names."}
        ],
    )

    content = completion.choices[0].message.content
    data = json.loads(content)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "programs" in data:
        return data["programs"]
    else:
        raise ValueError("Unexpected program list format.")

def generateDegreePlan(name):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        max_tokens=1500,
        messages=[
            {"role": "system",
             "content": """Output only valid JSON. No intro, no explanation. If unsure about any information, use placeholders rather than expanding.
                        Never invent nested or recursive structures. Total output must not exceed 1800 tokens. Never generate data not required by the schema.
                        Never generate more than 8 notes."""},
            {"role": "user",
             "content": f"""
                        Generate a detailed JSON degree plan for the program '{name}' at the University of Arkansas - Fort Smith.

                        Use exactly this schema:
                        {{
                            "degree": string,
                            "institution": string,
                            "major_code": string,
                            "credit_hours_total": int,
                            "notes": list[dict],
                            "core_courses": list[dict],
                            "concentrations": list[dict]
                        }}

                        Keep the keys exactly as defined in the schema. Do not add, remove, or rename any fields.

                        Follow these strict formatting rules:

                        All values must be valid JSON.
                        Never output trailing commas.
                        Never output placeholder expressions like {{...}}, ...etc..., or empty fields like `"hours":`.
                        If information is unknown, use empty strings `""` or zeroes `0` (for numbers), or empty lists `[]`.
                        The structure must always follow the schema shape:

                        {{
                        "degree": "string",
                        "institution": "string",
                        "major_code": "string",
                        "credit_hours_total": int,
                        "notes": ["string", "string", ...],
                        "core_courses": [
                            {{
                            "semester": "Freshman Fall",
                            "courses": [
                                {{ "code": "string", "title": "string", "hours": int }},
                                ...
                            ]
                            }},
                            {{
                            "semester": "Freshman Spring",
                            "courses": [
                                {{ "code": "string", "title": "string", "hours": int }},
                                ...
                            ]
                            }},
                            ...
                            {{
                            "semester": "Senior Fall",
                            "courses": [
                                {{ "code": "string", "title": "string", "hours": int }},
                                ...
                            ]
                            }},
                            ...
                        ],
                        "concentrations": [
                            {{
                            "code": "string",
                            "name": "string",
                            "required_hours": int,
                            "courses": ["string", "string", ...],
                            "notes": "string"
                            }},
                            ...
                        ]
                        }}

                        You must use this structure exactly and never invent new keys.
                        """
             }
        ],
    )

    content = completion.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print("bad json:", content)
        raise


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
        degreeListArray = degreeList()

        if count <= 0:
            return jsonify({"message": "Count must be at least 1"}), 400

        testingList = degreeListArray[:count]
        insertedDegrees = []
        failedInserts = []

        with Session(engine) as session:
            for degree in testingList:
                try:
                    normalized = normalize_degrees(degree)

                    generatedDegree = generateDegreePlan(degree)

                    generatedDegree["degree"] = normalized

                    existing = session.query(DegreePlan.DegreePlanMap).filter(DegreePlan.DegreePlanMap.degree == normalized).first()

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
                    
                    insertedDegrees.append(normalized)

                except Exception as e:
                    print(f"Failed Insert: {degree} — {e}")
                    failedInserts.append({"degree": degree, "error": str(e)})
                    session.rollback()

            session.commit()

        return jsonify({
            "message": f"Successfully generated {len(insertedDegrees)} sample degree plans.",
            "programs": insertedDegrees,
            "failed inserts": failedInserts
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"message": "Failed to insert or update degree plan.", "error": str(e)}), 500