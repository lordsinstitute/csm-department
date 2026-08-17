from django.db import models
from django.contrib.auth.models import User

class PatientRecord(models.Model):
    # Existing fields
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    blood_pressure = models.FloatField()
    serum_creatinine = models.FloatField()
    
    # NEW CLINICAL FIELDS
    sugar = models.FloatField(default=0.0) # Blood Glucose/HbA1c
    albumin = models.FloatField(default=0.0) # Protein in urine
    hemoglobin = models.FloatField(default=0.0) # Kidney failure causes anemia
    specific_gravity = models.FloatField(default=1.010) # Urine density
    egfr = models.FloatField(null=True, blank=True) # The "Health Score"
    
    # Existing status fields
    risk_level = models.CharField(max_length=50)
    prediction_result = models.TextField()
    doctor_feedback = models.CharField(max_length=50, null=True, blank=True)
    routing_status = models.CharField(max_length=100, default="Unassigned")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"
    
    # === NEW: AGENTIC ROUTING & LEARNING FIELDS ===
    assigned_department = models.CharField(max_length=100, default="Pending Triage")
    routing_status = models.CharField(max_length=50, default="Unassigned") 
    doctor_feedback = models.CharField(max_length=50, null=True, blank=True) # Will store "Approved" or "Overridden"

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product_name}"
    

class CustomCurePlan(models.Model):
    plan_name = models.CharField(max_length=100) # e.g., "Option 4: Specialist Manual Protocol"
    plan_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.plan_name