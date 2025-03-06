from fastapi import FastAPI
from routes import items , Xray_checking , treatment_plan , Scan_dental , report_summary , exercise_fetch , Ai_scribe , soap_note , Email_sender  , Add_Data , auth  , Bolna , appoinment , integration , drug_info , ReportRag
from cors_config import add_cors



app = FastAPI(
    title="Basic FastAPI Example",
    description="A simple FastAPI application structure",
    version="0.1.0"
)

add_cors(app)

# Include the routes
app.include_router(items.router)
app.include_router(Xray_checking.router)
app.include_router(treatment_plan.router)
app.include_router(Scan_dental.router)
app.include_router(report_summary.router)
app.include_router(exercise_fetch.router)
app.include_router(Ai_scribe.router)
app.include_router(soap_note.router)
app.include_router(Email_sender.router)
app.include_router(Add_Data.router)
app.include_router(auth.router)
app.include_router(Bolna.router)
app.include_router(appoinment.router)
app.include_router(integration.router)
app.include_router(drug_info.router)
app.include_router(ReportRag.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)