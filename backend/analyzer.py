# pyright: reportMissingImports=false
from fastapi import APIRouter, UploadFile, File, HTTPException
from androguard.misc import AnalyzeAPK

router = APIRouter()

@router.post("/analyze")
async def analyze_apk(file: UploadFile = File(...)):
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    contents = await file.read()
    with open("uploaded.apk", "wb") as f:
        f.write(contents)

    a, d, dx = AnalyzeAPK("uploaded.apk")
    perms = a.get_permissions()
    secrets = [s for s in dx.get_strings() if "API_KEY" in s]

    return {
        "permissions": perms,
        "secrets": secrets,
        "summary": f"Found {len(perms)} permissions and {len(secrets)} possible secrets."
    }
