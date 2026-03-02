# your_app/views_debug.py
from django.shortcuts import render
from types import SimpleNamespace
from datetime import date, datetime

def consultation_detail_preview(request):
    # Fake Appointment object
    fake_appointment = SimpleNamespace(
        date=date(2026, 3, 2),
        created_at=datetime(2026, 3, 2, 10, 0),
        id=1
    )

    # Fake ConsultationRecord object
    fake_record = SimpleNamespace(
        diagnosis="Fake Diagnosis",
        notes="Fake Notes",
        prescription="Fake Prescription",
        requested_tests="Fake Test",
        appointment=fake_appointment,
        created_at=datetime(2026, 3, 2, 12, 0),
        updated_at=datetime(2026, 3, 2, 12, 0),
        id=1
    )

    # Render template in browser
    return render(request, "medical_records/consultationrecord_detail.html", {"record": fake_record})



def patient_history_preview(request):
    fake_consultations = [
        SimpleNamespace(
            pk=1,
            diagnosis="Flu",
            appointment=SimpleNamespace(created_at=datetime(2026,3,2,10,0))
        ),
        SimpleNamespace(
            pk=2,
            diagnosis="Migraine",
            appointment=SimpleNamespace(created_at=datetime(2026,3,1,9,0))
        ),
    ]
    return render(request, "medical_records/patient_medical_history.html", {"consultations": fake_consultations})