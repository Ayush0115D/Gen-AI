from fastapi import FastAPI, Query
from .client.rq_client import queue
from .queue.worker import process_query
from rq.job import Job

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Server is up and running"}

@app.post("/chat")
def chat(
    query: str = Query(..., description="The chat query of user")
):
    job = queue.enqueue(process_query, query)
    return {
        "status": "Queued",
        "job_id": job.id
    }

@app.get("/job-status")
def get_result(
    job_id: str = Query(..., description="Job ID")
):
    job = Job.fetch(job_id, connection=queue.connection)

    if job.is_finished:
        return {"status": "finished", "result": job.return_value}

    if job.is_failed:
        return {"status": "failed", "error": str(job.exc_info)}

    return {"status": job.get_status()}
